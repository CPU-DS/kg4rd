# -*- coding: utf-8 -*-
# Create Date: 2025/06/12
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: kg2neo4j.py
# Description: 将图谱存入 Neo4j 中

from typing import Dict, Any
from loguru import logger

import pandas as pd
from neo4j import GraphDatabase


class KG2Neo4j:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
        
    def delete_all(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_constraints(self):
        with self.driver.session() as session:
            def create_constraint_if_not_exists(tx, label: str):
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:`{label}`) REQUIRE n.index IS UNIQUE"
                tx.run(query)
            
            node_types = set(self.df['x_type'].unique()) | set(self.df['y_type'].unique())
            
            for node_type in node_types:
                session.execute_write(create_constraint_if_not_exists, node_type)

    def import_node(self, tx, node_data: Dict[str, Any]):
        query = """
        MERGE (n:`{node_type}` {{index: $index}})
        SET n.id = $id,
            n.name = $name,
            n.source = $source
        RETURN n
        """.format(node_type=node_data['type'])
        
        params = {
            'index': node_data['index'],
            'id': node_data['id'],
            'name': node_data['name'],
            'source': node_data['source']
        }
        result = tx.run(query, **params)
        return result.single()[0]

    def create_relationship(self, tx, start_node_index: str, end_node_index: str, rel_type: str, display_relation: str):
        query = """
        MATCH (start:`{start_type}` {{index: $start_index}})
        MATCH (end:`{end_type}` {{index: $end_index}})
        MERGE (start)-[r:`{rel_type}`]-(end)
        SET r.display_relation = $display_relation
        """.format(
            start_type=tx.start_type,
            end_type=tx.end_type,
            rel_type=rel_type
        )
        
        tx.run(query, 
               start_index=start_node_index,
               end_index=end_node_index,
               display_relation=display_relation)

    def import_kg(self, csv_path: str):
        logger.info(f"import kg from {csv_path}")
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path, low_memory=False)
        
        self.create_constraints()
        
        with self.driver.session() as session:
            total_rows = len(self.df)
            for idx, row in self.df.iterrows():
                def import_transaction(tx):
                    tx.start_type = row['x_type']
                    tx.end_type = row['y_type']
                    
                    start_node_data = {
                        'index': str(row['x_index']),
                        'id': row['x_id'],
                        'type': row['x_type'],
                        'name': row['x_name'],
                        'source': row['x_source']
                    }
                    
                    end_node_data = {
                        'index': str(row['y_index']),
                        'id': row['y_id'],
                        'type': row['y_type'],
                        'name': row['y_name'],
                        'source': row['y_source']
                    }
                    
                    self.import_node(tx, start_node_data)
                    self.import_node(tx, end_node_data)
                    
                    self.create_relationship(
                        tx,
                        str(row['x_index']),
                        str(row['y_index']),
                        row['relation'],
                        row['display_relation']
                    )
                
                session.execute_write(import_transaction)
                if (idx + 1) % 1000 == 0:
                    logger.info(f"processed {idx + 1}/{total_rows} records")
                
        logger.success("kg imported successfully")


if __name__ == "__main__":
    uri = "neo4j://10.4.3.159:7687" 
    user = None
    password = None
    
    csv_path = 'primekg/kg/kg.csv'
    
    importer = KG2Neo4j(uri, user, password)
    importer.delete_all()
    importer.import_kg(csv_path)
    importer.close()
