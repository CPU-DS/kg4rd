# -*- coding: utf-8 -*-
# Create Date: 2025/06/12
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: disgenet.py
# Description: DisGeNet 处理

import pandas as pd

data_path = 'data/disgenet/curated_gene_disease_associations.tsv'

df = pd.read_csv(data_path, sep='\t')

print(df['source'].unique().tolist())
