# -*- coding: utf-8 -*-
# Create Date: 2025/10/07
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: grace.py
# Description: GRACE 模型

from torch_geometric.nn import GCNConv
from torch_geometric.utils import dropout_edge
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal


class GraphEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512, output_dim: int = 256):
        super().__init__()
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        return x


class GRACE(nn.Module):
    def __init__(self, 
            input_dim: int, 
            hidden_dim: int = 512, 
            output_dim: int = 256,
            edge_drop_rate: float = 0.2,
            feat_drop_rate: float = 0.2):
        super().__init__()
        self.encoder = GraphEncoder(input_dim, hidden_dim, output_dim)
        
        self.projection_head = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(output_dim, output_dim)
        )
        
        self.edge_drop_rate = edge_drop_rate
        self.feat_drop_rate = feat_drop_rate
        
        self.augmentation_type: Literal['edge', 'feature', 'mixed'] = 'mixed'
        
    def augment_graph(self, 
                      x: torch.Tensor, 
                      edge_index: torch.Tensor, 
                      use_edge_drop: bool = True, 
                      use_feat_drop: bool = True
        ) -> tuple[torch.Tensor, torch.Tensor]:
        aug_x = x
        aug_edge_index = edge_index
        
        if use_edge_drop and self.training:
            aug_edge_index, _ = dropout_edge(  # 边丢弃
                edge_index, 
                p=self.edge_drop_rate,
                force_undirected=False,
                training=True
            )
        
        if use_feat_drop and self.training:
            feat_mask = torch.bernoulli(
                torch.ones_like(x) * (1 - self.feat_drop_rate)  # 特征丢弃, 随机 mask 部分特征
            )
            aug_x = x * feat_mask
        
        return aug_x, aug_edge_index
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        match self.augmentation_type:
            case 'edge':
                x1, edge_index1 = self.augment_graph(x, edge_index, use_edge_drop=True, use_feat_drop=False)
                x2, edge_index2 = self.augment_graph(x, edge_index, use_edge_drop=True, use_feat_drop=False)
            case 'feature':
                x1, edge_index1 = self.augment_graph(x, edge_index, use_edge_drop=False, use_feat_drop=True)
                x2, edge_index2 = self.augment_graph(x, edge_index, use_edge_drop=False, use_feat_drop=True)
            case _:  # mixed
                x1, edge_index1 = self.augment_graph(x, edge_index, use_edge_drop=True, use_feat_drop=True)
                x2, edge_index2 = self.augment_graph(x, edge_index, use_edge_drop=True, use_feat_drop=True)  # 独立采样
        
        h1 = self.encoder(x1, edge_index1)
        h2 = self.encoder(x2, edge_index2)
        
        z1 = self.projection_head(h1)
        z2 = self.projection_head(h2)
        
        return z1, z2
    
    def nt_xent_loss(self, z1: torch.Tensor, z2: torch.Tensor, temperature: float = 0.5) -> torch.Tensor:
        # NT-Xent (Normalized Temperature-scaled Cross Entropy) (InfoNCE)
        batch_size = z1.size(0)
        
        z1 = F.normalize(z1, dim=1)
        z2 = F.normalize(z2, dim=1)

        z = torch.cat([z1, z2], dim=0)  # (2*batch_size, dim)
        
        sim_matrix = torch.mm(z, z.t()) / temperature  # 相似度矩阵 (2*batch_size, 2*batch_size)
        
        pos_mask = torch.zeros(2 * batch_size, 2 * batch_size, device=z.device)  # 正样本 mask, 对于每个样本i，它的正样本是另一个视图中的相同节点
        for i in range(batch_size):
            pos_mask[i, batch_size + i] = 1
            pos_mask[batch_size + i, i] = 1
        
        neg_mask = torch.ones_like(sim_matrix) - torch.eye(2 * batch_size, device=z.device) - pos_mask  # 负样本 mask, 排除本身和正样本
        
        exp_sim = torch.exp(sim_matrix)  # 指数相似度
        pos_sim = (exp_sim * pos_mask).sum(dim=1)  # 正样本的相似度之和
        neg_sim = (exp_sim * neg_mask).sum(dim=1)  # 负样本的相似度之和

        loss = -torch.log(pos_sim / (pos_sim + neg_sim + 1e-8))
        
        return loss.mean()
    
    def loss(self, z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        # 双向对比损失
        loss1 = self.nt_xent_loss(z1, z2, temperature=0.5)
        loss2 = self.nt_xent_loss(z2, z1, temperature=0.5)
        
        return (loss1 + loss2) / 2


