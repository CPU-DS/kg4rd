# -*- coding: utf-8 -*-
# Create Date: 2025/09/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: data_parse.py
# Description: 抽取到的三元组处理

import json
import json5
import sys
import os
import re
import pandas as pd
from tqdm import tqdm
from pprint import pprint
from typing import TypedDict
sys.path.append('src/kg4rd')

from synonyms.simple_search import simple_search

relation_type_name_map = json5.load(open('src/kg4rd/extract/relation_type_name_map.json5'))
node_type_name_map = json5.load(open('src/kg4rd/extract/node_type_name_map.json5'))
exists_edges = pd.read_csv('src/kg4rd/kg/kg.csv')
exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')

existing_edges_set = set(zip(
    exists_edges['relation'],
    exists_edges['x_id'].astype(str),
    exists_edges['y_id'].astype(str),
    exists_edges['x_type'],
    exists_edges['y_type'],
))

existing_nodes_set = set(zip(
    exists_nodes['node_id'],
    exists_nodes['node_type'],
))

result_path = 'data/data_abstract/result'

def parse(data: list[dict], name: str, save_df: bool = True):
    original_triples = []
    approved_triples = []
    approved_triples_node_exist = []

    for result in tqdm(data, position=1, leave=False):
        relation_choices = result['relation_choices']
        for item in result['extracted_relations']:  # 获取到的三元组
            
            subject, object_, relation, uid = item['subject'], item['object'], item['predicate'], item['uid']  # SOP
            triple = {
                'subject': subject,
                'object': object_,
                'relation': relation,
                'uid': uid,
                'status': ''
            }
            
            original_triples.append(triple)

            rs = re.sub(r'\s*\([^)]*\)', '', relation)
            rs = [r.strip() for r in rs.split('-')]
            if len(rs) != 2:
                continue
            
            subject_type = node_type_name_map.get(rs[0], '')
            object_type = node_type_name_map.get(rs[1], '')
            
            subject_ret = simple_search(subject, subject_type)  # 名称和类型可能都有问题所以写作 synonym/id
            object_ret = simple_search(object_, object_type)
            
            if subject_ret is None and object_ret is None:
                triple['status'] = 'TWO_SIDE_NO_SYNONYM/ID'
            elif subject_ret is None or object_ret is None:
                triple['status'] = 'ONLY_ONE_SIDE_SYNONYM/ID'
            elif object_ret is not None and object_ret is not None:
                
                subject_id, subject_preferred_name, subject_preferred_name_score = subject_ret
                object_id, object_preferred_name, object_preferred_name_score = object_ret

                
                if relation not in relation_choices:
                    triple['status'] = 'RELATION_TYPE_NOT_IN_CHOICES'
                else:
                    relation = relation_type_name_map.get(relation)
                    if (relation, subject_id, object_id, subject_type, object_type) in existing_edges_set:
                        triple['status'] = 'KG_ALREADY_EXISTS'
                    else:
                        triple['status'] = 'APPROVED'
                        at = {
                                'relation': relation,
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
                            triple['status'] = 'APPROVED(NODE_ALL_EXISTS)'
                            approved_triples_node_exist.append(at)
                        approved_triples.append(at)
    
    df_original_triples = pd.DataFrame(original_triples, columns=['subject', 'object', 'relation', 'uid', 'status'])   # pyright: ignore[reportArgumentType]
    df_approved_triples = pd.DataFrame(approved_triples)
    df_approved_triples_node_exist = pd.DataFrame(approved_triples_node_exist)

    overview = {
        'abstract count': len(data),  # 摘要数量
        'extracted triples': len(df_original_triples),  # 抽取到的三元组数量
        'two side no synonyms/id': len(df_original_triples[df_original_triples['status'] == 'TWO_SIDE_NO_SYNONYM/ID']),  # 双侧均为获取到同义词
        'one side synonyms/id': len(df_original_triples[df_original_triples['status'] == 'ONLY_ONE_SIDE_SYNONYM/ID']),  # 仅一侧获取到同义词
        'relation type not in choices': len(df_original_triples[df_original_triples['status'] == 'RELATION_TYPE_NOT_IN_CHOICES']),  # 关系类型不在限定范围内
        'kg already exists': len(df_original_triples[df_original_triples['status'] == 'KG_ALREADY_EXISTS']),  # 三元组已存在
        'approved triples/before deduplication': len(df_approved_triples),  # 可用的三元组数量(去重前)
        'approved triples node exist/before deduplication': len(df_approved_triples_node_exist),  # 可用的三元组数量(双侧节点已存在)(去重前)
    }
    
    if save_df:
        os.makedirs('data/data_abstract/original_triples', exist_ok=True)
        os.makedirs('data/data_abstract/approved_triples', exist_ok=True)
        os.makedirs('data/data_abstract/approved_triples_node_exist', exist_ok=True)
        if df_original_triples.shape[0] > 0:
            df_original_triples.to_csv(os.path.join('data/data_abstract/original_triples', f'{name}.csv'), index=False)
        if df_approved_triples.shape[0] > 0:
            df_approved_triples.to_csv(os.path.join('data/data_abstract/approved_triples', f'{name}.csv'), index=False)
        if df_approved_triples_node_exist.shape[0] > 0:
            df_approved_triples_node_exist.to_csv(os.path.join('data/data_abstract/approved_triples_node_exist', f'{name}.csv'), index=False)  # 最后可用
    
    return overview

overview = {}
for file in tqdm(os.listdir(result_path), position=0):
    with open(os.path.join(result_path, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in parse(data, file.split('.')[0], save_df=True).items():
            overview[k] = overview.get(k, 0) + v  # 统计更新

with open('data/data_abstract/overview.json', 'w', encoding='utf-8') as f:
    json.dump(overview, f, ensure_ascii=False, indent=4)
