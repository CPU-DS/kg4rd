# -*- coding: utf-8 -*-
# Create Date: 2025/10/22
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransD_PreEv2.py
# Description: TransD 改进模型

from unike.module.model import TransD, get_transd_hpo_config
import torch
from typing_extensions import override
import os
from .PreEv2Mixin import PreEv2Mixin


class TransD_PreEv2(PreEv2Mixin, TransD):
    def __init__(
        self,
        ent_tol: int,
        rel_tol: int,
        ent_embed_path: str,
        rel_embed_path: str | None = None,
        dim_e: int = 100,
        dim_r: int = 100,
        p_norm: int = 1,
        norm_flag: bool = True,
        margin: float | None = None,
        dropout: float = 0.1
    ):
        super().__init__(
            ent_tol=ent_tol,
            rel_tol=rel_tol,
            dim_e=dim_e,
            dim_r=dim_r,
            p_norm=p_norm,
            norm_flag=norm_flag,
            margin=margin
        )
        
        self.init_pre_embeddings(
            dim=self.dim_e,
            ent_embed_path=ent_embed_path,
            rel_embed_path=rel_embed_path,
            dropout=dropout
        )
    
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
        **get_transd_hpo_config(),
        'model': {
            'value': 'TransD_PreEv2'
        },
        'model_class_path': {
            'value': os.path.dirname(__file__)
        },
        'model_class': {
            'value': 'TransD_PreEv2.TransD_PreEv2'
        },
        'ent_embed_path': {
            'value': ''
        }
    }
    return parameters_dict
