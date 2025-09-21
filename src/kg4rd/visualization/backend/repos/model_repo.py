# -*- coding: utf-8 -*-
# Create Date: 2025/09/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: model_repo.py
# Description: 模型推理服务

from pydantic_core.core_schema import model_schema
from unike.utils import Link
from unike.module.model import Model
import os
from typing import Optional
from models.link_model import LinkRequest, LinkResult, LinkRelation
import pandas as pd


class ModelRepository:
    def __init__(self):
        self.link = Link(
            in_path=os.path.join(os.path.dirname(__file__), '../../../kge/data')
        )
        self._model_list = []
        
    def add_model(self, model_name: str, model: Model):
        self._model_list.append({
            'model_name': model_name,
            'model': model
        })
        
    def get_model(self, model_name: str) -> Optional[Model]:
        for model in self._model_list:
            if model['model_name'] == model_name:
                return model['model']
        return None
    
    def get_model_names(self) -> list[str]:
        return [model['model_name'] for model in self._model_list]

    def link_predict(
            self,
            request: LinkRequest
        ) -> LinkResult:
        if (model := self.get_model(request.model_name)) is None:
            return []
        if isinstance(request.head, str):
            request.head = [self.link.ent2id[ent_name] for ent_name in self.link.ent2id.keys() if ent_name.split(':')[-1] == request.head]
        if isinstance(request.tail, str):
            request.tail = [self.link.ent2id[ent_name] for ent_name in self.link.ent2id.keys() if ent_name.split(':')[-1] == request.tail]
        rels = [self.link.rel2id[rel] for rel in request.rel]
        result = self.link.link(
            request.head, rels, request.tail, model, device='cuda:0'
        ).head(request.limit)
        
        return [
            LinkRelation(
                relation_name=row.relation,
                x_index=row.head,
                x_name=self.link.id2ent[row.head].split(':')[0],
                x_type=self.link.id2ent[row.head].split(':')[1],
                y_index=row.tail,
                y_name=self.link.id2ent[row.tail].split(':')[0],
                y_type=self.link.id2ent[row.tail].split(':')[1],
                score=row.score,
                type='present' if row['in'] == True else 'absent'
            ) for row in result
        ]
