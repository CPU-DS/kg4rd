# -*- coding: utf-8 -*-
# Create Date: 2025/09/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: relation_repo.py
# Description: 关系查询

import os
import pandas as pd
from models.relation_model import Relation, RELA_DIRECTION, MATCH_RELA_TYPE


class RelationRepository:
    def __init__(self):
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
        
    def get_relation_by_node_index(
        self,
        node_index: int,
        direction: RELA_DIRECTION = 'bidirection',
        relation_type: MATCH_RELA_TYPE = 'all',
        hop: int = 1
    ) -> list[Relation]:
        df = self.edges_df
        df_supp = self.edges_supp_df
        if relation_type != 'all':
            df = self.edges_df[self.edges_df['relation'] == relation_type]
            df_supp = self.edges_supp_df[self.edges_supp_df['relation'] == relation_type]
        
        results = []
        match direction:
            case 'in':
                rows: pd.DataFrame = df[df['y_index'] == node_index]  # type: ignore
                rows_supp: pd.DataFrame = df_supp[df_supp['y_index'] == node_index]  # type: ignore
            case 'out':
                rows: pd.DataFrame = df[df['x_index'] == node_index]  # type: ignore
                rows_supp: pd.DataFrame = df_supp[df_supp['x_index'] == node_index]  # type: ignore
            case 'bidirection':
                rows: pd.DataFrame = df.query("x_index == @node_index or y_index == @node_index")  # type: ignore
                rows_supp: pd.DataFrame = df_supp.query("x_index == @node_index or y_index == @node_index")  # type: ignore
        
        for row in rows.itertuples():
            results.append(Relation(
                relation_name=row.relation,  # type: ignore
                x_index=int(row.x_index),  # type: ignore
                x_name=row.x_name,  # type: ignore
                x_type=row.x_type,  # type: ignore
                y_index=int(row.y_index),  # type: ignore
                y_name=row.y_name,  # type: ignore
                y_type=row.y_type,  # type: ignore
                display_relation_name=row.display_relation,  # type: ignore
            ))
        for row in rows_supp.itertuples():
            results.append(Relation(
                relation_name=row.relation,  # type: ignore
                x_index=int(row.x_index),  # type: ignore
                x_name=row.x_name,  # type: ignore
                x_type=row.x_type,  # type: ignore
                y_index=int(row.y_index),  # type: ignore
                y_name=row.y_name,  # type: ignore
                y_type=row.y_type,  # type: ignore
                uid=row.uid,  # type: ignore
            ))
            
        if hop > 1:
            for result in results:
                if result.x_index == node_index:
                    results.extend(self.get_relation_by_node_index(result.y_index, direction, relation_type, hop - 1))
                elif result.y_index == node_index:
                    results.extend(self.get_relation_by_node_index(result.x_index, direction, relation_type, hop - 1))
        
        return list(set(results))
