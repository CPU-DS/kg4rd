# -*- coding: utf-8 -*-
# Create Date: 2026/02/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: RGCN_PreE.py
# Description: RGCN 改进模型, 使用 GCL 训练得到节点预嵌入

from unike.module.model import RGCN, get_rgcn_hpo_config
from unike.module.model import Model
import torch
import numpy as np
import torch.nn as nn
import os
import torch.nn.functional as F
from dgl.nn.pytorch.conv import RelGraphConv


class RGCN_PreE(RGCN):
    def __init__(
    self,
    ent_tol: int,
    rel_tol: int,
    dim: int,
    num_layers: int,
    ent_embed_path: str):
        Model.__init__(self, ent_tol, rel_tol)

        self.dim: int = dim
        self.num_layers: int = num_layers
        self.ent_emb: torch.nn.Embedding = None  # type: ignore
        self.rel_emb: torch.nn.parameter.Parameter = None  # type: ignore
        self.RGCN: torch.nn.ModuleList = None  # type: ignore
        self.Loss_emb: torch.nn.Embedding = None  # type: ignore
        
        self.ent_embed_path: str = ent_embed_path
        
        self.build_model()

    def build_model(self):
        self.ent_emb = nn.Embedding(self.ent_tol, self.dim)
        self.ent_emb.weight.data = torch.from_numpy(np.load(self.ent_embed_path)['embeddings'])
        self.ent_emb.weight.requires_grad = False

        self.rel_emb = nn.Parameter(torch.Tensor(self.rel_tol, self.dim))
        nn.init.xavier_uniform_(self.rel_emb, gain=nn.init.calculate_gain('relu'))

        self.RGCN = nn.ModuleList()
        for idx in range(self.num_layers):
            RGCN_idx = self.build_hidden_layer(idx)
            self.RGCN.append(RGCN_idx)
    
    def build_hidden_layer(self,idx: int) -> RelGraphConv:
        act = F.relu if idx < self.num_layers - 1 else None
        return RelGraphConv(self.dim, self.dim, self.rel_tol, "bdd",
                    num_bases=128, activation=act, self_loop=True, dropout=0.2)

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
