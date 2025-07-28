# -*- coding: utf-8 -*-
# Create Date: 2025/07/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: disease_def_embed.py
# Description: disease definition embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")


disease_mondo = 'data/data_feature/disease_mondo.csv'
df_disease_mondo = pd.read_csv(disease_mondo)
df_disease_mondo = df_disease_mondo[df_disease_mondo['definition'].notna()][['mondo_id', 'definition']]

ids = list(map(int, df_disease_mondo['mondo_id'].tolist()))
defs = df_disease_mondo['definition'].tolist()
embeddings = model.encode(defs, show_progress_bar=True, device='cuda')

np.savez_compressed('data/data_feature/disease_def_embed.npz', 
                    ids=ids, 
                    embeddings=embeddings)