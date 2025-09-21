# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: relation_router.py
# Description: 关系查询

from fastapi import APIRouter, Depends, Request
from repos.relation_repo import RelationRepository
from services.relation_service import RelationService
from models.relation_model import RelationQuery, Relation
from models.result_model import Result

router = APIRouter(
    prefix='/relation'
)

async def get_relation_repo(request: Request) -> RelationRepository:
    return request.app.state.relation_repo

async def get_relation_service(
    relation_repo: RelationRepository = Depends(get_relation_repo)
) -> RelationService:
    return RelationService(relation_repo)


@router.post('/query')
async def relation_query(
    query: RelationQuery,
    relation_service: RelationService = Depends(get_relation_service)
) -> Result[list[Relation]]:
    return relation_service.query(query)
