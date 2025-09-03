# -*- coding: utf-8 -*-
# Create Date: 2025/06/19
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: simple_search.py
# Description: 同义词查询

from typing import Optional

from numpy import int_
import pandas as pd

df_dis = pd.read_csv('data/data_synonyms/mondo_synonyms_concat.csv')
df_dis['name'] = df_dis['name'].astype(str).apply(lambda x: x.lower())

df_drug = pd.read_csv('data/data_synonyms/drugbank_synonyms_concat.csv')
df_drug['name'] = df_drug['name'].astype(str).apply(lambda x: x.lower())
df_drug['id'] = df_drug['id'].apply(lambda x: int(x.strip('DB'))).astype(str)

df_go = pd.read_csv('data/data_synonyms/go_synonyms.csv')
df_go['name'] = df_go['name'].astype(str).apply(lambda x: x.lower())

df_phe = pd.read_csv('data/data_synonyms/hpo_synonyms.csv')
df_phe['name'] = df_phe['name'].astype(str).apply(lambda x: x.lower())

df_ana = pd.read_csv('data/data_synonyms/uberon_synonyms.csv')
df_ana['name'] = df_ana['name'].astype(str).apply(lambda x: x.lower())

df_prot = pd.read_csv('data/data_synonyms/hgnc_synonyms.csv')
df_prot['name'] = df_prot['name'].astype(str).apply(lambda x: x.lower())
df_prot = df_prot.drop_duplicates(['id', 'name'])

df_path = pd.read_csv('data/data_synonyms/reactome_synonyms.csv')
df_path['name'] = df_path['name'].astype(str).apply(lambda x: x.lower())
df_path2 = pd.read_csv('data/data/kegg/drug_kegg_pathway.csv').drop('drugbank_id', axis=1).rename(
    columns={'pathway_kegg_id': 'id', 'pathway_kegg_name': 'name'}
)
df_path2['preferred_name'] = True
df_path2.drop_duplicates()
df_path = pd.concat([df_path, df_path2])

df_exp = pd.read_csv('data/data_synonyms/ctd_synonyms.csv')
df_exp['name'] = df_exp['name'].astype(str).apply(lambda x: x.lower())

def simple_search(name: str,
                  type_: str
    ) -> Optional[tuple[str, str, int]]:
    type_ = type_.lower()
    match type_:
        case 'cellular_component' | 'molecular_function' | 'biological_process':
            df = df_go
        case 'disease':
            df = df_dis
        case 'drug':
            df = df_drug
        case 'effect/phenotype':
            df = df_phe
        case 'anatomy':
            df = df_ana
        case 'gene/protein':
            df = df_prot
        case 'pathway':
            df = df_path
        case 'exposure':
            df = df_exp
        case _:
            return None

    name = name.lower()
    if len(ids := df[df['name'] == name]['id'].tolist()) == 0:  # 完全匹配
        return None
    id_ = ids[0]
    preferred_name = df.query('id == @id_ and preferred_name == True')['name'].tolist()[0]
    return 'kg4rd:' + str(id_), preferred_name, 1000  # 完全匹配为 1000 分

if __name__ == '__main__':
    print(simple_search('Muscular Dystrophy, Duchenne', 'disease'))
