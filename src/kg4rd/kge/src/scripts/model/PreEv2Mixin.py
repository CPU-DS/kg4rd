# -*- coding: utf-8 -*-
# Create Date: 2025/10/22
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: PreEv2Mixin.py

import torch
from torch import nn
import numpy as np


def project_layer(dim: int, dropout: float) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(dim, dim * 2),
        nn.LayerNorm(dim * 2),
        nn.GELU(),  
        nn.Dropout(dropout),
        nn.Linear(dim * 2, dim * 2),
        nn.LayerNorm(dim * 2),
        nn.GELU(),
        nn.Dropout(dropout),
        nn.Linear(dim * 2, dim),
    )


class PreEv2Mixin:
    def init_pre_embeddings(
        self,
        dim: int,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dropout: float = 0.1
    ):
        self.ent_embeddings.weight.data = torch.from_numpy(  # type: ignore
            np.load(ent_embed_path)['embeddings']
        )
        self.ent_embeddings.weight.requires_grad = False  # type: ignore
        
        if rel_embed_path is not None:
            self.rel_embeddings.weight.data = torch.from_numpy(  # type: ignore
                np.load(rel_embed_path)['embeddings']
            )
            self.rel_embeddings.weight.requires_grad = False  # type: ignore
        
        self.head_projection = project_layer(dim, dropout)
        self.tail_projection = project_layer(dim, dropout)
        self.rel_projection = project_layer(dim, dropout)
        
        self.head_gate = nn.Linear(dim, dim)
        self.tail_gate = nn.Linear(dim, dim)
        self.rel_gate = nn.Linear(dim, dim)
    
    def project(
        self,
        head_emb: torch.Tensor,
        relation_emb: torch.Tensor,
        tail_emb: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        head_proj = self.head_projection(head_emb)
        head_gate = torch.sigmoid(self.head_gate(head_emb))
        head_emb = head_gate * head_proj + (1 - head_gate) * head_emb

        rel_proj = self.rel_projection(relation_emb)
        rel_gate = torch.sigmoid(self.rel_gate(relation_emb))
        relation_emb = rel_gate * rel_proj + (1 - rel_gate) * relation_emb
        
        tail_proj = self.tail_projection(tail_emb)
        tail_gate = torch.sigmoid(self.tail_gate(tail_emb))
        tail_emb = tail_gate * tail_proj + (1 - tail_gate) * tail_emb
        
        return head_emb, relation_emb, tail_emb
