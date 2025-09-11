# -*- coding: utf-8 -*-
# Create Date: 2025/09/11
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: tsne.py
# Description: tSNE 降维

from unike.module.model import Model
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import numpy as np
import os

_nodes = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../../kg/nodes.csv'))
_id2type = {row['node_index']: row['node_type'] for _, row in _nodes.iterrows()}

_types = list(_id2type.values())
_color_map = {
    'gene/protein': 'blue',
    'anatomy': 'cyan',
    'biological_process': 'magenta',
    'cellular_component': 'yellow',
    'disease': 'red',
    'drug': 'purple',
    'effect/phenotype': 'plum',
    'exposure': 'orange',
    'molecular_function': 'lightgreen',
    'pathway': 'sienna',
}
_colors = [ _color_map[t] for t in _types]

def plot_tsne(model: Model):
    embeddings: np.ndarray = model.ent_embeddings.weight.data.cpu().numpy()
    embeddings_pca = PCA(n_components=50).fit_transform(embeddings)
    embeddings_2d = TSNE(n_components=2).fit_transform(embeddings_pca).T
    plt.figure(figsize=(9, 9))
    scatter = plt.scatter(embeddings_2d[0, :], embeddings_2d[1, :], label=_types, color=_colors, s=10)
    plt.grid(True, alpha=0.3)

    legend_handles = [mlines.Line2D([], [], color=_color_map[t], marker='o', linestyle='None', markersize=3, label=t) for t in _color_map]
    plt.legend(handles=legend_handles, title='Node Type', loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)

    plt.show()
