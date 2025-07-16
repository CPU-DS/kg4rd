# -*- coding: utf-8 -*-
# Create Date: 2025/06/03
# Author: houfengzhen
# File Name: extract.py
# Description: 从 PubMed 中提取三元组

import pandas as pd
import json
from google import genai
from google.genai.types import GenerateContentConfig, ThinkingConfig
from google.genai.types import HttpOptions
import time
from pydantic import BaseModel
from enum import Enum
from typing import Generic, TypeVar, TypedDict
import os
from loguru import logger
from retry import retry
from shortuuid import uuid


os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'


T = TypeVar('T')

SYSTEM_PROMPT = "You are an AI assistant specializing in biomedical information extraction. Your task is to extract strictly defined biomedical relationship triples (Subject, Predicate, Object) from the provided abstract, with a specific focus on information relevant to human disease drug repositioning."

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'), http_options=HttpOptions(timeout=3*60*1000))

with open('src/kg4rd/extractor/prompt.md', 'rt', encoding='utf-8') as fp:
    prompt = fp.read()
    
with open('src/kg4rd/extractor/definition of node type.txt', 'rt', encoding='utf-8') as fp:
    node_type = fp.read()

with open('src/kg4rd/extractor/examples.json', 'r', encoding='utf-8') as f:
    examples = json.load(f)

with open('src/kg4rd/extractor/disease_subheadings_to_relation.json', 'r', encoding='utf-8') as f:
    disease_subheadings_to_relation = json.load(f)

with open('src/kg4rd/extractor/definition_of_relations.json', 'r', encoding='utf-8') as f:
    definition_of_relations = json.load(f)
        
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


class Triple(BaseModel, Generic[T]):
    subject: str
    predicate: T
    object: str


@retry(tries=5, delay=60)
def extract_relations_with_gemini(abstract, relations, relations_with_definitions, prompt, examples:list[dict]=None):     
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

    RelationType = Enum('RelationType', {name: name for name in relations})

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_prompt,
        config=GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=list[Triple[RelationType]]
        )
    )
    return json.loads(response.text)


def extract(mesh_id: str):
    
    # heading = orphanet_mesh.query('mesh == @mesh_id')['mesh_name'].values[0]
    heading = 'Muscular Dystrophy, Duchenne'

    # df = pd.read_csv(f'data/data_abstract/{mesh_id}.csv') 
    df = pd.read_excel('src/kg4rd/extractor/disease_DMD_abstracts.xlsx')

    # save_file = f'data/data_abstract/result/{mesh_id}.json'
    save_file = f'src/kg4rd/extractor/dmd.json'

    if os.path.exists(save_file):
        with open(save_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    for idx, row in df.iterrows():
        logger.info(f"处理第 {idx}/{len(df)}条")
        
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

        try:
            extracted_relations = extract_relations_with_gemini(abstract, list(relations), relations_with_definitions, prompt, examples)
        except Exception as e:
            raise e
        else:
            for r in extracted_relations:
                r['uid'] = f'{mesh_id}:{row["pmid"]}:{str(uuid4())}'
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
    extract('')
