# -*- coding: utf-8 -*-
# Create Date: 2025/11/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: RESCAL_PreEv2.py
# Description: RESCAL 改进模型

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unike.module.model import RESCAL, get_rescal_hpo_config
import torch
from typing_extensions import override
from PreEv2Mixin import PreEv2Mixin


class RESCAL_PreEv2(RESCAL, PreEv2Mixin):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed_path: str,
        dim: int = 100,
        dropout: float = 0.1
    ): 
        super().__init__(
            ent_tol = ent_tol,
            rel_tol = rel_tol,
            dim = dim
        )
        
        self.prepare_ent_embeddings(ent_embed_path)
        self.init_ent_project_layers(dim, dropout)
        
    @override
    def tri2emb(
		self,
		triples: torch.Tensor,
		negs: torch.Tensor | None = None,
		mode: str = 'single'
    ) -> tuple:
        head_emb, tail_emb = super().tri2emb(triples, negs, mode)  # type: ignore
        return self.head_project(head_emb), self.tail_project(tail_emb)


def get_hpo_config() -> dict:
	parameters_dict = {
        **get_rescal_hpo_config(),
        'model': {
            'value': 'RESCAL_PreEv2'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'RESCAL_PreEv2.RESCAL_PreEv2'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
