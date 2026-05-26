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
    def __init__(self, device: str = 'cuda:0'):
        self.link = Link(
            in_path=os.path.join(os.path.dirname(__file__), '../../../kge/data')
        )
        self._model_list = []
        self.device = device
        self.edges_supp_df = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), 
                '../../../kg/kg_supplement.csv'
            )
        )
        self.edges_supp_df['relation_index'] = self.edges_supp_df['relation'].apply(lambda x: self.link.rel2id[x])
        
    def add_model(self, model_name: str, model: Model, checkpoint_path: str):
        model.load_checkpoint(checkpoint_path, device=self.device)
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
            request.head, rels, request.tail, model, device=self.device
        )
        result = result.rename(columns={'in': 'in_kg'})
        if request.limit is not None:
            result = result.head(request.limit)
            
        result = pd.merge(  # 补充 uid
            result, 
            self.edges_supp_df, 
            left_on=['head', 'rel', 'tail'],
            right_on=['x_index', 'relation_index', 'y_index'],
            how='left'
        ).drop(columns=['x_index', 'relation_index', 'y_index'])
        
        return [
            LinkRelation(
                relation_name=row.rel_ent,  # type: ignore
                x_index=row.head,  # type: ignore
                x_name=':'.join(row.head_ent.split(':')[:-1]),  # type: ignore
                x_type=row.head_ent.split(':')[-1],  # type: ignore
                y_index=row.tail,  # type: ignore
                y_name=':'.join(row.tail_ent.split(':')[:-1]),  # type: ignore
                y_type=row.tail_ent.split(':')[1],  # type: ignore
                score=row.score,  # type: ignore
                type='present' if row.in_kg == True else 'absent',  # type: ignore
                uid=row.uid if not pd.isna(row.uid) else None  # type: ignore
            ) for row in result.itertuples()
        ]
