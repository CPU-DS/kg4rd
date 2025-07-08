# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: orphanet_mesh.py
# Description: 获取罕见病 MeSH ID

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


def get_mesh(code: str) -> dict | None | bool:
    url = f'https://www.orpha.net/en/disease/detail/{code}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('div', class_='result-detail').find('h2').text.strip()
        ps = soup.find_all('p')
        for p in ps:
            if 'MeSH' in p.text:
                return {'name': name, 'mesh': p.text.split('MeSH:')[1].strip()}
        return {'name': name, 'mesh': None}
    elif response.status_code == 500:
        return None
    else:
        return False
    
def get_mesh_name(code: str) -> str | None | bool:
    url = f'https://www.ncbi.nlm.nih.gov/mesh/{code}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('h1', class_='title').text.strip()
    elif response.status_code == 404:
        return None
    else:
        return False

def wait_for_download(func, *args, **kwargs):
    response = func(*args, **kwargs)
    while response == False:
        time.sleep(60)
        response = func(*args, **kwargs)
    return response

if __name__ == '__main__':
    df_orphanet_mondo_ref = pd.read_csv('data/mondo/mondo_references.csv').query('ontology == "Orphanet"')
    df_orphanet_mondo_ref.reset_index(drop=True, inplace=True)
    df_orphanet_mondo_ref['ontology_id'] = df_orphanet_mondo_ref['ontology_id'].astype(int).astype(str)

    data = []

    for _, row in tqdm(df_orphanet_mondo_ref.iterrows(), total=len(df_orphanet_mondo_ref)):
        code = row['ontology_id']
        resp = wait_for_download(get_mesh, code)
        if resp is None:
            name, mesh = None, None
        else:
            (name, mesh) = resp.values()
        mesh_name = None
        if mesh is not None:
            mesh_name = wait_for_download(get_mesh_name, mesh)
        data.append({'code': code, 'name': name, 'mesh': mesh, 'mesh_name': mesh_name})
    pd.DataFrame(data).to_csv('data/orphanet/orphanet_mesh.csv', index=False)
