# -*- coding: utf-8 -*-
# Create Date: 2025/07/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drug_seq_embed.py
# Description: drug peptide sequence embedding

import pandas as pd
import re
from Bio import SeqIO
from io import StringIO
import numpy as np
from tqdm import tqdm
from protein_seq_embed import get_sequence_embedding

split_pattern = re.compile(r'>.*?\n')

drugbank = 'data/data_feature/drugbank.csv'
df_drugbank = pd.read_csv(drugbank)
# 有 SMILES 则不需要序列
df_drugbank = df_drugbank[df_drugbank['SMILES'].isna() & df_drugbank['sequences'].notna()][['id', 'sequences']]
df_drugbank['id'] = df_drugbank['id'].apply(lambda x: int(x.strip('DB')))
ids = []
embeddings = []

for _, row in tqdm(df_drugbank.iterrows(), total=len(df_drugbank)):
    id_ = row['id']
    seq = row['sequences'].replace('|>', '\n>')
    seq_embeds = []
    for record in SeqIO.parse(StringIO(seq), 'fasta'):
        if (embedding := get_sequence_embedding(str(record.seq))) is not None:
            seq_embeds.append(embedding.cpu().numpy())
    if len(seq_embeds) > 0:
        ids.append(id_)
        embeddings.append(np.mean(seq_embeds, axis=0))

np.savez_compressed('data/data_feature/drug_seq_embed.npz', 
                   ids=ids,
                   embeddings=embeddings)
