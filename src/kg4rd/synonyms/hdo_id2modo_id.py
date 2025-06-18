# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: hdo_id2modo_id.py
# Description: 将 HumanDO 的 ID 转换为 Mondo 的 ID

import pandas as pd


mondo_ref = 'data/mondo/mondo_references.csv'
mondo_ref_df = pd.read_csv(mondo_ref).query('ontology == "DOID"')
mondo_ref_df['ontology_id'] = mondo_ref_df['ontology_id'].astype(int)

do_synonyms = 'data_synonyms/do_synonyms.csv'
do_synonyms_df = pd.read_csv(do_synonyms)
do_synonyms_df['id'] = do_synonyms_df['id'].str.replace(r'^DOID:', '', regex=True).astype(int)

do_synonyms_mondo_df = pd.merge(do_synonyms_df, mondo_ref_df, 'inner', left_on='id', right_on='ontology_id')
do_synonyms_mondo_df = do_synonyms_mondo_df.drop(['ontology_id', 'ontology'], axis=1)
do_synonyms_mondo_df['mondo_id'] = do_synonyms_mondo_df['mondo_id'].apply(lambda x: f"MONDO:{int(x):07d}")
do_synonyms_mondo_df['id'] = do_synonyms_mondo_df['id'].apply(lambda x: f"DOID:{int(x):07d}")

do_synonyms_mondo_df.to_csv('data_synonyms/do_synonyms_mondo_id.csv', index=False)
