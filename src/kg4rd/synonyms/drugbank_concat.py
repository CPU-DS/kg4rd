# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drugbank_concat.py
# Description: drugbank 同义词合并

import pandas as pd


drugcentral_df = pd.read_csv('data/data_synonyms/drugcentral_synonyms_drugbank_id.csv').drop(['id'], axis=1).rename(columns={'drugbank_id': 'id'})
drugbank_df = pd.read_csv('data/data_synonyms/drugbank_synonyms.csv')

df = pd.concat([drugbank_df, drugcentral_df], axis=0)

df['name'] = df['name'].apply(lambda x: x.lower())

# 可能会存在多个 True

df = df.drop_duplicates(['id', 'name'], keep='first')
df = df.sort_values(by=['id', 'preferred_name'], ascending=[True, False], na_position='last')
df.to_csv('data/data_synonyms/drugbank_synonyms_concat.csv', index=False)
