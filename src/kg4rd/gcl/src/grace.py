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
            edge_drop_rate: float = 0.2,
            feat_drop_rate: float = 0.2):
        super().__init__()
        hidden_dim = input_dim * 2
        output_dim = input_dim
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
        self.temperature: float = 0.2
        
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
    
    def nt_xent_loss(self, z1: torch.Tensor, z2: torch.Tensor, temperature: float = 0.2) -> torch.Tensor:
        batch_size = z1.size(0)

        z1 = F.normalize(z1, dim=1)
        z2 = F.normalize(z2, dim=1)

        sim_11 = torch.mm(z1, z1.t()) / temperature
        sim_22 = torch.mm(z2, z2.t()) / temperature
        sim_12 = torch.mm(z1, z2.t()) / temperature
        sim_21 = torch.mm(z2, z1.t()) / temperature
        
        # 对角线是正样本
        mask = torch.eye(batch_size, device=z1.device).bool()
        
        # z1->z2的损失
        pos_12 = torch.diag(sim_12)
        neg_sim_1 = torch.cat([sim_11.masked_fill(mask, -float('inf')), 
                               sim_12.masked_fill(mask, -float('inf'))], dim=1)
        neg_1 = torch.logsumexp(neg_sim_1, dim=1)
        loss_1 = -pos_12 + neg_1
        
        # z2->z1的损失
        pos_21 = torch.diag(sim_21)
        neg_sim_2 = torch.cat([sim_22.masked_fill(mask, -float('inf')), 
                               sim_21.masked_fill(mask, -float('inf'))], dim=1)
        neg_2 = torch.logsumexp(neg_sim_2, dim=1)
        loss_2 = -pos_21 + neg_2

        loss = (loss_1 + loss_2) / 2.0
        
        return loss.mean()
    
    def loss(self, z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        # NT-Xent对比损失（内部已包含双向对称损失）
        return self.nt_xent_loss(z1, z2, temperature=self.temperature)
