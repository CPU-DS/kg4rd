# -*- coding: utf-8 -*-
# Create Date: 2025/09/20
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransE_GCLv2.py
# Description: TransE 改进模型

from unike.module.model import TransE, get_transe_hpo_config
import torch
from torch import nn
from typing_extensions import override
import numpy as np
import os


def pl(dim: int, dropout: float) -> nn.Sequential:
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


class TransE_GCLv2(TransE):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dim: int = 100,
        p_norm: int = 1,
        norm_flag: bool = True,
        margin: float | None = None,
        dropout: float = 0.1
    ):
        super().__init__(
            ent_tol = ent_tol,
            rel_tol = rel_tol,
            dim = dim,
            p_norm = p_norm,
            norm_flag = norm_flag,
            margin = margin
        )
        
        self.ent_embeddings.weight.data = torch.from_numpy(np.load(ent_embed_path)['embeddings'])
        self.ent_embeddings.weight.requires_grad = False
        
        if rel_embed_path is not None:
            self.rel_embeddings.weight.data = torch.from_numpy(np.load(rel_embed_path)['embeddings'])
            self.rel_embeddings.weight.requires_grad = False

        self.head_projection = pl(self.dim, dropout)
        self.tail_projection = pl(self.dim, dropout)
        self.rel_projection = pl(self.dim, dropout)
        
        self.head_gate = nn.Linear(self.dim, self.dim)
        self.tail_gate = nn.Linear(self.dim, self.dim)
        self.rel_gate = nn.Linear(self.dim, self.dim)
    
    @override
    def tri2emb(
		self,
		triples: torch.Tensor,
		negs: torch.Tensor | None = None,
		mode: str = 'single'
    ) -> tuple:
        head_emb, relation_emb, tail_emb = super().tri2emb(triples, negs, mode)  # type: ignore
        
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

def get_hpo_config() -> dict:
	parameters_dict = {
        **get_transe_hpo_config(),
        'model': {
            'value': 'TransE_GCLv2'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'TransE_GCLv2.TransE_GCLv2'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
