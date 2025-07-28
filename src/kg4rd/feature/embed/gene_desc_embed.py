# -*- coding: utf-8 -*-
# Create Date: 2025/07/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gene_desc_embed.py
# Description: gene description embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from typing import Optional
import json
import re
from glob import glob
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

model = SentenceTransformer("neuml/pubmedbert-base-embeddings")

def get_prot_desc(ncbi_id: int) -> Optional[str]:
    path = f'/home/wangtao/gene/{ncbi_id}/data_report.jsonl'
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        data_report = json.load(f)
        desc = data_report.get('summary', [{}])[0].get('description', None)
        desc = re.sub(r'\[.*?\]', '', desc) if desc else None
    return desc

if __name__ == "__main__":
    ids = []
    descs = []
    for gene in tqdm(glob('/home/wangtao/gene/*')):
        gene_id = int(gene.split('/')[-1])
        desc = get_prot_desc(gene_id)
        if desc:
            ids.append(gene_id)
            descs.append(desc)
    
    embeddings = model.encode(descs, show_progress_bar=True, batch_size=64)

    np.savez_compressed('data/data_feature/gene_desc_embed.npz',
                       ids=ids,
                       embeddings=embeddings)
