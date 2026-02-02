# -*- coding: utf-8 -*-
# Create Date: 2026/02/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: CompGCN_PreE.py
# Description: CompGCN 改进模型, 使用 GCL 训练得到节点预嵌入

from unike.module.model import CompGCN, get_compgcn_hpo_config
import torch
import numpy as np
import os


class CompGCN_PreE(CompGCN):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dim: int = 100,
        opn: str = 'mult',
        fet_drop: float = 0.2,
        hid_drop: float = 0.3
    ):
        super().__init__(
            ent_tol = ent_tol,
            rel_tol = rel_tol,
            dim = dim,
            opn = opn,
            fet_drop = fet_drop,
            hid_drop = hid_drop
        )
        
        self.ent_embeddings.weight.data = torch.from_numpy(np.load(ent_embed_path)['embeddings'])
        self.ent_embeddings.weight.requires_grad = False
        
        if rel_embed_path is not None:
            self.rel_embeddings.weight.data = torch.from_numpy(np.load(rel_embed_path)['embeddings'])
            self.rel_embeddings.weight.requires_grad = False

def get_hpo_config() -> dict:
	parameters_dict = {
        **get_compgcn_hpo_config(),
        'model': {
            'value': 'CompGCN_PreE'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'CompGCN_PreE.CompGCN_PreE'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
