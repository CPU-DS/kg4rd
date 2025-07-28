# -*- coding: utf-8 -*-
# Create Date: 2025/06/12
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: kg2neo4j.py
# Description: 将图谱存入 Neo4j 中

from typing import Dict, Any, Optional

import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm


class Pipeline:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
        
    def delete_all(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def import_nodes(self, node_csv_path: str):
        df = pd.read_csv(node_csv_path)

        with self.driver.session() as session:
            grouped = df.groupby("node_type")
            for node_type, group in tqdm(grouped, total=len(grouped)):
                rows = group.to_dict("records")
                query = f"""
                UNWIND $rows AS row
                CREATE (n:`{node_type}` {{
                    index: row.node_index,
                    name: row.node_name,
                    id: row.node_id,
                    source: row.node_source
                }})
                """
                constraint_query = f"""
                    CREATE CONSTRAINT `unique_{node_type}_index` IF NOT EXISTS FOR (n:`{node_type}`) REQUIRE n.index IS UNIQUE
                """
                session.run(query, rows=rows)
                session.run(constraint_query)

    def import_edges(self):
        

        with self.driver.session() as session:
            query = """
                LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
                MATCH (a {index: toInteger(row.x_index)}), (b {index: toInteger(row.y_index)})
                CREATE (a)-[r:`${row.relation}` {display_relation: row.display_relation}]->(b)
            """
            session.run(query)

if __name__ == "__main__":
    uri = "neo4j://10.4.3.159:7687" 
    user = ''
    password = ''
    
    node_csv_path = 'src/kg4rd/kg/nodes.csv'
    edges_csv_path = ''

    pipe = Pipeline(uri, user, password)
    pipe.delete_all()
    pipe.import_nodes(node_csv_path)
    pipe.import_edges()
    pipe.close()
