# -*- coding: utf-8 -*-
# Create Date: 2025/06/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: reactome.py
# Description: pathway 别名

import pandas as pd
import requests
from tqdm import tqdm
import os
import json


df_terms = pd.read_csv('data/data/reactome/ReactomePathways.txt', sep='\t', names=['reactome_id', 'reactome_name', 'species'])
df_terms = df_terms.query('species=="Homo sapiens"')
df_terms = df_terms.reset_index().drop('index',axis=1)

data_path = os.path.join(os.path.dirname(__file__), 'data.json')
if not os.path.exists(data_path):
    json.dump([], open(data_path, 'w'))

data = json.load(open(data_path, 'r'))

for i, line in tqdm(enumerate(df_terms.itertuples()), total=len(df_terms)):
    if len(data) > 0 and i <= data[-1]['index']:
        continue
    id_ = line.reactome_id
    name = line.reactome_name
    try:
        r = requests.get(f'https://reactome.org/ContentService/data/query/enhanced/{id_}', 
                        headers={'Accept': 'application/json'})
        synonyms = r.json()['name']
    except Exception as e:
        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            f.write(json.dumps(data))
        raise e
    data.append({
        'index': i,
        'id': id_,
        'name': name,
        'preferred_name': True
    })
    for synonym in synonyms:
        data.append({
            'index': i,
            'id': id_,
            'name': synonym,
            'preferred_name': ''
        })

df = pd.DataFrame(data)
df = df.drop_duplicates(['id', 'name'])
df = df.drop(['index'], axis=1)
df.to_csv('data/data_synonyms/reactome_synonyms.csv', index=False)