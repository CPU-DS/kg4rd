# -*- coding: utf-8 -*-
# Create Date: 2025/09/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: link_router.py
# Description: 链接预测

from fastapi import APIRouter, Depends, Request
from models.result_model import Result
from services.link_service import LinkService
from repos.model_repo import ModelRepository
from models.link_model import LinkRequest, LinkResult

router = APIRouter(
    prefix='/link'
)

async def get_model_repo(request: Request) -> ModelRepository:
    return request.app.state.model_repo

async def get_link_service(model_repo: ModelRepository = Depends(get_model_repo)) -> LinkService:
    return LinkService(model_repo)

@router.post('/predict')
async def link_predict(
    request: LinkRequest,
    link_service: LinkService = Depends(get_link_service)
) -> Result[LinkResult]:
    return link_service.link_predict(request)

@router.get('/model_names')
async def get_model_names(
    link_service: LinkService = Depends(get_link_service)
) -> Result[list[str]]:
    return link_service.get_model_names()
