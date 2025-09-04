# -*- coding: utf-8 -*-
# Create Date: 2025/09/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: addition.py
# Description: 三元组补充

import pandas as pd
import os

exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')

data_path = 'data/data_abstract/approved_triples_node_exist'

edges_addition = pd.DataFrame()

for file in os.listdir(data_path):
    df = pd.read_csv(os.path.join(data_path, file))
    # 获取两侧 node index
    df = pd.merge(df, exists_nodes, left_on=['x_id', 'x_type'], right_on=['node_id', 'node_type'], how='inner').rename(columns={'node_index': 'x_index'})[
    ['relation', 'x_index', 'y_id', 'y_type', 'uid']
].astype({'x_index': int}).astype({'x_index': str})
    df = pd.merge(df, exists_nodes, left_on=['y_id', 'y_type'], right_on=['node_id', 'node_type'], how='inner').rename(columns={'node_index': 'y_index'})[
    ['relation', 'x_index', 'y_index', 'uid']  # 只剩下 relation x_index y_index uid
].astype({'y_index': int}).astype({'y_index': str})
    
    edges_addition = pd.concat([edges_addition, df])
    
edges_addition.to_csv('src/kg4rd/kg/edges_addition.csv', index=False) # 并非完整结构
