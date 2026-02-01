# -*- coding: utf-8 -*-
# Create Date: 2025/11/02
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: RotatE_PreEv2.py
# Description: RotatE 改进模型

import os
import sys
from pathlib import Path as path
sys.path.append(str(path(__file__).parent.parent))

from unike.module.model import RotatE, get_rotate_hpo_config
import torch
from typing_extensions import override
from PreEv2Mixin import PreEv2Mixin


class RotatE_PreEv2(RotatE, PreEv2Mixin):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dim: int = 100,
        margin: float = 6.0,
        epsilon: float = 2.0,
        dropout: float = 0.1
    ):
        RotatE.__init__(
            self,
            ent_tol = ent_tol,
            rel_tol = rel_tol,
            dim = dim,
            margin = margin,
            epsilon = epsilon
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
        **get_rotate_hpo_config(),
        'model': {
            'value': 'RotatE_PreEv2'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'RotatE_PreEv2.RotatE_PreEv2'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
