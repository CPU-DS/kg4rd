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
from ggd import GGD
from grace import GRACE

import numpy as np
import torch
import torch.nn as nn
from torch.nn.utils.clip_grad import clip_grad_norm_
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
import pandas as pd
from tqdm import tqdm
import swanlab
import pytorch_warmup as warmup
import yaml
import argparse
import time
from typing import Literal


class GCL:
    def __init__(self, 
                 nodes_path: str = 'src/kg4rd/kg/nodes.csv',
                 edges_path: str = 'src/kg4rd/kg/edges.csv',
                 target_dim: int = 200,
                 model_type: Literal['dgi', 'ggd', 'grace'] = 'dgi',
                 device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.nodes_path = nodes_path
        self.edges_path = edges_path
        
        self.target_dim = target_dim
        self.device = device

        self.fusion_model = EmbeddingFusion(target_dim)
        
        self.model_type = model_type
        match model_type:
            case 'ggd':
                self.gcl_model = GGD(target_dim)
            case 'grace':
                self.gcl_model = GRACE(target_dim)
            case _:  #  dgi
                self.gcl_model = DGI(target_dim)
        
        self.embedding_norm = nn.LayerNorm(target_dim, device=device)
        
        self._load_graph_data()
        self._load_pre_embeddings()
    
        self._init_fusion_model()        
        self._init_node_embeddings()  # 从 pre_embeddings 到 learnable_embeddings
        
    def _load_graph_data(self):
        self.nodes = pd.read_csv(self.nodes_path, low_memory=False).astype({'node_index': str}).astype({'node_index': int})
        self.node_indices = self.nodes['node_index'].tolist()
        
        edges = pd.read_csv(self.edges_path, low_memory=False)
        
        self.edge_index = torch.from_numpy(  # (2, num_edges) COO 格式 head -> tail
            np.stack([
                edges['x_index'].to_numpy(dtype=np.int64),
                edges['y_index'].to_numpy(dtype=np.int64)
            ])
        )
        
    def _load_pre_embeddings(self):
        embedding_loader = NodeEmbeddingLoader()
        self.pre_embeddings, self.type_dims = embedding_loader.load_node_embeddings(self.nodes, self.device)
        
    def _init_fusion_model(self):
        for embed_type, dim in self.type_dims.items():
            self.fusion_model.add_embedding_type(embed_type, dim)
    
    def _init_node_embeddings(self):
        num_nodes = len(self.node_indices)
        
        self.learnable_embeddings = nn.Parameter(
            torch.zeros(num_nodes, self.target_dim, device=self.device)
        )
        nn.init.xavier_normal_(self.learnable_embeddings)
        
        self.has_pretrained = torch.zeros(num_nodes, dtype=torch.bool, device=self.device)  # mask
        for node_idx in self.node_indices:  # 可以确保 self.node_indices 是连续的 
            if node_idx in self.pre_embeddings and self.pre_embeddings[node_idx]:
                self.has_pretrained[node_idx] = True
        
    def get_node_embeddings(self, node_indices):
        indices_tensor = torch.tensor(node_indices, device=self.device)
        batch_has_pretrained = self.has_pretrained[indices_tensor]
    
        batch_embeddings = torch.zeros(len(node_indices), self.target_dim, device=self.device)
        
        pretrained_mask = batch_has_pretrained
        if pretrained_mask.any():
            pretrained_indices = indices_tensor[pretrained_mask]
            pretrained_node_indices = [self.node_indices[int(idx)] for idx in pretrained_indices]
            
            fused_embeddings = []
            for node_idx in pretrained_node_indices:
                fused = self.fusion_model(self.pre_embeddings[node_idx])
                fused = self.embedding_norm(fused)
                fused_embeddings.append(fused)
            
            if fused_embeddings:
                batch_embeddings[pretrained_mask] = torch.stack(fused_embeddings)
        
        learnable_mask = ~batch_has_pretrained
        if learnable_mask.any():
            learnable_indices = indices_tensor[learnable_mask]
            learnable_emb = self.embedding_norm(self.learnable_embeddings[learnable_indices])
            batch_embeddings[learnable_mask] = learnable_emb
        
        return batch_embeddings
        
    def train(self, 
              epochs: int = 100, 
              lr: float = 0.001, 
              batch_size: int = 1024,
              save_epoch: int = 20,
              warmup_period: float = 0.1,
              num_neighbors: list[int] = [10, 10],
              save_dir: str = 'src/kg4rd/gcl/checkpoints'):

        lr_s = lr * 0.5
        optimizer = torch.optim.Adam([
            {'params': self.fusion_model.parameters(), 'lr': lr},
            {'params': self.gcl_model.parameters(), 'lr': lr},
            {'params': self.embedding_norm.parameters(), 'lr': lr},
            {'params': [self.learnable_embeddings], 'lr': lr_s}
        ])
        
        scheduler = CosineAnnealingLR(
            optimizer, 
            T_max=epochs,
            eta_min=1e-6
        )
        
        warmup_steps = int(epochs * warmup_period)
        warmup_scheduler = warmup.LinearWarmup(
            optimizer,
            warmup_period=warmup_steps
        )
        
        self.fusion_model.to(self.device)
        self.gcl_model.to(self.device)
        self.embedding_norm.to(self.device)
        
        self.fusion_model.train()
        self.gcl_model.train()
        self.embedding_norm.train()

        data = Data(
            x = torch.zeros((len(self.node_indices), self.target_dim)),
            edge_index = self.edge_index
        )
        
        start_time = time.time()
        for epoch in range(epochs):
            
            train_loader = NeighborLoader(
                data,
                num_neighbors=[min(50, num_neighbors[0]), min(50, num_neighbors[1])],
                batch_size=batch_size,
                shuffle=True
            )
            
            total_loss = 0
            for batch in (phar := tqdm(train_loader)):
                batch = batch.to(self.device)
                optimizer.zero_grad()
                
                batch.x = self.get_node_embeddings(batch.n_id.cpu().numpy())
                
                if isinstance(self.gcl_model, DGI):
                    positive, negative, summary = self.gcl_model(batch.x, batch.edge_index)
                    loss = self.gcl_model.loss(positive, negative, summary)
                elif isinstance(self.gcl_model, GGD):
                    real_proj, fake_proj, real_repr = self.gcl_model(batch.x, batch.edge_index)
                    loss = self.gcl_model.loss(real_proj, fake_proj, real_repr)
                else:  # GRACE
                    z1, z2 = self.gcl_model(batch.x, batch.edge_index)
                    loss = self.gcl_model.loss(z1, z2)
                
                loss.backward()
                
                clip_grad_norm_([
                    *self.fusion_model.parameters(),
                    *self.gcl_model.parameters(), 
                    *self.embedding_norm.parameters(),
                    self.learnable_embeddings
                ], max_norm=1.0)
                
                optimizer.step()
                
                total_loss += loss.item()
                
                phar.set_description(desc=f"Epoch {epoch+1}/{epochs}, time={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}, loss={total_loss:.3f}")

            with warmup_scheduler.dampening():
                scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            swanlab.log({
                "epoch": epoch + 1,
                "loss": total_loss,
                "lr": current_lr
            })
            
            if (epoch + 1) % save_epoch == 0:
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                    
                torch.save(self.gcl_model.state_dict(), os.path.join(save_dir, f'{self.model_type}_model_{epoch+1}.pth'))
                torch.save(self.fusion_model.state_dict(), os.path.join(save_dir, f'fusion_model_{epoch+1}.pth'))
                torch.save(self.learnable_embeddings, os.path.join(save_dir, f'learnable_embeddings_{epoch+1}.pth'))
                torch.save(self.embedding_norm.state_dict(), os.path.join(save_dir, f'embedding_norm_{epoch+1}.pth'))

        swanlab.log({
            "duration": time.time() - start_time
        })
        
    def get_embeddings(self) -> torch.Tensor:
        self.gcl_model.to(self.device)
        self.fusion_model.to(self.device)
        self.embedding_norm.to(self.device)
        
        self.gcl_model.eval()
        self.fusion_model.eval()
        self.embedding_norm.eval()
        
        self.edge_index = self.edge_index.to(self.device)
        with torch.no_grad():
            embeddings = self.get_node_embeddings(self.node_indices)
            embeddings = self.gcl_model.encoder(embeddings, self.edge_index)
            return embeddings
    
    def save_embeddings(self, save_path: str):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        embeddings = self.get_embeddings()
        np.savez_compressed(os.path.join(save_path, 'ent_embed.npz'), 
                            node_indices=np.arange(len(self.node_indices)),
                            embeddings=embeddings.cpu().numpy())


def train(args):
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
     
    swanlab.init(project=config['project'], name=config['name'], config=config, mode=args.swanlab)
    
    gcl = GCL(
        target_dim=config['target_dim'],
        model_type=config.get('model_type', 'dgi'),
        device=config['device']
    )
    
    if isinstance(gcl.gcl_model, DGI):
        gcl.gcl_model.corruption_type = config.get('corruption_type', 'shuffle')
    elif isinstance(gcl.gcl_model, GGD):
        gcl.gcl_model.generation_type = config.get('generation_type', 'transform')
    elif isinstance(gcl.gcl_model, GRACE):
        gcl.gcl_model.augmentation_type = config.get('augmentation_type', 'mixed')
    
    gcl.train(
        epochs=config['epochs'],
        lr=float(config['lr']),
        batch_size=config['batch_size'],
        save_epoch=config['save_epoch'],
        num_neighbors=config['num_neighbors'],
        warmup_period=config['warmup_period'],
        save_dir=config['checkpoints_dir']
    )

    swanlab.finish()
    
def save(args):  
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    model_type = config.get('model_type', 'dgi')
        
    gcl = GCL(
        target_dim=config['target_dim'],
        model_type=model_type,
        device=config['device']
    )

    gcl.gcl_model.load_state_dict(
        torch.load(os.path.join(config['checkpoints_dir'], f'{model_type}_model_{args.epoch}.pth'))
    )
    gcl.fusion_model.load_state_dict(
        torch.load(os.path.join(config['checkpoints_dir'], f'fusion_model_{args.epoch}.pth'))
    )
    gcl.learnable_embeddings = torch.load(os.path.join(config['checkpoints_dir'], f'learnable_embeddings_{args.epoch}.pth'))
    gcl.embedding_norm.load_state_dict(
        torch.load(os.path.join(config['checkpoints_dir'], f'embedding_norm_{args.epoch}.pth'))
    )
    
    gcl.save_embeddings(config['embeddings_dir'])


def main():
    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(dest='mode')
    subparsers.required = True
    
    train_parser = subparsers.add_parser('train')
    train_parser.add_argument('--config', type=str)
    train_parser.add_argument('--swanlab', type=str, default='cloud', choices=["disabled", "cloud", "local", "offline"])
    train_parser.set_defaults(func=train)
    
    save_parser = subparsers.add_parser('save')
    save_parser.add_argument('--config', type=str)
    save_parser.add_argument('--epoch', type=int)
    save_parser.set_defaults(func=save)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
