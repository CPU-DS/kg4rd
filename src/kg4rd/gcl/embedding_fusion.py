# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: embedding_fusion.py
# Description: 多嵌入融合

import torch
from torch import nn
from typing import Optional
from torch.nn import functional as F


class EmbeddingFusion(nn.Module):
    def __init__(self, target_dim: int = 512):
        super().__init__()
        self.target_dim = target_dim
        self.projectors = nn.ModuleDict()
        
    def add_embedding_type(self, name: str, input_dim: int):
        self.projectors[name] = nn.Sequential(  # 通过线性层投影到目标维度
            nn.Linear(input_dim, self.target_dim),
            nn.LayerNorm(self.target_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(self.target_dim, self.target_dim)
        )
        
    def forward(self, embeddings_dict: dict[str, torch.Tensor]) -> Optional[torch.Tensor]:
        projected_embeddings = []
        for name, embedding in embeddings_dict.items():
            if name in self.projectors:
                projected = self.projectors[name](embedding)
                projected_embeddings.append(projected)
        
        if len(projected_embeddings) == 0:
            return None
        elif len(projected_embeddings) == 1:
            return projected_embeddings[0]
        else:  # 使用注意力加权
            stacked = torch.stack(projected_embeddings, dim=0)  # (num_embeddings, dim)
            attention_scores = torch.matmul(stacked, stacked.transpose(0, 1))
            attention_weights = F.softmax(attention_scores.mean(dim=1), dim=0)
            weighted = torch.sum(stacked * attention_weights.unsqueeze(-1), dim=0)
            return weighted
