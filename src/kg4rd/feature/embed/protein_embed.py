# -*- coding: utf-8 -*-
# Create Date: 2025/07/17
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: protein_embed.py
# Description: protein feature embedding

import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com/'
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from esm.models.esm3 import ESM3
from esm.sdk.api import ESMProtein, SamplingConfig
from esm.utils.constants.models import ESM3_OPEN_SMALL
from Bio import SeqIO
import pandas as pd
import numpy as np
from tqdm import tqdm
import torch

client = ESM3.from_pretrained(ESM3_OPEN_SMALL, device="cuda:3")
client_cpu = ESM3.from_pretrained(ESM3_OPEN_SMALL, device="cpu")

def get_sequence_embedding(sequence):
    protein = ESMProtein(sequence)
    protein_tensor = client.encode(protein)
    try:
        output = client.forward_and_sample(
            protein_tensor, SamplingConfig(return_mean_embedding=True)
        )
        return output.mean_embedding
    except torch.cuda.OutOfMemoryError as e:
        return None

def get_prot_seq(ncbi_id: int, seq_name: str):
    path = f'~/gene/{ncbi_id}/protein.faa'
    if not os.path.exists(path):
        return None
    for record in SeqIO.parse(path, 'fasta'):
        if record.id == seq_name:
            return record.seq
    return None

if __name__ == "__main__":
    sequence_ids = []
    embeddings = []
    ids = []
    
    ref_seq = pd.read_csv('data/data_feature/MANE.GRCh38.v1.4.summary.tsv', sep='\t')
    ref_seq = ref_seq[ref_seq['RefSeq_prot'].notna()][['NCBI_GeneID', 'RefSeq_prot']]
    ref_seq['NCBI_GeneID'] = ref_seq['NCBI_GeneID'].apply(lambda x: int(x.split(':')[1]))

    no_seq = 0
    no_processed = 0
    for index, row in tqdm(ref_seq.iterrows(), total=len(ref_seq)):
        ncbi_id = row.NCBI_GeneID
        seq_name = row.RefSeq_prot
        seq = get_prot_seq(ncbi_id, seq_name)
        if seq is not None:
            if (embedding := get_sequence_embedding(str(seq))) is not None:
                sequence_ids.append(seq_name)
                ids.append(ncbi_id)
                embeddings.append(embedding.cpu().numpy())
            else:
                no_processed += 1
        else:
            no_seq += 1
    np.savez_compressed('data/data_feature/protein_seq_embed.npz', sequence_ids=sequence_ids, ids=ids, embeddings=embeddings)

    print(f"Total sequences processed: {len(sequence_ids)}")
    print(f"Sequences with no protein found: {no_seq}")
    print(f"Sequences that could not be processed: {no_processed}")
    print("Protein sequence embedding completed.")
    