# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: entity_model.py
# Description: 实体模型

from pydantic import BaseModel, Field
from typing import Literal

NODE_TYPE = Literal[
    'disease', 
    'drug', 
    'gene/protein', 
    'pathway', 
    'effect/phenotype', 
    'molecular_function', 
    'cellular_component', 
    'biological_process'
]
MATCH_NODE_TYPE = Literal['all', NODE_TYPE]
MATCH_MODE = Literal['strict', 'contains', 'prefix', 'regex']

class Entity(BaseModel):
    node_index: int
    node_id: str
    node_name: str
    node_type: NODE_TYPE
    node_source: str
    node_source_url: list[str] = Field(default_factory=list)
    node_properties: dict[str, str] = Field(default_factory=dict)

class EntityDTO(BaseModel):
    node_index: int
    node_name: str
    node_type: str
 
class EntityQuery(BaseModel):
    query_type: Literal['node_index', 'node_name']
    query_value: str
    node_type: MATCH_NODE_TYPE = 'all'
    match_mode: MATCH_MODE = 'strict'
    limit: int = Field(default=10, ge=-1)
