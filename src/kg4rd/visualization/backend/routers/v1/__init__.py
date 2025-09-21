# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: __init__.py
# Description: 路由 v1

from fastapi import APIRouter
from .entity_router import router as entity_router
from .relation_router import router as relation_router
from .link_router import router as link_router

router = APIRouter(
    prefix='/api/v1'
)

router.include_router(entity_router)
router.include_router(relation_router)
router.include_router(link_router)