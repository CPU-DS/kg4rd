# -*- coding: utf-8 -*-
# Create Date: 2025/09/03
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: parse.py
# Description: 抽取到的三元组处理

import json
import json5
import sys
import os
import re
import pandas as pd
from tqdm import tqdm
sys.path.append('src/kg4rd')

from synonyms.simple_search import simple_search

# data prepare
synonyms = json.load(open('src/kg4rd/extract/experimental_dmd/synonyms.json'))
relation_type_name_map = json5.load(open('src/kg4rd/extract/relation_type_name_map.json5'))
node_type_name_map = json5.load(open('src/kg4rd/extract/node_type_name_map.json5'))
exists_edges = pd.read_csv('src/kg4rd/kg/kg.csv')
exists_nodes = pd.read_csv('src/kg4rd/kg/nodes.csv')

existing_edges_set = set(
    (row['relation'], str(row['x_id']), str(row['y_id']), row['x_type'], row['y_type'])
    for _, row in exists_edges.iterrows()
)

existing_nodes_set = set(
    (row['node_id'], row['node_type'])
    for _, row in exists_nodes.iterrows()
)

result_path = 'data/data_abstract/result'

def parse(data: list[dict], name: str, save_df: bool = True):
    original_triples = []
    approved_triples = []
    approved_triples_node_exist = []

    for result in tqdm(data):
        relation_choices = result['relation_choices']
        for triple in result['extracted_relations']:  # 获取到的三元组
            
            subject, object_, relation = triple['subject'], triple['object'], triple['predicate']  # SOP
            
            original_triples.append({
                'subject': subject,
                'object': object_,
                'relation': relation,
                'uid': triple['uid'],
                'status': ''
            })
        
            rs = re.sub(r'\s*\([^)]*\)', '', relation)
            rs = [r.strip() for r in rs.split('-')]
            
            subject_type = node_type_name_map.get(rs[0])
            object_type = node_type_name_map.get(rs[1])
            
            subject_ret = simple_search(subject, subject_type)  # 名称和类型可能都有问题所以写作 synonym/id
            object_ret = simple_search(object_, object_type)
            
            if subject_ret is None and object_ret is None:
                original_triples[-1]['status'] = 'TWO_SIDE_NO_SYNONYM/ID'
            elif subject_ret is None or object_ret is None:
                original_triples[-1]['status'] = 'ONLY_ONE_SIDE_SYNONYM/ID'
            elif object_ret is not None and object_ret is not None:
                
                subject_id, subject_preferred_name, subject_preferred_name_score = subject_ret
                object_id, object_preferred_name, object_preferred_name_score = object_ret

                
                if relation not in relation_choices:
                    original_triples[-1]['status'] = 'RELATION_TYPE_NOT_IN_CHOICES'
                else:
                    if (relation, subject_id, object_id, subject_type, object_type) in existing_edges_set:
                        original_triples[-1]['status'] = 'KG_ALREADY_EXISTS'
                    else:
                        original_triples[-1]['status'] = 'APPROVED'
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
                            original_triples[-1]['status'] = 'APPROVED(NODE_ALL_EXISTS)'
                            approved_triples_node_exist.append(at)
                        approved_triples.append(at)

    df_original_triples = pd.DataFrame(original_triples)
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
    
    # 对可用的三元组去重 (包括严格双侧实体存在的部分)
    df_approved_triples.drop_duplicates(subset=['relation', 'x_id', 'y_id', 'x_type', 'y_type'], inplace=True, keep='first')
    df_approved_triples_node_exist.drop_duplicates(subset=['relation', 'x_id', 'y_id', 'x_type', 'y_type'], inplace=True, keep='first')

    overview.update({
        'approved triples': len(df_approved_triples),  # 可用的三元组数量(去重后)
        'approved triples node exist': len(df_approved_triples_node_exist),  # 可用的三元组数量(双侧节点已存在)(去重后)
    })
    
    if save_df:
        df_original_triples.to_csv(os.path.join('data/data_abstract/original_triples', f'{name}.csv'), index=False)
        df_approved_triples.to_csv(os.path.join('data/data_abstract/approved_triples', f'{name}.csv'), index=False)
        df_approved_triples_node_exist.to_csv(os.path.join('data/data_abstract/approved_triples_node_exist', f'{name}.csv'), index=False)  # 最后可用
    
    return overview
    
for file in os.listdir(result_path):
    with open(os.path.join(result_path, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        overview = parse(data, file, save_df=True)
        ...
