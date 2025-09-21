# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: result_model.py
# Description: 数据返回模型

from typing import Generic, TypeVar
from pydantic import BaseModel
from enum import Enum
from typing import Optional

T = TypeVar('T')


class ResultCode(Enum):
    QUERY_OK = 20011
    QUERY_ERR = 40011


class Result(BaseModel, Generic[T]):
    code: ResultCode
    message: str
    data: Optional[T]
