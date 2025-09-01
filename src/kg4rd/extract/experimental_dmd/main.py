# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: main.py
# Description: DMD 三元组抽取结果分析

import json
import json5
import sys
import re
import pandas as pd
from tqdm import tqdm
sys.path.append('src/kg4rd')

from synonyms.simple_search import simple_search

synonyms = json.load(open('src/kg4rd/extract/experimental_dmd/synonyms.json'))
dmd = json.load(open('src/kg4rd/extract/experimental_dmd/dmd.json'))
relation_type_name_map = json5.load(open('src/kg4rd/extract/relation_type_name_map.json5'))
node_type_name_map = json5.load(open('src/kg4rd/extract/node_type_name_map.json5'))
exists_edges = pd.read_csv('src/kg4rd/kg/kg.csv')
exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')

existing_edges_set = set(
    (row.relation, str(row.x_id), str(row.y_id), row.x_type, row.y_type)
    for row in exists_edges.itertuples(index=False)
)

existing_nodes_set = set(
    (row.node_id, row.node_type)
    for row in exists_nodes.itertuples(index=False)
)

original_triples = []
approved_triples = []
approved_triples_node_exist = []

for result in tqdm(dmd):
    for triple in result['extracted_relations']:
        
        subject = triple['subject']
        object_ = triple['object']
        relation = triple['predicate']
        
        original_triples.append({
            'subject': subject,
            'object': object_,
            'relation': relation,
            'uid': triple['uid'],
            'status': ''
        })
    
        rs = re.sub(r'\s*\([^)]*\)', '', relation)
        rs = [r.strip() for r in rs.split('-')]
        
        subject_preferred_name = synonyms.get(subject, {}).get('preferred_name', None)
        subject_preferred_name_score = synonyms.get(subject, {}).get('score', None)
        object_preferred_name = synonyms.get(object_, {}).get('preferred_name', None)
        object_preferred_name_score = synonyms.get(object_, {}).get('score', None)
        
        
        if subject_preferred_name is None and object_preferred_name is None:
            original_triples[-1]['status'] = 'TWO_SIDE_NO_SYNONYM'
        elif subject_preferred_name is None or object_preferred_name is None:
            original_triples[-1]['status'] = 'ONLY_ONE_SIDE_SYNONYM'
        elif subject_preferred_name is not None and object_preferred_name is not None:
            
            subject_id = simple_search(subject_preferred_name, rs[0])
            subject_type = node_type_name_map.get(rs[0])
            object_id = simple_search(object_preferred_name, rs[1])
            object_type = node_type_name_map.get(rs[1])
            
            if subject_id is not None and object_id is not None:
                if (relation_type := relation_type_name_map.get(relation, None)) is None:
                    original_triples[-1]['status'] = 'ERROR_RELATION_TYPE'
                else:
                    if (relation_type, subject_id, object_id, subject_type, object_type) in existing_edges_set:
                        original_triples[-1]['status'] = 'KG_ALREADY_EXISTS'
                    else:
                        original_triples[-1]['status'] = 'APPROVED'
                        at = {
                                'relation': relation_type,
                                'x_type': subject_type,
                                'y_type': object_type,
                                'x_id': subject_id,
                                'y_id': object_id,
                                'uid': triple['uid'],
                                'x_preferred_name': subject_preferred_name,
                                'y_preferred_name': object_preferred_name,
                                'x_preferred_name_score': subject_preferred_name_score,
                                'y_preferred_name_score': object_preferred_name_score,
                            }
                        if (subject_id, subject_type) in existing_nodes_set and (object_id, object_type) in existing_nodes_set:
                            original_triples[-1]['status'] = 'APPROVED(NODE_ALL_EXISTS)'
                            approved_triples_node_exist.append(at)
                        approved_triples.append(at)
            else:
                original_triples[-1]['status'] = 'NO_ID'

df_original_triples = pd.DataFrame(original_triples)
df_approved_triples = pd.DataFrame(approved_triples)
df_approved_triples_node_exist = pd.DataFrame(approved_triples_node_exist)

print('摘要数: ', len(dmd))
len_original_triples = len(df_original_triples)
print('抽取到的三元组总数: ', len_original_triples)

len_two_side_no_synonym = len(df_original_triples[df_original_triples['status'] == 'TWO_SIDE_NO_SYNONYM'])
print('双侧均未获取到同义词: ', len_two_side_no_synonym)

len_only_one_side_synonym = len(df_original_triples[df_original_triples['status'] == 'ONLY_ONE_SIDE_SYNONYM'])
print('双侧仅获取到一侧同义词: ', len_only_one_side_synonym)

print('双侧均获取到同义词: ', len_original_triples - len_two_side_no_synonym - len_only_one_side_synonym)

len_no_id = len(df_original_triples[df_original_triples['status'] == 'NO_ID'])
print('单侧或双侧未获取到id: ', len_no_id)

print('双侧均获取到id: ', len_original_triples - len_two_side_no_synonym - len_only_one_side_synonym - len_no_id)

print('关系不在限定范围内: ', len(df_original_triples[df_original_triples['status'] == 'ERROR_RELATION_TYPE']))

print('三元组已存在: ', len(df_original_triples[df_original_triples['status'] == 'KG_ALREADY_EXISTS']))

print('新加入的三元组(去重前): ', len(df_approved_triples))
print('新加入的三元组(双侧实体均已存在)(去重前): ', len(df_approved_triples_node_exist))

df_approved_triples.drop_duplicates(subset=['relation', 'x_id', 'y_id', 'x_type', 'y_type'], inplace=True, keep='first')
df_approved_triples_node_exist.drop_duplicates(subset=['relation', 'x_id', 'y_id', 'x_type', 'y_type'], inplace=True, keep='first')

print('新加入的三元组(去重后): ', len(df_approved_triples))
print('新加入的三元组(双侧实体均已存在)(去重后): ', len(df_approved_triples_node_exist))

df_original_triples.to_csv('src/kg4rd/extract/experimental_dmd/original_triples.csv', index=False)
df_approved_triples.to_csv('src/kg4rd/extract/experimental_dmd/approved_triples.csv', index=False)
df_approved_triples_node_exist.to_csv('src/kg4rd/extract/experimental_dmd/approved_triples_node_exist.csv', index=False)
