# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: entity_repo.py
# Description: 实体查询

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))

from typing import Optional
import pandas as pd
from models.entity_model import EntityDTO, MATCH_MODE, MATCH_NODE_TYPE, Entity
from synonyms.simple_search import *
import json
import re


class EntityRepository:
    def __init__(self):
        self.entity_df = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), 
                '../../../kg/nodes.csv'
            )
        ).astype({'node_index': str})
        
        self.edges_df = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), 
                '../../../kg/kg.csv'
            )
        )
        self.edges_supp_df = pd.read_csv(
            os.path.join(
                os.path.dirname(__file__), 
                '../../../kg/kg_supplement.csv'
            )
        )
        
        def add_prefix(df: pd.DataFrame) -> pd.DataFrame:
            df['id'] = df['id'].apply(lambda x: f'kg4rd:{x}')
            return df
        
        self.df_dis = pd.merge(
            add_prefix(df_dis), 
            self.entity_df[self.entity_df['node_type'] == 'disease'], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        self.df_drug = pd.merge(
            add_prefix(df_drug), 
            self.entity_df[self.entity_df['node_type'] == 'drug'], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        self.df_phe = pd.merge(
            add_prefix(df_phe), 
            self.entity_df[self.entity_df['node_type'] == 'effect/phenotype'], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        self.df_prot = pd.merge(
            add_prefix(df_prot), 
            self.entity_df[self.entity_df['node_type'] == 'gene/protein'], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        self.df_path = pd.merge(
            add_prefix(df_path), 
            self.entity_df[self.entity_df['node_type'] == 'pathway'], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        self.df_go = pd.merge(
            add_prefix(df_go), 
            self.entity_df[
                self.entity_df["node_type"].isin(
                    ["molecular_function", "cellular_component", "biological_process"]
                )
            ], 
            left_on='id', right_on='node_id', how='left'
        ).dropna(subset=['node_index'])
        
        self.df_all = pd.concat([self.df_dis, self.df_drug, self.df_phe, self.df_prot, self.df_path, self.df_go], ignore_index=True)
        
        self.df_disease_mondo = pd.read_csv(os.path.join(
                os.path.dirname(__file__), 
                '../../../../../data/data_feature/disease_mondo.csv'
            ))
        self.df_disease_mondo = add_prefix(
            self.df_disease_mondo[self.df_disease_mondo['definition'].notna()][['mondo_id', 'definition']].rename(columns={'mondo_id': 'id'}) # type: ignore
        )
        
        self.df_disease_ref = pd.read_csv(os.path.join(
            os.path.dirname(__file__),
            '../../../../../data/data/mondo/mondo_references.csv'
        ))
        self.df_disease_ref = add_prefix(
            self.df_disease_ref.astype({'mondo_id': int}).astype({'mondo_id': str}).rename(columns={'mondo_id': 'id'})
        )
        
        self.df_disease_umls = pd.read_csv(os.path.join(
                os.path.dirname(__file__), 
                '../../../../../data/data_feature/disease_umls.csv'
            ))
        self.df_disease_umls = add_prefix(
            self.df_disease_umls[self.df_disease_umls['description'].notna()][['mondo_id', 'description']].rename(columns={'mondo_id': 'id'})  # type: ignore
        )
        
        self.df_drugbank = pd.read_csv(os.path.join(
            os.path.dirname(__file__), 
            '../../../../../data/data_feature/drugbank.csv'
        ))
        self.df_drugbank = add_prefix(
            self.df_drugbank[self.df_drugbank['description'].notna()][['id', 'description']]  # type: ignore
        )
        
        self.go = pd.read_csv(os.path.join(
            os.path.dirname(__file__), 
            '../../../../../data/data_feature/go.csv'
        ))
        self.go = add_prefix(
            self.go[self.go['def'].notna()][['id', 'def']]  # type: ignore
        )
        
        self.hpo = pd.read_csv(os.path.join(
            os.path.dirname(__file__), 
            '../../../../../data/data_feature/hpo.csv'
        ))
        self.hpo = add_prefix(
            self.hpo[self.hpo['def'].notna()][['id', 'def']]  # type: ignore
        )
        
        
    def get_entity_dto_by_index(
        self,
        node_index: str,
        node_type: MATCH_NODE_TYPE = 'all',
        match_mode: MATCH_MODE = 'strict',
        limit: Optional[int] = None
    ) -> list[EntityDTO]:
        df = self.entity_df
        if node_type != 'all':
            df: pd.DataFrame = df[df['node_type'] == node_type]  # type: ignore
        match match_mode:
            case 'strict':
                rows = df[df['node_index'] == str(node_index)]
            case 'contains':
                rows = df[df['node_index'].str.contains(str(node_index), na=False)]
            case 'prefix':
                rows = df[df['node_index'].str.startswith(str(node_index), na=False)]
            case 'regex':
                rows = df[df['node_index'].str.match(str(node_index), na=False)]
        
        if limit:
            rows = rows.head(limit)
        return [
            EntityDTO(
                node_index=int(row.node_index),  # type: ignore
                node_name=row.node_name,  # type: ignore
                node_type=row.node_type  # type: ignore
            )
            for row in rows.itertuples()
        ]

    def get_entity_dto_by_name(
        self,
        node_name: str,
        node_type: MATCH_NODE_TYPE = 'all',
        match_mode: MATCH_MODE = 'strict',
        limit: Optional[int] = None
    ) -> list[EntityDTO]:
        match node_type:
            case 'all':
                df = self.df_all
            case 'disease':
                df = self.df_dis
            case 'drug':
                df = self.df_drug
            case 'effect/phenotype':
                df = self.df_phe
            case 'gene/protein':
                df = self.df_prot
            case 'pathway':
                df = self.df_path
            case 'molecular_function' | 'cellular_component' | 'biological_process':
                df = self.df_go

        node_name = node_name.lower()
        match match_mode:
            case 'strict':
                rows = df[df['name'] == node_name]
            case 'contains':
                rows = df[df['name'].str.contains(node_name, na=False)]
            case 'prefix':
                rows = df[df['name'].str.startswith(node_name, na=False)]
            case 'regex':
                rows = df[df['name'].str.match(node_name, na=False)]
        
        if limit:
            rows = rows.head(limit)
        return [
            EntityDTO(
                node_index=int(row.node_index),  # type: ignore
                node_name=row.name,  # type: ignore
                node_type=row.node_type  # type: ignore
            )
            for row in rows.itertuples()
        ]

    def get_entity_by_index(
        self,
        node_index: int
    ) -> Optional[Entity]:
        rows = self.entity_df[self.entity_df['node_index'] == str(node_index)]
        if rows.empty:
            return None
        row = rows.iloc[0]
        entity = Entity(
            node_index=int(row.node_index),  # type: ignore
            node_id=row.node_id,  # type: ignore
            node_name=row.node_name,  # type: ignore
            node_type=row.node_type,  # type: ignore
            node_source=row.node_source  # type: ignore
        )
        
        match entity.node_type:
            case 'disease':
                entity.node_properties = {
                    'definition': self.df_disease_mondo[self.df_disease_mondo['id'] == entity.node_id]['definition'].iloc[0],  # type: ignore
                    'description': self.df_disease_umls[self.df_disease_umls['id'] == entity.node_id]['description'].iloc[0],  # type: ignore
                }
                rows = self.df_disease_ref[self.df_disease_ref['id'] == entity.node_id]
                for row in rows.itertuples():
                    match row.ontology:  # type: ignore
                        case 'MESH':
                            entity.node_source_url.append({
                                'name': f'{row.ontology}',  # type: ignore
                                'url': f'https://meshb.nlm.nih.gov/record/ui?ui={row.ontology_id}'  # type: ignore
                            })
                        case 'Orphanet':
                            entity.node_source_url.append({
                                'name': f'{row.ontology}',  # type: ignore
                                'url': f'https://www.orpha.net/en/disease/detail/{row.ontology_id}'  # type: ignore
                            })
                        case 'PMID':
                            entity.node_source_url.append({
                                'name': f'{row.ontology}',  # type: ignore
                                'url': f'https://pubmed.ncbi.nlm.nih.gov/{row.ontology_id}'  # type: ignore
                            })
                        case 'Wikipedia':
                            entity.node_source_url.append({
                                'name': f'{row.ontology}',  # type: ignore
                                'url': f'https://en.wikipedia.org/wiki/{row.ontology_id}'  # type: ignore
                            })

            case 'drug':
                entity.node_properties = {
                    'description': self.df_drugbank[self.df_drugbank['id'] == entity.node_id]['description'].iloc[0],  # type: ignore
                }
                entity.node_source_url = [{
                    'name': 'DrugBank',
                    'url': f'https://go.drugbank.com/drugs/{entity.node_id.split(":")[1]}'
                }]
            case 'gene/protein':
                ncbi_id = int(entity.node_id.split(":")[1])
                path = f'/home/wangtao/gene/{ncbi_id}/data_report.jsonl'
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        data_report = json.load(f)
                        desc = data_report.get('summary', [{}])[0].get('description', None)
                        desc = re.sub(r'\[.*?\]', '', desc) if desc else None
                    if desc:
                        entity.node_properties = {
                            'description': desc
                        }
                entity.node_source_url = [{
                    'name': 'NCBI Gene',
                    'url': f'https://www.ncbi.nlm.nih.gov/gene/{ncbi_id}'
                }]
            case 'molecular_function' | 'biological_process' | 'cellular_component':
                entity.node_properties = {
                    'definition': self.go[self.go['id'] == entity.node_id]['def'].iloc[0],  # type: ignore
                }
                entity.node_source_url = [{
                    'name': 'GO',
                    'url': f'https://amigo.geneontology.org/amigo/term/GO:{entity.node_id.split(":")[1].zfill(7)}'
                }]
            case 'effect/phenotype':
                entity.node_properties = {
                    'definition': self.hpo[self.hpo['id'] == entity.node_id]['def'].iloc[0],  # type: ignore
                }
                entity.node_source_url = [{
                    'name': 'HPO',
                    'url': f'https://hpo.jax.org/browse/term/HP:{entity.node_id.split(":")[1].zfill(7)}'
                }]
            case 'pathway':
                if entity.node_source == 'REACTOME':
                    entity.node_source_url = [{
                        'name': 'REACTOME',
                        'url': f'https://reactome.org/content/detail/{entity.node_id.split(":")[1]}'
                    }]
                elif entity.node_source == 'KEGG':
                    entity.node_source_url = [{
                        'name': 'KEGG',
                        'url': f'https://www.kegg.jp/pathway/{entity.node_id.split(":")[1]}'
                    }]
        
        return entity
