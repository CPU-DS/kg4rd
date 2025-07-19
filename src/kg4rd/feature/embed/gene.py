# -*- coding: utf-8 -*-
# Create Date: 2025/07/17
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gene.py
# Description: gene feature embedding

import numpy as np
from Bio import SeqIO

npz = np.load('data/data_feature/gene_seq_embed.npz')
seq_ids = npz['sequence_ids']
embeddings = npz['embeddings']

kv = {k: v for k, v in zip(seq_ids, embeddings)}

def get_gene_embed_by_seq_id(seq_id: str):
    return kv[seq_id]

def get_gene_embed(ncbi_id: int) -> np.ndarray:
    path = f'data/data_feature/gene/{ncbi_id}/gene.fna'
    record = next(SeqIO.parse(path, 'fasta'))
    return get_gene_embed_by_seq_id(record.id)


if __name__ == '__main__':
    print(get_gene_embed(1))
