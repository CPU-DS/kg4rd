# -*- coding: utf-8 -*-
# Create Date: 2025/09/08
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: lib.py
# Description: 公共方法

import matplotlib.pyplot as plt
import pandas as pd

nodes = pd.read_csv('../kg/nodes.csv', low_memory=False)

_ref = pd.read_csv('../../../data/data/mondo/mondo_references.csv').astype({'mondo_id':int}).astype({'mondo_id':str})
_all_disease_nodes = nodes.query('node_type == "disease"').copy()
_all_disease_nodes['node_id'] = _all_disease_nodes['node_id'].apply(lambda x: str(x.lstrip('kg4rd:')))    

orphanets = pd.merge(_all_disease_nodes, _ref,'left', left_on='node_id', right_on='mondo_id')[[
    'mondo_id', 'ontology', 'ontology_id', 'node_name', 'node_index'
]].query('ontology == "Orphanet"')

def plot_degree_distribution(nodes: pd.DataFrame, edges: pd.DataFrame, type_: str, threshold: int = 500):
    
    plt.rcParams['figure.dpi'] = 150  # 提高图片分辨率
    plt.rcParams['font.family'] = 'serif'  # 设置字体

    all_type_nodes = nodes.query(f'node_type == "{type_}"')[['node_index']].astype({'node_index': int}).astype({'node_index': str})

    out_degree = edges.query(f'x_type == "{type_}"').groupby('x_index').count()['relation'].reset_index().astype({'x_index': int}).astype({'x_index': str})
    out_degree = pd.merge(out_degree, all_type_nodes, left_on='x_index', right_on='node_index', how='right')
    out_degree = out_degree[['relation', 'node_index']].fillna(0).astype({'relation': int})
    out_degree = out_degree['relation']
    
    in_degree = edges.query(f'y_type == "{type_}"').groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    in_degree = pd.merge(in_degree, all_type_nodes, left_on='y_index', right_on='node_index', how='right')
    in_degree = in_degree[['relation', 'node_index']].fillna(0).astype({'relation': int})
    in_degree = in_degree['relation']

    out_threshold = out_degree <= threshold
    in_threshold = in_degree <= threshold

    filtered_out = out_degree[out_threshold]
    filtered_in = in_degree[in_threshold]

    out_filtered_count = (~out_threshold).sum()  # 被过滤的节点数量
    in_filtered_count = (~in_threshold).sum()
    out_filtered_percent = (out_filtered_count / len(out_degree)) * 100
    in_filtered_percent = (in_filtered_count / len(in_degree)) * 100

    plt.figure(figsize=(14, 6))

    plt.subplot(121)
    plt.hist(filtered_out, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'Out-degree Distribution for {type_}', fontsize=10)
    plt.xlabel('Out-degree')
    plt.ylabel('Count')
    plt.figtext(0.45, 0.95, 
        f'Filtered degree > {threshold} ({out_filtered_count} nodes, {out_filtered_percent:.3f}%)\n'
        f'Sum = {out_degree.sum()}\n'
        f'Mean = {out_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.subplot(122)
    plt.hist(filtered_in, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'In-degree Distribution for {type_}', fontsize=10)
    plt.xlabel('In-degree')
    plt.ylabel('Count')
    plt.figtext(0.45, 0.95, 
        f'Filtered degree > {threshold} ({in_filtered_count} nodes, {in_filtered_percent:.3f}%)\n'
        f'Sum = {in_degree.sum()}\n'
        f'Mean = {in_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.tight_layout()
    plt.show()

  
def plot_node_relation_distribution(nodes: pd.DataFrame, edges: pd.DataFrame, threshold: int = 500):
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['font.family'] = 'serif'


    head_relation = edges.groupby(['x_index', 'relation']).count().reset_index()['y_index']
    head_relation_threshold = head_relation <= threshold
    head_relation_filtered = head_relation[head_relation_threshold]

    tail_relation = edges.groupby(['y_index', 'relation']).count().reset_index()['x_index']
    tail_relation_threshold = tail_relation <= threshold
    tail_relation_filtered = tail_relation[tail_relation_threshold]

    head_relation_filtered_count = (~head_relation_threshold).sum()
    head_filtered_percent = (head_relation_filtered_count / len(head_relation)) * 100

    tail_relation_filtered_count = (~tail_relation_threshold).sum()
    tail_filtered_percent = (tail_relation_filtered_count / len(tail_relation)) * 100

    plt.figure(figsize=(14, 6))

    plt.subplot(121)
    plt.hist(head_relation_filtered, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title('Number Distribution of Tail Entity for Each Relation Head Entity Pair', fontsize=10)
    plt.xlabel('Number')
    plt.ylabel('Count')
    plt.text(0.35, 0.95, 
        f'Total = {len(head_relation)}\n'
        f'Filtered number > {threshold} ({head_relation_filtered_count} pair, {head_filtered_percent:.3f}%)\n'
        f'Mean = {head_relation.mean():.3f}\n'
        f'Max = {head_relation.max()}\n'
        f'Min = {head_relation.min()}\n'
        f'Middle = {head_relation.median():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.subplot(122)
    plt.hist(tail_relation_filtered, bins=20, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title('Number Distribution of Head Entity for Each Relation Tail Entity Pair', fontsize=10)
    plt.xlabel('Number')
    plt.ylabel('Count')
    plt.text(0.35, 0.95, 
        f'Total = {len(tail_relation)}\n'
        f'Filtered number > {threshold} ({tail_relation_filtered_count} pair, {tail_filtered_percent:.3f}%)\n'
        f'Mean = {tail_relation.mean():.3f}\n'
        f'Max = {tail_relation.max()}\n'
        f'Min = {tail_relation.min()}\n'
        f'Middle = {tail_relation.median():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )
    
    plt.show()
    

def plot_drug_disease_distribution(nodes: pd.DataFrame, drug_disease: pd.DataFrame, threshold: int = 50):
    
    all_disease = nodes.query('node_type == "disease"')[['node_index']].astype({'node_index': int}).astype({'node_index': str})

    # 尾实体必定为 disease 只能计算 in degree
    drug_disease_indication_in_degree = drug_disease.query('relation == "indication"').groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    df = pd.merge(drug_disease_indication_in_degree, all_disease, how="right", left_on='y_index', right_on='node_index')
    df = df[['relation', 'node_index']].fillna(0).astype({'relation': int})
    disease_indication_in_degree = df['relation']

    indication = disease_indication_in_degree <= threshold
    filtered_indication = disease_indication_in_degree[indication]
    filtered_indication_count = (~indication).sum()
    filtered_indication_percent = (filtered_indication_count / len(disease_indication_in_degree)) * 100

    drug_disease_olu_in_degree = drug_disease.query('relation == "off-label use"').groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    df = pd.merge(drug_disease_olu_in_degree, all_disease, how="right", left_on='y_index', right_on='node_index')
    df = df[['relation', 'node_index']].fillna(0).astype({'relation': int})
    disease_olu_in_degree = df['relation']

    olu = disease_olu_in_degree <= threshold
    filtered_olu = disease_olu_in_degree[olu]
    filtered_olu_count = (~olu).sum()
    filtered_olu_percent = (filtered_olu_count / len(disease_olu_in_degree)) * 100

    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['font.family'] = 'serif'

    plt.figure(figsize=(14, 6))

    plt.subplot(121)
    plt.hist(filtered_indication, bins=10, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'In-degree Distribution for disease (drug indication)', fontsize=10)
    plt.xlabel('In-degree')
    plt.ylabel('Count')
    plt.figtext(0.45, 0.95,
        f'Filtered degree > {threshold} ({filtered_indication_count} nodes, {filtered_indication_percent:.3f}%)\n'
        f'Sum = {disease_indication_in_degree.sum()}\n'
        f'Mean = {disease_indication_in_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.subplot(122)
    plt.hist(filtered_olu, bins=10, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'In-degree Distribution for disease (drug off-label use)', fontsize=10)
    plt.xlabel('In-degree')
    plt.ylabel('Count')

    plt.figtext(0.45, 0.95,
        f'Filtered degree > {threshold} ({filtered_olu_count} nodes, {filtered_olu_percent:.3f}%)\n'
        f'Sum = {disease_olu_in_degree.sum()}\n'
        f'Mean = {disease_olu_in_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.tight_layout()
    plt.show()


def plot_drug_orphanet_disease_distribution(orphanets: pd.DataFrame, drug_disease: pd.DataFrame, threshold: int = 50):

    all_rare_disease = orphanets[['node_index']].astype({'node_index': int}).astype({'node_index': str})

    drug_disease_indication_in_degree = drug_disease.query('relation == "indication"').groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    df = pd.merge(drug_disease_indication_in_degree, all_rare_disease, how="right", left_on='y_index', right_on='node_index')
    df = df[['relation', 'node_index']].fillna(0).astype({'relation': int})
    disease_indication_in_degree = df['relation']

    indication = disease_indication_in_degree <= threshold
    filtered_indication = disease_indication_in_degree[indication]
    filtered_indication_count = (~indication).sum()
    filtered_indication_percent = (filtered_indication_count / len(disease_indication_in_degree)) * 100

    drug_disease_olu_in_degree = drug_disease.query('relation == "off-label use"').groupby('y_index').count()['relation'].reset_index().astype({'y_index': int}).astype({'y_index': str})
    df = pd.merge(drug_disease_olu_in_degree, all_rare_disease, how="right", left_on='y_index', right_on='node_index')
    df = df[['relation', 'node_index']].fillna(0).astype({'relation': int})
    disease_olu_in_degree = df['relation']

    olu = disease_olu_in_degree <= threshold
    filtered_olu = disease_olu_in_degree[olu]
    filtered_olu_count = (~olu).sum()
    filtered_olu_percent = (filtered_olu_count / len(disease_olu_in_degree)) * 100

    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['font.family'] = 'serif'

    plt.figure(figsize=(14, 6))

    plt.subplot(121)
    plt.hist(filtered_indication, bins=10, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'In-degree Distribution for rare disease (drug indication)', fontsize=10)
    plt.xlabel('In-degree')
    plt.ylabel('Count')
    plt.figtext(0.5, 0.95,
        f'Filtered degree > {threshold} ({filtered_indication_count} nodes, {filtered_indication_percent:.3f}%)\n'
        f'Sum = {disease_indication_in_degree.sum()}\n'
        f'Mean = {disease_indication_in_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.subplot(122)
    plt.hist(filtered_olu, bins=10, alpha=0.7, color='#3498db', edgecolor='#2980b9', linewidth=1)
    plt.grid(True, alpha=0.3)
    plt.title(f'In-degree Distribution for rare disease (drug off-label use)', fontsize=10)
    plt.xlabel('In-degree')
    plt.ylabel('Count')

    plt.figtext(0.5, 0.95,
        f'Filtered degree > {threshold} ({filtered_olu_count} nodes, {filtered_olu_percent:.3f}%)\n'
        f'Sum = {disease_olu_in_degree.sum()}\n'
        f'Mean = {disease_olu_in_degree.mean():.3f}', 
        transform=plt.gca().transAxes, 
        bbox=dict(facecolor='white', alpha=0.8),
        verticalalignment='top'
    )

    plt.tight_layout()
    plt.show()

__all__ = [
    'plot_degree_distribution',
    'plot_node_relation_distribution',
    'plot_drug_disease_distribution',
    'plot_drug_orphanet_disease_distribution',
    'nodes',
    'orphanets',
]
