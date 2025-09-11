# -*- coding: utf-8 -*-
# Create Date: 2025/09/10
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: link.py
# Description: 快速数据和 link 对象

from unike.utils import Link
import pandas as pd
import os
from typing import Optional

link = Link(
    in_path=os.path.join(os.path.dirname(__file__), '../../data')
)

# 治疗关系
indication_rel_index = 3

# 实体
dmd_ent_index = 40189
s1pr1_ent_index = 5153
tak1_ent_index = 9662 # MAP3K7
ad_ent_index = 49932

# 药品实体
drug_ent_indexs = [link.ent2id[ent_name] for ent_name in link.ent2id.keys() if ent_name.split(':')[-1] == 'drug']

_edges_supplement = pd.read_csv(
    os.path.join(os.path.dirname(__file__), '../../../kg/edges_supplement.csv'), 
    low_memory=False)
_edges_supplement['relation_index'] = _edges_supplement['relation'].apply(lambda x: link.rel2id[x])
_edges_supplement = _edges_supplement.drop(columns=['relation'])

# 如果该关系为新补充则添加相应的 uid 值
def supplement_uid(df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(
        df, 
        _edges_supplement, 
        left_on=['head', 'rel', 'tail'],
        right_on=['x_index', 'relation_index', 'y_index'],
        how='left'
    ).drop(columns=['x_index', 'relation_index', 'y_index'])
    
def _search(head: int, rel: int, tail: int) -> Optional[str]:
    row = _edges_supplement.query('x_index == @head and relation_index == @rel and y_index == @tail')
    if len(row) == 0:
        return None
    return row['uid'].values[0]

if __name__ == '__main__':
    print(_search(20877, 3, 40189))
