# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: dgi.py
# Description: DGI 模型

from torch_geometric.nn import GCNConv, global_mean_pool
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal


class Discriminator(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.bilinear = nn.Bilinear(input_dim // 2, input_dim // 2, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mid = x.size(1) // 2
        x1 = x[:, :mid]
        x2 = x[:, mid:]
        return self.bilinear(x1, x2)

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
    def __init__(self, 
            input_dim: int, 
            hidden_dim: int = 512, 
            output_dim: int = 256):
        super().__init__()
        self.encoder = GraphEncoder(input_dim, hidden_dim, output_dim)
        self.discriminator = Discriminator(output_dim * 2)
        
        self.projection_head = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, output_dim)
        )
        
        self.corruption_type: Literal['dropout', 'gaussian', 'shuffle'] = 'shuffle'
        
    def corruption(self, x: torch.Tensor) -> torch.Tensor:
        if self.corruption_type == 'dropout':  # 随机丢弃特征
            return F.dropout(x, p=0.2, training=True)
        elif self.corruption_type == 'gaussian':
            noise = torch.randn_like(x) * 0.1  # 高斯噪声
            return x + noise
        else:
            idx = torch.randperm(x.size(0)) # 打乱节点顺序
            return x[idx]
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        positive = self.encoder(x, edge_index)
        positive_proj = self.projection_head(positive)
        
        corrupted_x = self.corruption(x)
        negative = self.encoder(corrupted_x, edge_index)
        negative_proj = self.projection_head(negative)
        
        batch_vector = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
        summary = torch.tanh(global_mean_pool(positive, batch_vector))
        summary_proj = self.projection_head(summary)
        
        return positive_proj, negative_proj, summary_proj
    
    def loss(self, positive: torch.Tensor, negative: torch.Tensor, summary: torch.Tensor) -> torch.Tensor:
        summary = summary.expand(positive.size(0), -1)
        
        pos_scores = self.discriminator(torch.cat([positive, summary], dim=1))  # 局部和全局特征拼接
        neg_scores = self.discriminator(torch.cat([negative, summary], dim=1))
        
        pos_loss = F.binary_cross_entropy_with_logits(
            pos_scores.squeeze(), 
            torch.ones_like(pos_scores.squeeze())  # 取消标签平滑
        )
        neg_loss = F.binary_cross_entropy_with_logits(
            neg_scores.squeeze(), 
            torch.zeros_like(neg_scores.squeeze())
        )
        
        return pos_loss + neg_loss
