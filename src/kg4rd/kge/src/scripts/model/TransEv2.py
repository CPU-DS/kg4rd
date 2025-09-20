# -*- coding: utf-8 -*-
# Create Date: 2025/09/20
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransEv2.py
# Description: TransE 改进模型

from unike.module.model import TransE
import torch
from torch import nn
from typing_extensions import override


class TransEv2(TransE):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed: torch.Tensor,
        rel_embed: torch.Tensor | None = None,
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
        
        self.ent_embeddings.weight.data = ent_embed
        self.ent_embeddings.weight.requires_grad = False
        
        if rel_embed is not None:
            self.rel_embeddings.weight.data = rel_embed
            self.rel_embeddings.weight.requires_grad = False
        
        self.ent_head = nn.Sequential(
            nn.Linear(self.dim, self.dim * 2),
            nn.ReLU(),
            nn.Linear(self.dim * 2, self.dim),
        )

        self.rel_head = nn.Sequential(
            nn.Linear(self.dim, self.dim * 2),
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
    