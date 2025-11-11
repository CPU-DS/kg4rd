# -*- coding: utf-8 -*-
# Create Date: 2025/11/11
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: up_dataset.py
# Description: 上传数据集到 huggingface

import os

os.environ["HF_ENDPOINT"] = "https://huggingface.co"

from huggingface_hub import HfApi

api = HfApi()
api.upload_large_folder(
    repo_id="wangtao2001/kg4rd",
    repo_type="dataset",
    folder_path="/home/wangtao/src/kg4rd/data",
    num_workers=64
)
