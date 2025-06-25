# -*- coding: utf-8 -*-
# Create Date: 2025/06/24
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gene.py
# Description: gene/protein 序列

import os
import pandas as pd
import requests
import zipfile
import shutil
from tqdm import tqdm
import time


gene_id_df = (
    pd.read_csv('data/vocab/gene_names.csv', sep='\t')
    .loc[:, ['Approved symbol', 'NCBI Gene ID(supplied by NCBI)']]
    .drop_duplicates()
    .dropna()
    .rename(columns={
        'Approved symbol': 'symbol',
        'NCBI Gene ID(supplied by NCBI)': 'id'
    })
)
gene_id_df['id'] = gene_id_df['id'].astype(int).astype(str)

headers = {
    'Content-Type': 'application/zip',
    'api-key': os.getenv('NCBI_API_KEY')
}


def download(gene_id):
    url = f'https://api.ncbi.nlm.nih.gov/datasets/v2/gene/id/{gene_id}/download'
    query = {
        'include_annotation_type': ['FASTA_GENE', 'FASTA_PROTEIN', 'FASTA_RNA']
    }
    response = requests.get(url, headers=headers, params=query)
    if response.status_code != 200:
        return False
    
    zip_file = f'data_feature/gene/{gene_id}.zip'
    with open(zip_file, 'wb') as f:
        f.write(response.content)

    dir_ = f'data_feature/gene/{gene_id}'
    os.makedirs(dir_, exist_ok=True)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(dir_)

    os.remove(zip_file)
    os.remove(f'{dir_}/md5sum.txt')
    os.remove(f'{dir_}/README.md')

    data_dir = f'{dir_}/ncbi_dataset/data'

    for file_name in os.listdir(data_dir):
        os.rename(f'{data_dir}/{file_name}', f'{dir_}/{file_name}')

    shutil.rmtree(f'{dir_}/ncbi_dataset')
    return True


def wait_for_download(gene_id):
    while not download(gene_id):
        time.sleep(60)
        
from glob import glob
li =[os.path.basename(file) for file in glob('data_feature/gene/*')]

for _, row in tqdm(gene_id_df.iterrows(), total=len(gene_id_df)):
    if row['id'] in li:
        continue
    try:
        wait_for_download(row['id'])
    except Exception as e:
        print(row['id'])
        raise e
