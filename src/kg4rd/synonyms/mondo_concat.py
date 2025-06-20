# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: concat.py
# Description: MONDO 同义词合并

import pandas as pd

do_df = pd.read_csv('data_synonyms/do_synonyms_mondo_id.csv').drop(['id'], axis=1).rename(columns={'mondo_id': 'id'})
orphanet_df = pd.read_csv('data_synonyms/orphanet_synonyms.csv').drop(['id'], axis=1).rename(columns={'mondo_id': 'id'})
mondo_df = pd.read_csv('data_synonyms/mondo_synonyms.csv')

df = pd.concat([mondo_df, do_df, orphanet_df], axis=0)
df = df.drop_duplicates(['id', 'name'], keep='first')

df['name'] = df['name'].astype(str).apply(lambda x: x.lower())

df = df.sort_values(by=['id', 'preferred_name'], ascending=[True, False], na_position='last')
df.to_csv('data_synonyms/mondo_synonyms_concat.csv', index=False)
