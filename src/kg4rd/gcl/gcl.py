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
        
    def load_pre_embeddings(self):
        embedding_loader = NodeEmbeddingLoader()
        self.pre_embeddings, self.type_dims = embedding_loader.load_node_embeddings(self.nodes, self.device)
        
    def init_fusion_model(self):
        for embed_type, dim in self.type_dims.items():
            self.fusion_model.add_embedding_type(embed_type, dim)
        
    def get_fused_embeddings(self, node_indices):
        embeddings = []
        
        for node_idx in node_indices:
            if node_idx in self.pre_embeddings and self.pre_embeddings[node_idx]:
                fused = self.fusion_model(self.pre_embeddings[node_idx])
                embeddings.append(fused)
            else:
                embeddings.append(torch.randn(self.target_dim, device=self.device, requires_grad=True) * 0.1)

        return torch.stack(embeddings)
        
    def train(self, 
              epochs: int = 100, 
              lr: float = 0.001, 
              batch_size: int = 1024, 
              log_epoch: int = 1,
              save_epoch: int = 20,
              num_neighbors: list[int] = [10, 10],
              save_dir: str = 'src/kg4rd/gcl/checkpoints'):

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
            
            data = Data(
                x = torch.zeros((len(self.node_indices), self.target_dim)),
                edge_index = self.edge_index
            )
            
            train_loader = NeighborLoader(
                data,
                num_neighbors=num_neighbors,
                batch_size=batch_size,
            )
            
            total_loss = 0
            for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
                batch = batch.to(self.device)
                optimizer.zero_grad()
                
                batch.x = self.get_fused_embeddings(batch.n_id.cpu().numpy())  # 原来是全 0
                
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
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                torch.save(self.dgi_model.state_dict(), os.path.join(save_dir, f'dgi_model_{epoch+1}.pth'))
                torch.save(self.fusion_model.state_dict(), os.path.join(save_dir, f'fusion_model_{epoch+1}.pth'))
        
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
        "device": "cuda:0",
        "batch_size": 128,
        "epochs": 5000,
        "lr": 0.001,
        "log_epoch": 1,
        "save_epoch": 500,
        "num_neighbors": [10, 10]
    })
    config = wandb.config
    
    
    gcl = GCL(
        target_dim=config.target_dim,
        device=config.device
    )

    gcl.load_graph_data()
    gcl.load_pre_embeddings()
    
    gcl.init_fusion_model()
    gcl.train(
        epochs=config.epochs,
        lr=config.lr,
        batch_size=config.batch_size,
        log_epoch=config.log_epoch,
        save_epoch=config.save_epoch
    )

    wandb.finish()
