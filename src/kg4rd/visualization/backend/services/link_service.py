# -*- coding: utf-8 -*-
# Create Date: 2025/09/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: link_service.py
# Description: 链接预测

from repos.model_repo import ModelRepository
from models.link_model import LinkRequest, LinkResult
from models.result_model import Result, ResultCode

class LinkService:
    def __init__(self, model_repo: ModelRepository):
        self.model_repo = model_repo

    def link_predict(self, request: LinkRequest) -> Result[LinkResult]:
        return Result(
            code=ResultCode.QUERY_OK,
            message="Link predict success.",
            data=self.model_repo.link_predict(request)
        )
        
    def get_model_names(self) -> Result[list[str]]:
        return Result(
            code=ResultCode.QUERY_OK,
            message="Get model names success.",
            data=self.model_repo.get_model_names()
        )
