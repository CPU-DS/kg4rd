# -*- coding: utf-8 -*-
# Create Date: 2025/07/27
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drug_desc_embed.py
# Description: drug description embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import re

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")

drugbank = 'data/data_feature/drugbank.csv'
df_drugbank = pd.read_csv(drugbank)
df_drugbank = df_drugbank[df_drugbank['description'].notna()][['id', 'description']]
df_drugbank['id'] = df_drugbank['id'].apply(lambda x: int(x.strip('DB')))

ids = df_drugbank['id'].tolist()
embeddings = model.encode([re.sub(r'\[.*?\]', '', d) for d in df_drugbank['description'].tolist()], show_progress_bar=True, batch_size=64)

np.savez_compressed('data/data_feature/drug_desc_embed.npz', 
                   ids=ids,
                   embeddings=embeddings)
