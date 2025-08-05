# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gcl.py
# Description: 图节点嵌入融合与图对比学习

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from embedding_loader import NodeEmbeddingLoader
from embedding_fusion import EmbeddingFusion
from dgi import DGI

import numpy as np
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import wandb


class GCL:
    def __init__(self, 
                 nodes_path: str = 'src/kg4rd/kg/nodes.csv',
                 edges_path: str = 'src/kg4rd/kg/edges.csv',
                 target_dim: int = 512,
                 device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.nodes_path = nodes_path
        self.edges_path = edges_path
        
        self.target_dim = target_dim
        self.device = device

        self.fusion_model = EmbeddingFusion(target_dim)
        self.dgi_model = DGI(target_dim)
        
    def load_graph_data(self):
        self.nodes = pd.read_csv(self.nodes_path, low_memory=False).astype({'node_index': str}).astype({'node_index': int})
        self.node_indices = self.nodes['node_index'].tolist()
        
        edges = pd.read_csv(self.edges_path, low_memory=False)
        
        self.edge_index = torch.from_numpy(  # (2, num_edges) COO 格式 head -> tail
            np.stack([
                edges['x_index'].to_numpy(dtype=np.int64),
                edges['y_index'].to_numpy(dtype=np.int64)
            ])
        )
        
    def prepare_embeddings(self):
        embedding_loader = NodeEmbeddingLoader()
        self.adv_embeddings = embedding_loader.load_node_embeddings(self.nodes, self.device)
        
    def prepare_fusion_model(self):
        type_dims = {}  # 嵌入类型及维度

        for node_embeddings in self.adv_embeddings.values():  # need improve
            for embed_type, embedding in node_embeddings.items():
                if embed_type not in type_dims:
                    type_dims[embed_type] = embedding.shape[0]

        for embed_type, dim in type_dims.items():
            self.fusion_model.add_embedding_type(embed_type, dim)   
        
    def get_fused_embeddings(self, node_indices):
        embeddings = []
        
        for node_idx in node_indices:
            if node_idx in self.adv_embeddings and self.adv_embeddings[node_idx]:
                fused = self.fusion_model(self.adv_embeddings[node_idx])
                embeddings.append(fused)
            else:  
                embeddings.append(torch.randn(self.target_dim, device=self.device) * 0.1)

        return torch.stack(embeddings)
        
    def train(self, epochs: int = 100, lr: float = 0.001, batch_size: int = 1024, log_epoch: int = 1, save_epoch: int = 20):

        optimizer = torch.optim.Adam(
            list(self.fusion_model.parameters()) + list(self.dgi_model.parameters()), 
            lr=lr
        )
        
        scheduler = CosineAnnealingLR(
            optimizer, 
            T_max=epochs,
            eta_min=1e-6
        )
        
        self.fusion_model.to(self.device)
        self.dgi_model.to(self.device)
        
        self.fusion_model.train()
        self.dgi_model.train()

        for epoch in range(epochs):
            
            fused_embeddings = self.get_fused_embeddings(self.node_indices)  # (num_nodes, target_dim)    0 -> num_nodes-1
            data = Data(
                x = fused_embeddings,
                edge_index = self.edge_index
            )
            
            train_loader = NeighborLoader(
                data,
                num_neighbors=[10, 10],
                batch_size=batch_size,
            )
            
            total_loss = 0
            for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
                batch = batch.to(self.device)
                optimizer.zero_grad()

                positive, negative, summary = self.dgi_model(batch.x, batch.edge_index)
                loss = self.dgi_model.loss(positive, negative, summary)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()

            scheduler.step()
            current_lr = scheduler.get_last_lr()[0]
            
            if (epoch + 1) % log_epoch == 0:
                wandb.log({
                    "epoch": epoch + 1,
                    "loss": total_loss,
                    "learning_rate": current_lr
                })
                
            if (epoch + 1) % save_epoch == 0:
                torch.save(self.dgi_model.state_dict(), f'src/kg4rd/gcl/checkpoints/dgi_model_{epoch+1}.pth')
                torch.save(self.fusion_model.state_dict(), f'src/kg4rd/gcl/checkpoints/fusion_model_{epoch+1}.pth')
        
    def get_embeddings(self) -> torch.Tensor:
        self.dgi_model.to(self.device)
        self.fusion_model.to(self.device)            
        
        self.dgi_model.eval()
        self.fusion_model.eval()
        
        with torch.no_grad():
            fused_embeddings = self.get_fused_embeddings(self.node_indices)
            embeddings = self.dgi_model.encoder(fused_embeddings, self.edge_index)
            return embeddings
    
    def save_embeddings(self, save_path: str):
        embeddings = self.get_embeddings()
        np.savez_compressed(save_path, 
                            node_indices=np.arange(len(self.node_indices)),
                            embeddings=embeddings.cpu().numpy())

if __name__ == "__main__":
    wandb.init(project="kg4rd", name="gcl", config={
        "target_dim": 512,
        "device": "cuda:3",
        "batch_size": 1024,
        "epochs": 1000,
        "lr": 0.001,
        "log_epoch": 1
    })
    config = wandb.config
    
    
    gcl = GCL(
        target_dim=config.target_dim,
        device=config.device
    )

    gcl.load_graph_data()
    gcl.prepare_embeddings()
    
    gcl.prepare_fusion_model()
    gcl.train(
        epochs=config.epochs,
        lr=config.lr,
        batch_size=config.batch_size,
        log_epoch=config.log_epoch
    )
    
    # gcl.save_embeddings('data/data_feature/node_embeddings.npz')
