# -*- coding: utf-8 -*-
# Create Date: 2025/06/12
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: kg2neo4j.py
# Description: 将图谱存入 Neo4j 中

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

    def import_edges(self, 
            edges_csv_path: str, 
            batch_size: int = 1000):
        df = pd.read_csv(edges_csv_path).sample(frac=1).reset_index(drop=True)  # 打乱
        
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size)):
                batch = df.iloc[i:i+batch_size]
                grouped_batch = batch.groupby('relation')
                
                for relation_type, group in grouped_batch:
                    
                    x_types = group['x_type'].unique()
                    y_types = group['y_type'].unique()

                    for x_type in x_types:
                        for y_type in y_types:
                            subset = group[(group['x_type'] == x_type) & (group['y_type'] == y_type)]
                            if len(subset) == 0:
                                continue

                            subset_rows = subset.to_dict("records")
                            
                            query = """
                            UNWIND $rows AS row
                            MERGE (x:`""" + x_type + """` {index: row.x_index})
                            ON CREATE SET x.name = row.x_name, 
                                            x.oid = row.x_id, 
                                            x.source = row.x_source
                            MERGE (y:`""" + y_type + """` {index: row.y_index})
                            ON CREATE SET y.name = row.y_name, 
                                            y.oid = row.y_id, 
                                            y.source = row.y_source
                            CREATE (x)-[r:`""" + relation_type + """` {
                                display_name: row.display_relation
                            }]->(y)
                            """
                            
                            session.run(query, rows=subset_rows)

if __name__ == "__main__":
    uri = "neo4j://10.4.3.159:7687" 
    user = ''
    password = ''
    
    edges_csv_path = 'src/kg4rd/kg/kg.csv'

    pipe = Pipeline(uri, user, password)
    pipe.delete_all()
    pipe.import_edges(edges_csv_path, batch_size=20000)
    pipe.close()