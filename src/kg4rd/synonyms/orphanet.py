# -*- coding: utf-8 -*-
# Create Date: 2025/06/18
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: orphanet.py
# Description: ORPHANET 同义词

import pandas as pd
import requests
from tqdm import tqdm


def method1():
    data = []
    mondo_ref = 'data/mondo/mondo_references.csv'
    orphanet_df = pd.read_csv(mondo_ref).query('ontology == "Orphanet"')
    for _, row in tqdm(orphanet_df.iterrows(), total=len(orphanet_df)):
        mondo_id = f'MONDO:{int(row["ontology_id"]):07d}'
        orphanet_id = row['ontology_id']
        name_url = f'https://api.orphacode.org/EN/ClinicalEntity/orphacode/{orphanet_id}/Name'
        response = requests.get(name_url, headers={'apiKey': '123456'}).json()
        if response == "Query not found":
            continue
        else:
            name = response['Preferred term']
            synonym_url = f'https://api.orphacode.org/EN/ClinicalEntity/orphacode/{orphanet_id}/Synonym'
            response = requests.get(synonym_url, headers={'apiKey': '123456'}).json()
            if response == "Query not found":
                synonym = []
            else:
                synonym = response['Synonym'] if response['Synonym'] is not None else []
            data.append({
                'id': f'ORID:{int(orphanet_id):07d}',
                'name': name,
                'preferred_name': True,
                'mondo_id': mondo_id
            })
            for s in synonym:
                data.append({
                    'id': f'ORID:{int(orphanet_id):07d}',
                    'name': s,
                    'preferred_name': '',
                    'mondo_id': mondo_id
                })

    pd.DataFrame(data).to_csv('data_synonyms/orphanet_synonyms.csv', index=False)


def method2():
    df = pd.read_excel('data/orphanet/Orphanet_Nomenclature_Pack_EN/ORPHAnomenclature_MasterFile_en_2024.xlsx')
    df['preferred_name'] = ''
    mask = pd.isna(df['Synonyms']) & (~pd.isna(df['ICDcodes']))
    df.loc[mask, 'Synonyms'] = df.loc[mask, 'PreferredTerm']
    df.loc[mask, 'preferred_name'] = True
    df = df.drop(['PreferredTerm', 'ICDcodes'], axis=1)
    df = df.rename(columns={'ORPHAcode': 'id', 'PreferredTerm': 'name'})
    df['id'] = df['id'].astype(int)
    
    mondo_ref = 'data/mondo/mondo_references.csv'
    mondo_ref_df = pd.read_csv(mondo_ref).query('ontology == "Orphanet"')
    mondo_ref_df['ontology_id'] = mondo_ref_df['ontology_id'].astype(int)
    
    df = pd.merge(df, mondo_ref_df, 'inner', left_on='id', right_on='ontology_id')
    df['mondo_id'] = df['mondo_id'].apply(lambda x: f"MONDO:{int(x):07d}")
    df['id'] = df['id'].apply(lambda x: f"Orphanet:{int(x):07d}")
    df = df.drop(['ontology_id', 'ontology'], axis=1)
    df = df.rename(columns={'Synonyms': 'name'})
    
    df.to_csv('data_synonyms/orphanet_synonyms.csv', index=False)


if __name__ == "__main__":
    method2()
