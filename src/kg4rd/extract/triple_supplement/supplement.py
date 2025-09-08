# -*- coding: utf-8 -*-
# Create Date: 2025/09/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: supplement.py
# Description: 三元组补充

import pandas as pd
import os
from tqdm import tqdm

exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')
data_path = 'data/data_abstract/approved_triples_node_exist'

kg_supplement = pd.DataFrame()

for file in tqdm(os.listdir(data_path), position=0):
    df = pd.read_csv(os.path.join(data_path, file))
    df = pd.merge(df, exists_nodes, left_on=['x_id', 'x_type'], right_on=['node_id', 'node_type'], how='inner').rename(
        columns={'node_index': 'x_index', 'node_name': 'x_name', 'node_source': 'x_source'}
    ).astype({'x_index': int}).astype({'x_index': str}).drop(columns=['node_id', 'node_type'])
    df = pd.merge(df, exists_nodes, left_on=['y_id', 'y_type'], right_on=['node_id', 'node_type'], how='inner').rename(
        columns={'node_index': 'y_index', 'node_name': 'y_name', 'node_source': 'y_source'}
    ).astype({'y_index': int}).astype({'y_index': str}).drop(columns=['node_id', 'node_type'])
    
    kg_supplement = pd.concat([kg_supplement, df])

kg_supplement = kg_supplement.drop(columns=[
    'x_preferred_name', 'y_preferred_name', 'x_preferred_name_score', 'y_preferred_name_score'
])
kg_supplement = kg_supplement.drop_duplicates(subset=['relation', 'x_id', 'y_id', 'x_type', 'y_type'], keep='first')
kg_supplement.to_csv('src/kg4rd/kg/kg_supplement.csv', index=False)

edges_supplement = kg_supplement[['relation', 'x_index', 'y_index', 'uid']].copy()
edges_supplement.to_csv('src/kg4rd/kg/edges_supplement.csv', index=False)
