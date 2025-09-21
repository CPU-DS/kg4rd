# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: rela_model.py
# Description: 关系模型


from pydantic import BaseModel, Field
from typing import Optional, Literal
from models.entity_model import NODE_TYPE

RELA_DIRECTION = Literal['in', 'out', 'bidirection']
RELA_TYPE = Literal[
    'drug_drug',
    'protein_protein',
    'disease_phenotype_positive',
    'bioprocess_protein',
    'cellcomp_protein',
    'molfunc_protein',
    'phenotype_protein',
    'disease_protein',
    'disease_disease',
    'drug_effect',
    'pathway_protein',
    'bioprocess_bioprocess',
    'drug_protein',
    'phenotype_phenotype',
    'contraindication',
    'molfunc_molfunc',
    'indication',
    'cellcomp_cellcomp',
    'drug_pathway',
    'pathway_pathway',
    'off-label use',
    'disease_phenotype_negative'
]
MATCH_RELA_TYPE = Literal['all', RELA_TYPE]


class Relation(BaseModel):
    relation_name: str
    x_index: int
    x_name: str
    x_type: NODE_TYPE
    y_index: int
    y_name: str
    y_type: NODE_TYPE
    uid: Optional[str] = None
    display_relation_name: Optional[str] = None
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relation):
            return False
        return self.x_index == other.x_index and self.y_index == other.y_index
    
    def __hash__(self) -> int:
        return hash((self.x_index, self.y_index))
    

class RelationQuery(BaseModel):
    node_index: int
    direction: RELA_DIRECTION = 'bidirection'
    relation_type: MATCH_RELA_TYPE = 'all'
    hop: int = Field(default=1, ge=1, le=5)
