# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: entity_service.py
# Description: 实体查询

from models.result_model import Result, ResultCode
from models.entity_model import EntityDTO, EntityQuery, Entity
from repos.entity_repo import EntityRepository


class EntityService:
    def __init__(self, entity_repo: EntityRepository): 
        self.entity_repo = entity_repo

    def query(self, query: EntityQuery) -> Result[list[EntityDTO]]:
        message = "Entity data query success."
        if query.query_type == 'node_index':
            return Result(
                code=ResultCode.QUERY_OK,
                message=message,
                data=self.entity_repo.get_entity_dto_by_index(
                    node_index=query.query_value,
                    node_type=query.node_type,
                    match_mode=query.match_mode,
                    limit=query.limit
                )
            )
        else:
            return Result(
                code=ResultCode.QUERY_OK,
                message=message,
                data=self.entity_repo.get_entity_dto_by_name(
                    node_name=query.query_value,
                    node_type=query.node_type,
                    match_mode=query.match_mode,
                    limit=query.limit
                )
            )
    
    def get(self, node_index: int) -> Result[Entity]:
        entity = self.entity_repo.get_entity_by_index(node_index)
        if entity is None:
            return Result(
                code=ResultCode.QUERY_ERR,
                message="Entity not found.",
                data=None
            )
        return Result(
            code=ResultCode.QUERY_OK,
            message="Entity detail success.", 
            data=entity
        )
