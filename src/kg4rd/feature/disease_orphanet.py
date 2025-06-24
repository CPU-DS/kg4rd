# -*- coding: utf-8 -*-
# Create Date: 2025/06/23
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: disease_orphanet.py
# Description: 获取 Orphanet Summary

import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_summary(code: int) -> str:
    url = f'https://www.orpha.net/en/disease/detail/{code}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    summary = [ele.text for ele in soup.find('div', class_='summary').children if ele.name != 'span' and ele.text != '\n']
    return '\n'.join(summary)


if __name__ == '__main__':
    df_orphanet_mondo_ref = pd.read_csv('data/mondo/mondo_references.csv').query('ontology == "Orphanet"')
    df_orphanet_mondo_ref['ontology_id'] = df_orphanet_mondo_ref['ontology_id'].astype(int).astype(str)
