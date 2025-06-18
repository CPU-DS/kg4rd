# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: drugcentral.py
# Description: 将 drugcentral 的 ID 转换为 drugbank 的 ID

import pandas as pd


df = pd.read_csv('data_synonyms/drugcentral_synonyms.csv', low_memory=False)
df = df.query('not @df.cas_reg_no.isna()')
df = df.sort_values(by=['id', 'preferred_name'])
df['preferred_name'] = df['preferred_name'].apply(lambda x: True if x == 1.0 else x)


db_vocab = pd.read_csv('data/vocab/drugbank_vocabulary.csv', low_memory=False)

df = pd.merge(df, db_vocab, 'inner', left_on='cas_reg_no', right_on='CAS').get(['id', 'name', 'preferred_name', 'DrugBank ID']).rename(columns={'DrugBank ID': 'drugbank_id'})

df.to_csv('data_synonyms/drugcentral_synonyms_drugbank_id.csv', index=False)