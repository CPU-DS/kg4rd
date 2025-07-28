# -*- coding: utf-8 -*-
# Create Date: 2025/07/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: disease_desc_embed.py
# Description: disease description embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")


disease_umls = 'data/data_feature/disease_umls.csv'
df_disease_umls = pd.read_csv(disease_umls)
df_disease_umls = df_disease_umls[df_disease_umls['description'].notna()][['mondo_id', 'description']]

ids = list(map(int, df_disease_umls['mondo_id'].tolist()))
defs = df_disease_umls['description'].tolist()
embeddings = model.encode(defs, show_progress_bar=True, device='cuda')

np.savez_compressed('data/data_feature/disease_desc_embed.npz', 
                    ids=ids, 
                    embeddings=embeddings)