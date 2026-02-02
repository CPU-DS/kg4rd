# -*- coding: utf-8 -*-
# Create Date: 2026/02/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: RGCN_PreE.py
# Description: RGCN 改进模型, 使用 GCL 训练得到节点预嵌入

from unike.module.model import RGCN, get_rgcn_hpo_config
import torch
import numpy as np
import torch.nn as nn
import os


class RGCN_PreE(RGCN):
    def build_model(  # type: ignore
        self,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dim: int = 100,
    ):
        self.ent_embeddings.weight.data = torch.from_numpy(np.load(ent_embed_path)['embeddings'])
        self.ent_embeddings.weight.requires_grad = False
        
        if rel_embed_path is not None:
            self.rel_embeddings.weight.data = torch.from_numpy(np.load(rel_embed_path)['embeddings'])
            self.rel_embeddings.weight.requires_grad = False

        self.RGCN = nn.ModuleList()
        for idx in range(self.num_layers):
            RGCN_idx = self.build_hidden_layer(idx)
            self.RGCN.append(RGCN_idx)

def get_hpo_config() -> dict:
	parameters_dict = {
        **get_rgcn_hpo_config(),
        'model': {
            'value': 'RGCN_PreE'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'RGCN_PreE.RGCN_PreE'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
	return parameters_dict
