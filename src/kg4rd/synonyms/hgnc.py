# -*- coding: utf-8 -*-
# Create Date: 2025/06/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: hgnc.py
# Description: protein/gene 同义词

import pandas as pd
import json
from tqdm import tqdm


gene_id_df = pd.read_csv('data/data/vocab/gene_names.csv', sep='\t').get(['Approved symbol', 'NCBI Gene ID(supplied by NCBI)']).drop_duplicates().dropna()
gene_id_df = gene_id_df.rename(columns={'Approved symbol': 'symbol', 'NCBI Gene ID(supplied by NCBI)': 'id'})
gene_id = dict(zip(gene_id_df['symbol'], gene_id_df['id']))

data = []
with open('data/data/hgnc/hgnc_complete_set.json', 'r') as f:
    docs = json.load(f)['response']['docs']
    for line in tqdm(docs):
        symbol = line['symbol']
        name = line['name']
        prev_symbol = line.get('prev_symbol', [])
        prev_name = line.get('prev_name', [])
        alias_name = line.get('alias_name', [])
        
        names = [name] + prev_symbol + prev_name + alias_name
        id_ = gene_id.get(symbol, None)
        if id_ is None:
            continue
        data.append({
            'id': id_,
            'name': symbol,
            'preferred_name': True
        })
        for name in names:
            data.append({
                'id': id_,
                'name': name,
                'preferred_name': ''
            })

df = pd.DataFrame(data)
df['id'] = df['id'].astype(int).astype(str)
df = df.drop_duplicates(['id', 'name'])
print(df.shape)

for k,v in gene_id.items():
    data.append(
        {
            'id': v,
            'name': k,
            'preferred_name': True
        }
    )
    
df = df.drop_duplicates()
print(df.shape)

# 检查并打印有相同name但不同id的情况
duplicate_names = df[df.duplicated('name', keep=False)].sort_values('name')
conflicting_names = duplicate_names.groupby('name').filter(lambda x: x['id'].nunique() > 1)
if not conflicting_names.empty:
    print("Found entries with same name but different ids:")
    print(conflicting_names)
    # 删除这些有冲突的行
    df = df[~df['name'].isin(conflicting_names['name'])]

print(df.shape)
df.to_csv('data/data_synonyms/hgnc_synonyms.csv', index=False)