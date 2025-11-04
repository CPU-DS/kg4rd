# -*- coding: utf-8 -*-
# Create Date: 2025/11/02
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransH_PreEv2.py
# Description: TransH 改进模型

import os
import sys
from pathlib import Path as path
sys.path.append(str(path(__file__).parent.parent))

from unike.module.model import TransH, get_transh_hpo_config
import torch
from typing_extensions import override
from PreEv2Mixin import PreEv2Mixin


class TransH_PreEv2(TransH, PreEv2Mixin):
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

        self.prepare_ent_embeddings(ent_embed_path)
        if rel_embed_path is not None:
            self.prepare_rel_embeddings(rel_embed_path)
        self.init_ent_project_layers(dim, dropout)
        self.init_rel_project_layers(dim, dropout)

    @override
    def tri2emb(
		self,
		triples: torch.Tensor,
		negs: torch.Tensor | None = None,
		mode: str = 'single'
    ) -> tuple:
        head_emb, relation_emb, tail_emb = super().tri2emb(triples, negs, mode)  # type: ignore
        return self.project(head_emb, relation_emb, tail_emb)


def get_hpo_config() -> dict:
	parameters_dict = {
        **get_transh_hpo_config(),
        'model': {
            'value': 'TransH_PreEv2'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'TransH_PreEv2.TransH_PreEv2'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict




        
