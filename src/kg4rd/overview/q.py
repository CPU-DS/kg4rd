# -*- coding: utf-8 -*-
# Create Date: 2025/09/08
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: plot.py
# Description: 绘图方法

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from typing import Optional

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 200
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 20
plt.rcParams['mathtext.fontset'] = 'stix'

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
]].query('ontology == "Orphanet"').drop_duplicates(['node_index'], keep='first')

edges_orphanets = edges.query('x_index in @orphanets["node_index"] or y_index in @orphanets["node_index"]')

if os.path.exists(_primekg_path):
    primekg_nodes = pd.read_csv(os.path.join(_primekg_path, 'kg/nodes.csv'), low_memory=False)
    primekg_edges = pd.read_csv(os.path.join(_primekg_path, 'kg/kg.csv'), low_memory=False)
    
    _primekg_all_disease_nodes = primekg_nodes.query('node_type == "disease"').copy()
    
    primekg_orphanets = pd.merge(_primekg_all_disease_nodes, _mondo_ref,'left', left_on='node_id', right_on='mondo_id')[[
        'mondo_id', 'ontology', 'ontology_id', 'node_name', 'node_index'
    ]].query('ontology == "Orphanet"').drop_duplicates(['node_index'], keep='first')
    primekg_edges_orphanets = primekg_edges.query('x_index in @primekg_orphanets["node_index"] or y_index in @primekg_orphanets["node_index"]')

def _calculate_gini_coefficient(x):
    x = np.array(x)
    # 去除0值（度数为0的节点不参与计算）
    x = x[x > 0]
    if len(x) == 0:
        return 0.0
    
    # 排序
    sorted_x = np.sort(x)
    n = len(x)
    
    # 计算基尼系数
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_x)) / (n * np.sum(sorted_x)) - (n + 1) / n
    
    return gini

def plot_degree_distribution(
        nodes: pd.DataFrame,
        edges: pd.DataFrame, 
        node_type: Optional[str] = None,
        relation_type: Optional[str] = None,  # 如果指定了关系类型，实体类型就不用了（关系类型就区分了实体类型）
        in_out: bool = True,  # 是否按出度入度区分 如果指定了关系类型，最好就不要区分出入度了（单向关系只有一边，双向关系两边是一样的）
        threshold: int = 500,
        figsize: tuple = (14, 6),
        fontsize: int = 10,
        figtext_pos: Optional[tuple] = (0.45, 0.95),
        linewidth: float = 1,
        bins: int = 25,
        save_path: Optional[str] = None
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
        
        out_gini = _calculate_gini_coefficient(out_degree)
        in_gini = _calculate_gini_coefficient(in_degree)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        ax1.hist(filtered_out, bins=bins, alpha=0.6, color='#3498db', edgecolor='white', linewidth=linewidth)
        ax1.set_title(f'out-degree distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        ax1.set_xlabel('out-degree', fontsize=fontsize)
        ax1.set_ylabel('frequency', fontsize=fontsize)
        ax1.tick_params(axis='both', labelsize=fontsize)
        if figtext_pos is not None:
            ax1.text(figtext_pos[0], figtext_pos[1], 
                f'filtered degree > {threshold} ({out_filtered_count} nodes, {out_filtered_percent:.3f}%)\n'
                f'sum = {out_degree.sum()}\n'
                f'mean = {out_degree.mean():.3f}\n'
                f'gini coefficient = {out_gini:.3f}', 
                transform=ax1.transAxes, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='0.8'),
                verticalalignment='top',
                fontsize=fontsize
            )

        ax2.hist(filtered_in, bins=bins, alpha=0.6, color='#3498db', edgecolor='white', linewidth=linewidth)
        ax2.set_title(f'in-degree distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        ax2.set_xlabel('in-degree', fontsize=fontsize)
        ax2.set_ylabel('frequency', fontsize=fontsize)
        ax2.tick_params(axis='both', labelsize=fontsize)
        if figtext_pos is not None:
            ax2.text(figtext_pos[0], figtext_pos[1], 
                f'filtered degree > {threshold} ({in_filtered_count} nodes, {in_filtered_percent:.3f}%)\n'
                f'sum = {in_degree.sum()}\n'
                f'mean = {in_degree.mean():.3f}\n'
                f'gini coefficient = {in_gini:.3f}', 
                transform=ax2.transAxes, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='0.8'),
                verticalalignment='top',
                fontsize=fontsize
            )

        plt.tight_layout()
        
    else:
        degree = pd.merge(out_degree, in_degree, on='node_index', how='outer').fillna(0).astype({'relation_x': int}).astype({'relation_y': int})
        degree['degree'] = degree['relation_x'] + degree['relation_y']
        degree = degree['degree']

        degree_threshold = degree <= threshold
        filtered_degree = degree[degree_threshold]
        filtered_degree_count = (~degree_threshold).sum()
        filtered_degree_percent = (filtered_degree_count / len(degree)) * 100

        degree_gini = _calculate_gini_coefficient(degree)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.hist(filtered_degree, bins=bins, alpha=0.6, color='#3498db', edgecolor='white', linewidth=linewidth)
        ax.set_title(f'Degree Distribution {"" if node_type is None else f"for {node_type}"}', fontsize=fontsize)
        ax.set_xlabel('Degree', fontsize=fontsize)
        ax.set_ylabel('Frequency', fontsize=fontsize)
        ax.tick_params(axis='both', labelsize=fontsize)
        if figtext_pos is not None:
            ax.text(figtext_pos[0], figtext_pos[1], 
                f'Filtered degree > {threshold} ({filtered_degree_count} nodes, {filtered_degree_percent:.3f}%)\n'
                f'Sum = {degree.sum()}\n'
                f'Mean = {degree.mean():.3f}\n'
                f'Gini Coefficient = {degree_gini:.3f}', 
                transform=ax.transAxes, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='0.8', alpha=0.8),
                verticalalignment='top',
                fontsize=fontsize
            )
        
    if save_path is not None:
        plt.savefig(save_path, bbox_inches='tight', facecolor='white', dpi=300, pil_kwargs={'compression': 'tiff_lzw'})
    plt.show()

if __name__ == '__main__':
    plot_degree_distribution(
        nodes, edges, 
        in_out=False, 
        bins=50, 
        fontsize=12,
        threshold=200, 
        figsize=(10, 6), 
        figtext_pos=(0.6, 0.96),
        save_path='degree_distribution.tif'
    )
