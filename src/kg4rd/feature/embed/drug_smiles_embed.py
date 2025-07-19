# -*- coding: utf-8 -*-
# Create Date: 2025/07/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drug_smiles_embed.py
# Description: drug smiles embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
from transformers import BertTokenizerFast, BertModel
import numpy as np
import torch
from tqdm import trange

device = torch.device('cuda:3' if torch.cuda.is_available() else 'cpu')

checkpoint = 'unikei/bert-base-smiles'
tokenizer = BertTokenizerFast.from_pretrained(checkpoint)
model = BertModel.from_pretrained(checkpoint)
model = model.to(device)

drugbank = 'data/data_feature/drugbank.csv'
df_drugbank = pd.read_csv(drugbank)
df_drugbank = df_drugbank[df_drugbank['SMILES'].notna()][['id', 'SMILES']]
df_drugbank['id'] = df_drugbank['id'].apply(lambda x: int(x.strip('DB')))
ids = df_drugbank['id'].tolist()
smiles = df_drugbank['SMILES'].tolist()

print(len(ids))
print(len(smiles))

chunk_size = len(smiles) // 100 + 1
all_embeddings = []

for i in trange(100):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, len(smiles))
    
    if start_idx >= len(smiles):
        break
        
    chunk_smiles = smiles[start_idx:end_idx]
    
    tokens = tokenizer(chunk_smiles, return_tensors='pt', padding='max_length', truncation=True)
    tokens = tokens.to(device)
    with torch.no_grad():
        predictions = model(**tokens)
    chunk_embeddings = predictions.last_hidden_state[:,-1,:].cpu().numpy()
    all_embeddings.append(chunk_embeddings)

final_embeddings = np.concatenate(all_embeddings, axis=0)
print(final_embeddings.shape)
np.savez_compressed('data/data_feature/drug_smiles_embed.npz', 
                   ids=ids,
                   embeddings=final_embeddings)
