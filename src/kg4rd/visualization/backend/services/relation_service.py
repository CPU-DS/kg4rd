# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: relation_service.py
# Description: 关系查询

from models.result_model import Result, ResultCode
from models.relation_model import RelationQuery, Relation
from repos.relation_repo import RelationRepository


class RelationService:
    def __init__(self, relation_repo: RelationRepository):
        self.relation_repo = relation_repo

    def query(self, query: RelationQuery) -> Result[list[Relation]]:
        return Result(
            code=ResultCode.QUERY_OK,
            message="Relation data query success.",
            data=self.relation_repo.get_relation_by_node_index(
                node_index=query.node_index, 
                direction=query.direction, 
                relation_type=query.relation_type, 
                hop=query.hop
            )
        )