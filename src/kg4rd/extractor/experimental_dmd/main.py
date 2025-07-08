# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: main.py
# Description: DMD 三元组抽取结果分析

import json
import sys
import re
import pandas as pd
import os
from tqdm import tqdm
sys.path.append('src/kg4rd')

from synonyms.simple_search import simple_search

synonyms = json.load(open('src/kg4rd/extractor/experimental_dmd/synonyms.json'))
dmd = json.load(open('src/kg4rd/extractor/experimental_dmd/dmd.json'))
relation_type_name_map = json.load(open('src/kg4rd/extractor/relation_type_name_map.json'))
node_type_name_map = json.load(open('src/kg4rd/extractor/node_type_name_map.json'))
exists_edges = pd.read_csv('src/kg4rd/kg/kg.csv')
exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')

triples = []
report = {
    '摘要数': len(dmd),
    '抽取到的三元组总数': 0,
    '抽取到的三元组去重后总数': 0,
    '双侧均未获取到同义词': 0,
    '双侧均获取到同义词': 0,
    '双侧均获取到id': 0,
    '关系不在限定范围内': 0,
    '已存在的三元组': 0,
    '新加入的三元组': 0,
    '新加入的三元组(双侧实体均已经存在)': 0,
}
unique_triples = set()

for result in tqdm(dmd):
    for triple in result['extracted_relations']:
        report['抽取到的三元组总数'] += 1
        
        subject = triple['subject']
        object_ = triple['object']
        relation = triple['predicate']
        
        unique_triples.add((subject, relation, object_))
        
for subject, relation, object_ in tqdm(unique_triples):
    report['抽取到的三元组去重后总数'] += 1
    
    rs = re.sub(r'\s*\([^)]*\)', '', relation)
    rs = [r.strip() for r in rs.split('-')]
    
    subject_preferred_name = synonyms.get(subject, {}).get('preferred_name', None)
    object_preferred_name = synonyms.get(object_, {}).get('preferred_name', None)
    
    if subject_preferred_name is None and object_preferred_name is None:
        report['双侧均未获取到同义词'] += 1
    elif subject_preferred_name is not None and object_preferred_name is not None:
        report['双侧均获取到同义词'] += 1
        
        subject_id = simple_search(subject_preferred_name, rs[0])
        subject_type = node_type_name_map.get(rs[0])
        object_id = simple_search(object_preferred_name, rs[1])
        object_type = node_type_name_map.get(rs[1])
        
        if subject_id is not None and object_id is not None:
            report['双侧均获取到id'] += 1
            if relation_type_name_map.get(relation, None) is None:
                report['关系不在限定范围内'] += 1
            else:
                triples.append({
                    'relation': relation_type_name_map[relation],
                    'x_type': subject_type,
                    'y_type': object_type,
                    'x_id': subject_id,
                    'y_id': object_id
                })
            
existing_edges_set = set(
    (row.relation, str(row.x_id), str(row.y_id), row.x_type, row.y_type)
    for row in exists_edges.itertuples(index=False)
)

existing_nodes_set = set(
    (row.node_id, row.node_type)
    for row in exists_nodes.itertuples(index=False)
)

triples_node_exist = []

for triple in tqdm(triples):
    relation, x_id, y_id, x_type, y_type = triple['relation'], triple['x_id'], triple['y_id'], triple['x_type'], triple['y_type']
    
    if (relation, x_id, y_id, x_type, y_type) in existing_edges_set:
        report['已存在的三元组'] += 1
    else:
        report['新加入的三元组'] += 1
        
        if (x_id, x_type) in existing_nodes_set and (y_id, y_type) in existing_nodes_set:
            report['新加入的三元组(双侧实体均已经存在)'] += 1
            triples_node_exist.append(triple)
        
print(report)

df_triples = pd.DataFrame(triples)
df_triples.to_csv('src/kg4rd/extractor/experimental_dmd/new_triples_dmd.csv', index=False)

pd.DataFrame(triples_node_exist).to_csv('src/kg4rd/extractor/experimental_dmd/new_triples_dmd_node_exist.csv', index=False)

# relation_type_name_map_reverse = {v: k for k, v in relation_type_name_map.items()}
# df_triples['relation_r'] = df_triples['relation'].apply(lambda x: relation_type_name_map_reverse[x])

# res = df_triples['relation_r'].value_counts()
# print(res)

# count = 0
# for triple in tqdm(triples_node_exist):
#     relation, x_id, y_id = triple['relation'], str(triple['x_id']), str(triple['y_id'])
#     rs = [r.strip() for r in relation.split('_')]
    
#     if 'disease' in rs:
#         loc = rs.index('disease')
#         if loc == 0:
#             if x_id == '10679':  # DMD
#                 count += 1
#         else:
#             if x_id == '10679':
#                 count += 1
            
# print(f'直接和DMD有关的三元组有{count}个')
