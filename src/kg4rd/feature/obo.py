# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gene.py
# Description: OBO 中的定义

import os
import sys

import pandas as pd


sys.path.append('src/kg4rd')

from synonyms.obo_parser import OBOParser


parser = OBOParser('data/data/go/go-basic.obo', None)
all_terms = parser.parse()

df = pd.DataFrame(all_terms)
df = df.drop(columns=['synonyms', 'name'], axis=1)
df['id'] = df['id'].apply(lambda x: x.replace('GO:', '')).astype(int).astype(str)
df = df[df['def'] != '']
df.to_csv('data/data_feature/go.csv', index=False)

parser = OBOParser('data/data/hpo/hp.obo', None)
all_terms = parser.parse()

df = pd.DataFrame(all_terms)
df = df.drop(columns=['synonyms', 'name'], axis=1)
df['id'] = df['id'].apply(lambda x: x.replace('HP:', '')).astype(int).astype(str)
df = df[df['def'] != '']
df.to_csv('data/data_feature/hpo.csv', index=False)

parser = OBOParser('data/data/uberon/ext.obo', 'UBERON')
all_terms = parser.parse()

df = pd.DataFrame(all_terms)
df = df.drop(columns=['synonyms', 'name'], axis=1)
df['id'] = df['id'].apply(lambda x: x.replace('UBERON:', '')).astype(int).astype(str)
df = df[df['def'] != '']
print(df.head())
df.to_csv('data/data_feature/uberon.csv', index=False)