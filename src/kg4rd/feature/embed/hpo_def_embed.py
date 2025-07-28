# -*- coding: utf-8 -*-
# Create Date: 2025/07/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: hpo_def_embed.py
# Description: hpo definition embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")


hpo = 'data/data_feature/hpo.csv'
df_hpo = pd.read_csv(hpo)
df_hpo = df_hpo[df_hpo['def'].notna()][['id', 'def']]

ids = list(map(int, df_hpo['id'].tolist()))
defs = df_hpo['def'].tolist()
embeddings = model.encode(defs, show_progress_bar=True, batch_size=64)

np.savez_compressed('data/data_feature/hpo_def_embed.npz', 
                    ids=ids, 
                    embeddings=embeddings)