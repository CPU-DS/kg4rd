# -*- coding: utf-8 -*-
# Create Date: 2025/09/20
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransE_GCL.py
# Description: TransE 改进模型, 使用 GCL 训练得到节点预嵌入

from unike.module.model import TransE, get_transe_hpo_config
import torch
import os
import numpy as np


class TransE_GCL(TransE):
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
        
        if rel_embed_path is not None:
            self.rel_embeddings.weight.data = torch.from_numpy(np.load(rel_embed_path)['embeddings'])


def get_hpo_config() -> dict:
	parameters_dict = {
        **get_transe_hpo_config(),
        'model': {
            'value': 'TransE_GCL'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'TransE_GCL.TransE_GCL'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
