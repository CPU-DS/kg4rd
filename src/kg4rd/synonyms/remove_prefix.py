# -*- coding: utf-8 -*-
# Create Date: 2025/06/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: go.py
# Description: 去掉id 前缀

import pandas as pd

df = pd.read_csv('data_synonyms/go_synonyms.csv')
df['id'] = df['id'].apply(lambda x: x.replace('GO:', '')).astype(int).astype(str)
df.to_csv('data_synonyms/go_synonyms.csv', index=False)

df = pd.read_csv('data_synonyms/hpo_synonyms.csv')
df['id'] = df['id'].apply(lambda x: x.replace('HP:', '')).astype(int).astype(str)
df.to_csv('data_synonyms/hpo_synonyms.csv', index=False)

df = pd.read_csv('data_synonyms/uberon_synonyms.csv')
df['id'] = df['id'].apply(lambda x: x.replace('UBERON:', '')).astype(int).astype(str)
df.to_csv('data_synonyms/uberon_synonyms.csv', index=False)

df = pd.read_csv('data_synonyms/mondo_synonyms_concat.csv')
df['id'] = df['id'].apply(lambda x: x.replace('MONDO:', '')).astype(int).astype(str)
df.to_csv('data_synonyms/mondo_synonyms_concat.csv', index=False)