# -*- coding: utf-8 -*-
# Create Date: 2025/09/08
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: plot.py
# Description: 绘图方法

import matplotlib.pyplot as plt
import pandas as pd
import os
from typing import Optional

plt.rcParams['figure.dpi'] = 150  # 提高图片分辨率
plt.rcParams['font.family'] = 'serif'  # 设置字体

_c = os.path.dirname(__file__)
_primekg_path = os.path.join(_c, '../../../primekg')

_mondo_ref = pd.read_csv(os.path.join(_c, '../../../data/data/mondo/mondo_references.csv')).astype({'mondo_id':int}).astype({'mondo_id':str})

nodes = pd.read_csv(os.path.join(_c, '../kg/nodes.csv'), low_memory=False)
edges = pd.read_csv(os.path.join(_c, '../kg/kg.csv'), low_memory=False)
edges_supplement = pd.read_csv(os.path.join(_c, '../kg/kg_supplement.csv'), low_memory=False)

_all_disease_nodes = nodes.query('node_type == "disease"').copy()
_all_disease_nodes['node_id'] = _all_disease_nodes['node_id'].apply(lambda x: str(x.lstrip('kg4rd:')))

orphanets = pd.merge(_all_disease_nodes, _mondo_ref,'left', left_on='node_id', right_on='mondo_id')[[
    'mondo_id', 'ontology', 'ontology_id', 'node_name', 'node_index'
]].query('ontology == "Orphanet"')

if os.path.exists(_primekg_path):
    primekg_nodes = pd.read_csv(os.path.join(_primekg_path, 'kg/nodes.csv'), low_memory=False)
    primekg_edges = pd.read_csv(os.path.join(_primekg_path, 'kg/kg.csv'), low_memory=False)
    
    _primekg_all_disease_nodes = primekg_nodes.query('node_type == "disease"').copy()
    
    primekg_orphanets = pd.merge(_primekg_all_disease_nodes, _mondo_ref,'left', left_on='node_id', right_on='mondo_id')[[
        'mondo_id', 'ontology', 'ontology_id', 'node_name', 'node_index'
    ]].query('ontology == "Orphanet"')

def plot_degree_distribution(
        nodes: pd.DataFrame,
        edges: pd.DataFrame, 
        node_type: Optional[str] = None,
        relation_type: Optional[str] = None,  # 如果指定了关系类型，实体类型就不用了（关系类型就区分了实体类型）
        in_out: bool = True,  # 是否按出度入度区分 如果指定了关系类型，最好就不要区分出入度了（单向关系只有一边，双向关系两边是一样的）
        threshold: int = 500,
        figsize: tuple = (14, 6),
        fontsize: int = 10,
        figtext_pos: tuple = (0.45, 0.95)
    ):
    
    all_type_nodes = nodes.copy()
    if node_type is not None:
        all_type_nodes = all_type_nodes.query(f'node_type == "{node_type}"')
    all_type_nodes = all_type_nodes[['node_index']].astype({'node_index': int}).astype({'node_index': str})
    
    all_out_edges = edges.copy()
    if relation_type is not None:
        all_out_edges = all_out_edges.query(f'relation == "{relation_type}"')
    if node_type is not None:
        all_out_edges = all_out_edges.query(f'x_type == "{node_type}"')
    out_degree = all_out_edges.groupby('x_index').count()['relation'].reset_index().astype({'x_index': int}).astype({'x_index': str})
    
    out_degree = pd.merge(out_degree, all_type_nodes, left_on='x_index', right_on='node_index', how='right')  # 合并是为了将出度为 0 的实体也包含进来
    out_degree = out_degree[['relation', 'node_index']].fillna(0).astype({'relation': int})
    
    all_in_edges = edges.copy()
    if relation_type is not None:
        all_in_edges = all_in_edges.query(f'relation == "{relation_type}"')
    if node_type is not None:
        all_in_edges = all_in_edges.query(f'y_type == "{node_type}"')
    in_degree = all_in_edges.groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    
    in_degree = pd.merge(in_degree, all_type_nodes, left_on='y_index', right_on='node_index', how='right')
    in_degree = in_degree[['relation', 'node_index']].fillna(0).astype({'relation': int})
    
    if in_out:
        out_degree = out_degree['relation']
        in_degree = in_degree['relation']

        out_threshold = out_degree <= threshold
        in_threshold = in_degree <= threshold

        filtered_out = out_degree[out_threshold]
        filtered_in = in_degree[in_threshold]

        out_filtered_count = (~out_threshold).sum()  # 被过滤的节点数量
        in_filtered_count = (~in_threshold).sum()
        out_filtered_percent = (out_filtered_count / len(out_degree)) * 100
        in_filtered_percent = (in_filtered_count / len(in_degree)) * 100

        plt.figure(figsize=figsize)

        plt.subplot(121)
        plt.hist(filtered_out, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
        plt.grid(True, alpha=0.3)
        plt.title(f'out-degree distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        plt.xlabel('out-degree', fontsize=fontsize)
        plt.ylabel('count', fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.figtext(figtext_pos[0], figtext_pos[1], 
            f'filtered degree > {threshold} ({out_filtered_count} nodes, {out_filtered_percent:.3f}%)\n'
            f'sum = {out_degree.sum()}\n'
            f'mean = {out_degree.mean():.3f}', 
            transform=plt.gca().transAxes, 
            bbox=dict(facecolor='white', alpha=0.8),
            verticalalignment='top',
            fontsize=fontsize
        )

        plt.subplot(122)
        plt.hist(filtered_in, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
        plt.grid(True, alpha=0.3)
        plt.title(f'in-degree distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        plt.xlabel('in-degree', fontsize=fontsize)
        plt.ylabel('count', fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.figtext(figtext_pos[0], figtext_pos[1], 
            f'filtered degree > {threshold} ({in_filtered_count} nodes, {in_filtered_percent:.3f}%)\n'
            f'sum = {in_degree.sum()}\n'
            f'mean = {in_degree.mean():.3f}', 
            transform=plt.gca().transAxes, 
            bbox=dict(facecolor='white', alpha=0.8),
            verticalalignment='top',
            fontsize=fontsize
        )

        plt.tight_layout()  # 调整子图之间的间距
        
    else:
        degree = pd.merge(out_degree, in_degree, on='node_index', how='outer').fillna(0).astype({'relation_x': int}).astype({'relation_y': int})
        degree['degree'] = degree['relation_x'] + degree['relation_y']
        degree = degree['degree']

        degree_threshold = degree <= threshold
        filtered_degree = degree[degree_threshold]
        filtered_degree_count = (~degree_threshold).sum()
        filtered_degree_percent = (filtered_degree_count / len(degree)) * 100
        
        plt.figure(figsize=figsize)
        
        plt.hist(filtered_degree, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
        plt.grid(True, alpha=0.3)
        plt.title(f'degree distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        plt.xlabel('degree', fontsize=fontsize)
        plt.ylabel('count', fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.figtext(figtext_pos[0], figtext_pos[1], 
            f'filtered degree > {threshold} ({filtered_degree_count} nodes, {filtered_degree_percent:.3f}%)\n'
            f'sum = {degree.sum()}\n'
            f'mean = {degree.mean():.3f}', 
            transform=plt.gca().transAxes, 
            bbox=dict(facecolor='white', alpha=0.8),
            verticalalignment='top',
            fontsize=fontsize
        )
        
    plt.show()
