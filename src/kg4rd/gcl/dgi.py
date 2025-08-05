# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: dgi.py
# Description: DGI 模型

from torch_geometric.nn import GCNConv, global_mean_pool
import torch
import torch.nn as nn
import torch.nn.functional as F


class Discriminator(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

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

class DGI(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512, output_dim: int = 256):
        super().__init__()
        self.encoder = GraphEncoder(input_dim, hidden_dim, output_dim)
        self.discriminator = Discriminator(output_dim)
        
    def corruption(self, x: torch.Tensor) -> torch.Tensor:
        idx = torch.randperm(x.size(0))  # 生成负样本，随机打乱节点特征
        return x[idx]
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        positive = self.encoder(x, edge_index)
        
        corrupted_x = self.corruption(x)
        negative = self.encoder(corrupted_x, edge_index)
        
        positive = positive.detach().requires_grad_(True)
        negative = negative.detach().requires_grad_(True)
        
        summary = torch.sigmoid(global_mean_pool(positive, torch.zeros(x.size(0), dtype=torch.long, device=x.device)))
        
        return positive, negative, summary
    
    def loss(self, positive: torch.Tensor, negative: torch.Tensor, summary: torch.Tensor) -> torch.Tensor:
        pos_scores = self.discriminator(positive + summary) 
        neg_scores = self.discriminator(negative + summary)
        
        pos_loss = F.binary_cross_entropy(pos_scores, torch.ones_like(pos_scores))
        neg_loss = F.binary_cross_entropy(neg_scores, torch.zeros_like(neg_scores))
        
        return pos_loss + neg_loss
