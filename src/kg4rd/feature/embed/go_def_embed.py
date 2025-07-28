# -*- coding: utf-8 -*-
# Create Date: 2025/07/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: go_def_embed.py
# Description: go definition embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")


go = 'data/data_feature/go.csv'
df_go = pd.read_csv(go)
df_go = df_go[df_go['def'].notna()][['id', 'def']]

ids = list(map(int, df_go['id'].tolist()))
defs = df_go['def'].tolist()
embeddings = model.encode(defs, show_progress_bar=True, batch_size=64)

np.savez_compressed('data/data_feature/go_def_embed.npz', 
                    ids=ids, 
                    embeddings=embeddings)