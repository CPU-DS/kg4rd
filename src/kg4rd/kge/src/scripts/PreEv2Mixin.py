# -*- coding: utf-8 -*-
# Create Date: 2025/10/22
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: PreEv2Mixin.py

import torch
from torch import nn
from torch.nn import functional as F
import numpy as np


def project_layer(dim: int, dropout: float) -> nn.Sequential:
    layers = nn.Sequential(
        nn.Linear(dim, dim * 4),
        nn.LayerNorm(dim * 4),
        nn.GELU(),  
        nn.Dropout(dropout),
        nn.Linear(dim * 4, dim),
    )
    return layers


class PreEv2Mixin:
    
    def prepare_ent_embeddings(
        self,
        ent_embed_path: str
    ):
        self.ent_embeddings.weight.data = torch.from_numpy(  # type: ignore
            np.load(ent_embed_path)['embeddings']
        )
        self.ent_embeddings.weight.requires_grad = False  # type: ignore
        
    def prepare_rel_embeddings(
        self,
        rel_embed_path: str
    ):
        self.rel_embeddings.weight.data = torch.from_numpy(  # type: ignore
            np.load(rel_embed_path)['embeddings']
        )
        self.rel_embeddings.weight.requires_grad = False  # type: ignore
        
    def init_ent_project_layers(
        self,
        dim: int,
        dropout: float = 0.1
    ):
        self.head_projection = project_layer(dim, dropout)
        self.head_gate = nn.Linear(dim, dim)
        self.tail_projection = project_layer(dim, dropout)
        self.tail_gate = nn.Linear(dim, dim)

    def init_rel_project_layers(
        self,
        dim: int,
        dropout: float = 0.1
    ):
        self.rel_projection = project_layer(dim, dropout)
        self.rel_gate = nn.Linear(dim, dim)
        
    def head_project(
        self,
        head_emb: torch.Tensor
    ) -> torch.Tensor:
        head_proj = self.head_projection(head_emb)
        head_proj = F.normalize(head_proj, p=2, dim=-1) * head_emb.norm(p=2, dim=-1, keepdim=True)
        head_gate = torch.sigmoid(self.head_gate(head_emb))
        head_emb = head_gate * head_proj + (1 - head_gate) * head_emb
        return head_emb
    
    def tail_project(
        self,
        tail_emb: torch.Tensor
    ) -> torch.Tensor:
        tail_proj = self.tail_projection(tail_emb)
        tail_gate = torch.sigmoid(self.tail_gate(tail_emb))
        tail_proj = F.normalize(tail_proj, p=2, dim=-1) * tail_emb.norm(p=2, dim=-1, keepdim=True)
        tail_emb = tail_gate * tail_proj + (1 - tail_gate) * tail_emb
        return tail_emb
    
    def rel_project(
        self,
        relation_emb: torch.Tensor
    ) -> torch.Tensor:
        rel_proj = self.rel_projection(relation_emb)
        rel_proj = F.normalize(rel_proj, p=2, dim=-1) * relation_emb.norm(p=2, dim=-1, keepdim=True)
        rel_gate = torch.sigmoid(self.rel_gate(relation_emb))
        relation_emb = rel_gate * rel_proj + (1 - rel_gate) * relation_emb
        return relation_emb
    
    def project(
        self,
        head_emb: torch.Tensor,
        relation_emb: torch.Tensor,
        tail_emb: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
                
        return self.head_project(head_emb), self.rel_project(relation_emb), self.tail_project(tail_emb)
