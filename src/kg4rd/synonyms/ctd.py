# -*- coding: utf-8 -*-
# Create Date: 2025/06/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: exporse.py
# Description: ctd 中 暴露的别名

import pandas as pd
import io
from tqdm import tqdm


data = []

path = 'data/data/ctd/CTD_chemicals.csv'
with open(path, 'r') as f:
    lines = [line for line in f.readlines() if not line.startswith('#')]
    df = pd.read_csv(io.StringIO('\n'.join(lines)), 
                     names=['ChemicalName', 
                             'ChemicalID', 
                             'CasRN', 
                             'Definition', 
                             'ParentIDs', 
                             'TreeNumbers', 
                             'ParentTreeNumbers', 
                             'Synonyms'])
    df = df.get(['ChemicalName', 'ChemicalID', 'Synonyms'])
    df['ChemicalID'] = df['ChemicalID'].str.replace('MESH:', '')
    for _, line in tqdm(df.iterrows(), total=len(df)):
        data.append({
            'id': line['ChemicalID'],
            'name': line['ChemicalName'],
            'preferred_name': True
        })
        if pd.notna(line['Synonyms']):
            for synonym in line['Synonyms'].split('|'):
                data.append({
                    'id': line['ChemicalID'],
                    'name': synonym,
                    'preferred_name': ''
                })
            
df = pd.DataFrame(data)
df = df.drop_duplicates(['id', 'name'])
df.to_csv('data/data_synonyms/ctd_synonyms.csv', index=False)