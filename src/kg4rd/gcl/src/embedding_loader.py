# -*- coding: utf-8 -*-
# Create Date: 2025/08/01
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: embedding_loader.py
# Description: 预嵌入导入

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch


class NodeEmbeddingLoader:
    def __init__(self, data_dir: str = '/home/wangtao/src/kg4rd/data/data_feature'):
        self.data_dir = data_dir
        self.node_types = {
            'gene/protein': ['gene_desc_embed.npz', 'protein_seq_embed.npz', 'gene_seq_embed.npz'],
            'disease': ['disease_def_embed.npz', 'disease_desc_embed.npz'],
            'drug': ['drug_desc_embed.npz', 'drug_seq_embed.npz', 'drug_smiles_embed.npz'],
            'biological_process': ['go_def_embed.npz'],
            'cellular_component': ['go_def_embed.npz'],
            'molecular_function': ['go_def_embed.npz'],
            'effect/phenotype': ['hpo_def_embed.npz'],
            'pathway': []
        }
        
    def load_embedding_file(self, filename: str) -> tuple[list[int], np.ndarray]:
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return [], np.array([])
        
        data = np.load(filepath)
        ids = data['ids'].tolist()
        embeddings = data['embeddings']
        return ids, embeddings

    def load_node_embeddings(self, nodes: pd.DataFrame, device: str) -> tuple[dict[int, dict[str, torch.Tensor]], dict[str, int]]:
        node_embeddings = {}
        type_dims = {}
        
        for node_type, embedding_files in self.node_types.items():  # node_type: [...]
                
            type_nodes = nodes[nodes['node_type'] == node_type]
            
            for embed_file in embedding_files:  # 多个嵌入文件
                ids, embeddings = self.load_embedding_file(embed_file)
                id_to_embedding = dict(zip(ids, embeddings))  # { int: array(embedding_dim) }
                
                embed_type = embed_file.replace('_embed.npz', '')

                for _, node_row in tqdm(type_nodes.iterrows(), total=type_nodes.shape[0], desc=f"{node_type}:{embed_file}"):  # 该类型下的所有 node
                    node_index = node_row['node_index']
                    actual_id = int(str(node_row['node_id']).split(':')[1].replace('DB', ''))  # node_id 都是 kg4rd:id 的格式 (drug 带 DB 前缀, 只有这里要额外处理)
                    
                    if actual_id in id_to_embedding:
                        if node_index not in node_embeddings:
                            node_embeddings[node_index] = {}
                        embedding = id_to_embedding[actual_id]
                        node_embeddings[node_index][embed_type] = torch.tensor(embedding, dtype=torch.float32).to(device)
                        
                        if embed_type not in type_dims:
                            type_dims[embed_type] = embedding.shape[0]

        return node_embeddings, type_dims  # {node_index: {embedding_type: embedding}} 不包含 pathway | {embedding_type: embedding_dim}
