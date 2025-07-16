# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: gene_select.py
# Description: 使用MANE选择代表性序列

import pandas as pd
import os
import json
from glob import glob
from tqdm import tqdm

ref_df = pd.read_csv('data/data_feature/MANE.GRCh38.v1.4.summary.tsv', sep='\t')

type_count = {
    'notype': 0
}


def fna_parse(fna_file):
    with open(fna_file, 'r') as f:
        start = False
        seq = ''
        name = ''
        for line in f:
            if line.startswith('>'):
                if start:
                    yield name, seq
                start = True
                name = line.strip()
            else:
                seq += line.strip()
        yield name, seq

data = []

for folder in tqdm(glob('data/data_feature/gene/*')):
    report_file = folder + '/data_report.jsonl'
    if not os.path.exists(report_file):
        type_ = 'notype'
    else:
        type_ = json.load(open(report_file)).get('type', 'notype')

    gene_id =f'GeneID:{folder.split("/")[-1]}'

    if gene_id == 'GeneID:100506696':
        print(gene_id)

    RefSeq_nuc_name = None
    RefSeq_prot_name = None
    RefSeq_prot_seq = None
    RefSeq_nuc_seq = None
    if (res:=ref_df.query("NCBI_GeneID == @gene_id and MANE_status == 'MANE Select'")).shape[0] != 0:
        RefSeq_nuc_name = res['RefSeq_nuc'].tolist()[0]
        RefSeq_prot_name = res['RefSeq_prot'].tolist()[0]
        if not pd.isna(RefSeq_prot_name):
            for name, seq in fna_parse(folder + '/protein.faa'):
                if RefSeq_prot_name in name:
                    RefSeq_prot_seq = seq
        if not pd.isna(RefSeq_nuc_name):
            for name, seq in fna_parse(folder + '/rna.fna'):
                if RefSeq_nuc_name in name:
                    RefSeq_nuc_seq = seq

        
    data.append({
        'gene_id': gene_id,
        'type': type_,
        'RefSeq_nuc_name': RefSeq_nuc_name,
        'RefSeq_prot_name': RefSeq_prot_name,
        'RefSeq_prot_seq': RefSeq_prot_seq,
        'RefSeq_nuc_seq': RefSeq_nuc_seq
    })

pd.DataFrame(data).to_csv('data/data_feature/gene.csv', index=False)