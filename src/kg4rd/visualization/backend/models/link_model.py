# -*- coding: utf-8 -*-
# Create Date: 2025/09/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: link_model.py
# Description: 链接预测模型

from pydantic import BaseModel
from models.relation_model import RELA_TYPE
from models.entity_model import NODE_TYPE
from typing import Literal

class LinkRequest(BaseModel):
    head: list[int] | NODE_TYPE
    rel: list[RELA_TYPE]
    tail: list[int] | NODE_TYPE
    model_name: str
    limit: int = 100

LINK_RELATION_TYPE = Literal['present', 'absent']

class LinkRelation(BaseModel):
    relation_name: str
    x_index: int
    x_name: str
    x_type: NODE_TYPE
    y_index: int
    y_name: str
    y_type: NODE_TYPE
    score: float
    type: LINK_RELATION_TYPE
    
LinkResult = list[LinkRelation]