# -*- coding: utf-8 -*-
# Create Date: 2025/06/03
# Author: houfengzhen
# File Name: extract.py
# Description: 从 PubMed 中提取三元组

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import json
import json5
import time
from typing import Optional
import os
from loguru import logger
from shortuuid import uuid

from llm import LLM

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

with open('src/kg4rd/extractor/system_prompt.txt', 'rt', encoding='utf-8') as fp:
    system_prompt = fp.read()

with open('src/kg4rd/extractor/prompt.md', 'rt', encoding='utf-8') as fp:
    prompt = fp.read()
    
with open('src/kg4rd/extractor/definition_of_node_type.txt', 'rt', encoding='utf-8') as fp:
    node_type = fp.read()

with open('src/kg4rd/extractor/examples.json', 'r', encoding='utf-8') as f:
    examples = json5.load(f)

with open('src/kg4rd/extractor/disease_subheadings_to_relation.json5', 'r', encoding='utf-8') as f:
    disease_subheadings_to_relation = json5.load(f)

with open('src/kg4rd/extractor/definition_of_relations.json5', 'r', encoding='utf-8') as f:
    definition_of_relations = json5.load(f)
        
orphanet_mesh = pd.read_csv('data/data/orphanet/orphanet_mesh.csv')


def extract_subheadings(heading, mesh_terms):
    if pd.isna(mesh_terms) or not mesh_terms:
        return []

    terms = [term.strip() for term in mesh_terms.split(';') if term.strip()]
    
    subheadings = []
    for term in terms:
        if term.strip().startswith(heading) and "/" in term:
            subheading = term.split("/", 1)[1].strip()
            subheadings.append(subheading)
    
    return subheadings

def get_relations_from_subheadings(subheadings, disease_subheadings_to_relation):
    all_relations = set()
    
    for subheading in subheadings:
        if subheading in disease_subheadings_to_relation:
            relations = disease_subheadings_to_relation[subheading]
            all_relations.update(relations)
    
    return all_relations

def get_filled_prompt(
    abstract,
    relations_with_definitions, 
    prompt, 
    examples:Optional[list[dict]]=None
):
    full_prompt = f"""{prompt}

# Input Data
## Pre-defined Node types
{node_type}

## Pre-defined Relationships:
{relations_with_definitions}
"""
        
    if examples:
        full_prompt += f"""

# Examples
"""     
        for i, example in enumerate(examples):
            full_prompt += f"""

## Example {i+1}

### Abstract Text
{example.get('abstract_text', '')}

### Output Data
{json.dumps(example.get('output_data', []), indent=2, ensure_ascii=False)}
"""

    full_prompt += f"""

## Abstract Text (Requested)
{abstract}

# Output Data
"""
    return full_prompt


def extract(llm: LLM, mesh_id: str, max_abs: int = 300):
    
    heading = orphanet_mesh.query('mesh == @mesh_id')['mesh_name'].values[0]
    csv_path = f'data/data_abstract/{mesh_id}.csv'
    if not os.path.exists(csv_path):
        logger.error(f"CSV file for {mesh_id} does not exist: {csv_path}")
        return
    df = pd.read_csv(f'data/data_abstract/{mesh_id}.csv') 
    save_file = f'data/data_abstract/result/{mesh_id}.json'

    if os.path.exists(save_file):
        with open(save_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    for idx, row in df.head(max_abs).iterrows():
        logger.info(f"处理 {mesh_id}: {heading} 第 {idx}/{len(df)}条")
        
        if any(item['index'] == idx for item in results):
            continue
        
        abstract = row['abstract']
        mesh_terms = row['mesh_terms']        
           
        subheadings = extract_subheadings(heading, mesh_terms)
        relations = get_relations_from_subheadings(subheadings, disease_subheadings_to_relation)

        relation_definitions = []
        for i, relation in enumerate(relations):
            definition = definition_of_relations[relation]
            relation_definitions.append(f"{(i+1)}.{relation}: {definition}")
        
        relations_with_definitions = "\n".join(relation_definitions)
        full_prompt = get_filled_prompt(abstract, relations_with_definitions, prompt, examples)      

        try:
            extracted_relations = llm.extract_relations(system_prompt, full_prompt, list(relations))
        except Exception as e:
            raise e
        else:
            for r in extracted_relations:
                r['uid'] = f'{mesh_id}:{row["pmid"]}:{str(uuid())}'
            results.append({
                'pmid': row['pmid'],
                'index': idx,
                'title': row.get('title', ''),
                'heading': heading,
                'mesh_terms':subheadings,
                'abstract': abstract,
                'extracted_relations': extracted_relations,
                'relation_choices': list(relations)
            })
        finally:
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        
        time.sleep(2)

    with open(save_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    gemini = LLM.get_llm('gemini')
    max_abs = 200
    print(f'最大摘要数量: {max_abs}')
    df = orphanet_mesh[orphanet_mesh['mesh'].notna()]
    for _, row in df.iterrows():
        extract(gemini, row['mesh'], max_abs=max_abs)
