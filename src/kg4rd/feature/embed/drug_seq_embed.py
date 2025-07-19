# -*- coding: utf-8 -*-
# Create Date: 2025/07/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drug_seq_embed.py
# Description: drug peptide sequence embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import re

split_pattern = re.compile(r'>.*?\n')

drugbank = 'data/data_feature/drugbank.csv'
df_drugbank = pd.read_csv(drugbank)
df_drugbank = df_drugbank[df_drugbank['sequences'].notna()][['id', 'sequences']]
for idx, row in df_drugbank.iterrows():
    print(row['sequences'])
    print('-' * 100)
    
