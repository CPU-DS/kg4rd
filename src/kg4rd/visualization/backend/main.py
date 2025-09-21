# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: main.py
# Description: 后端接口

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from routers import router_v1

from repos.relation_repo import RelationRepository
from repos.entity_repo import EntityRepository
from repos.model_repo import ModelRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.relation_repo = RelationRepository()
    app.state.entity_repo = EntityRepository()
    app.state.model_repo = ModelRepository()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router_v1)

@app.exception_handler(Exception)
async def generic_exception_handler(_, exc):
    return JSONResponse(
        status_code=500, 
        content={"message": "Server Error", "exec": str(exc)},
        headers={"Content-Type": "application/json"}
    )

if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=5555)
