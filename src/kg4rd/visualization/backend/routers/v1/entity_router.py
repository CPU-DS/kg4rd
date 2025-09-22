# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: entity_router.py
# Description: 实体查询

from fastapi import APIRouter, Depends, Request
from models.result_model import Result
from models.entity_model import EntityDTO, EntityQuery, Entity
from services.entity_service import EntityService
from repos.entity_repo import EntityRepository

router = APIRouter(
    prefix='/entity'
)

async def get_entity_repo(request: Request) -> EntityRepository:
    return request.app.state.entity_repo

async def get_entity_service(entity_repo: EntityRepository = Depends(get_entity_repo)) -> EntityService:
    return EntityService(entity_repo)

@router.post('/query')
async def entity_query(
    query: EntityQuery,
    entity_service: EntityService = Depends(get_entity_service)
) -> Result[list[EntityDTO]]:
    return entity_service.query(query)

@router.get('/get')
async def entity_get(
    node_index: int,
    entity_service: EntityService = Depends(get_entity_service)
) -> Result[Entity]:
    return entity_service.get(node_index)
