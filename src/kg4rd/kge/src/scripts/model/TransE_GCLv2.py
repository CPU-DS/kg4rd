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
        margin: float | None = None
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
        
        self.ent_head = nn.Sequential(
            nn.Linear(self.dim, self.dim * 2),
            nn.ReLU(),
            nn.Linear(self.dim * 2, self.dim * 2),
            nn.ReLU(),
            nn.Linear(self.dim * 2, self.dim),
        )
        
        self.rel_head = nn.Sequential(
            nn.Linear(self.dim, self.dim * 2),
            nn.ReLU(),
            nn.Linear(self.dim * 2, self.dim * 2),
            nn.ReLU(),
            nn.Linear(self.dim * 2, self.dim),
        )
    
    @override
    def tri2emb(
		self,
		triples: torch.Tensor,
		negs: torch.Tensor | None = None,
		mode: str = 'single'
    ) -> tuple:
        head_emb, relation_emb, tail_emb = super().tri2emb(triples, negs, mode)  # type: ignore
        head_emb = self.ent_head(head_emb)
        relation_emb = self.rel_head(relation_emb)
        tail_emb = self.ent_head(tail_emb)
            
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
