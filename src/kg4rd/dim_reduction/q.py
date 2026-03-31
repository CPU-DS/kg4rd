# -*- coding: utf-8 -*-
# Create Date: 2025/09/11
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: tsne.py
# Description: tSNE / UMAP 降维可视化

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from umap import UMAP
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import numpy as np
import os
from typing import Optional

_nodes = pd.read_csv(os.path.join(os.path.dirname(__file__), '../kg/nodes.csv'))
_id2type: dict[int, str] = {row['node_index']: row['node_type'] for _, row in _nodes.iterrows()}  # type: ignore


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


def _filter_embeddings(
    embeddings: np.ndarray,
    type_filters: Optional[list[str]],
    l2_normalize: bool,
    sample_ratio: float = 1.0,
    random_seed: int = 42,
) -> tuple[np.ndarray, list[str]]:
    if type_filters is None:
        ids = list(_id2type.keys())
        types = list(_id2type.values())
    else:
        ids = []
        types = []
        for node_index, node_type in _id2type.items():
            if node_type in type_filters:
                ids.append(node_index)
                types.append(node_type)

    if sample_ratio < 1.0:
        rng = np.random.default_rng(random_seed)
        type_indices: dict[str, list[int]] = {}
        for i, t in enumerate(types):
            type_indices.setdefault(t, []).append(i)
        sampled = []
        for indices in type_indices.values():
            k = max(1, int(len(indices) * sample_ratio))
            sampled.extend(rng.choice(indices, size=k, replace=False).tolist())
        sampled.sort()
        ids = [ids[i] for i in sampled]
        types = [types[i] for i in sampled]

    embeddings = embeddings[ids]

    if l2_normalize:
        embeddings = normalize(embeddings, norm='l2')

    return embeddings, types


def _plot(
    embeddings_2d: np.ndarray,
    types: list[str],
    alpha: float,
    point_size: float,
):
    colors = [_color_map[t] for t in types]
    plt.figure(figsize=(9, 9))
    plt.scatter(
        embeddings_2d[0, :], embeddings_2d[1, :],
        label=types, color=colors,
        s=point_size, alpha=alpha, edgecolors='none',
    )
    plt.grid(True, alpha=0.3)

    legend_handles = [mlines.Line2D([], [], color=_color_map[t], marker='o', linestyle='None', markersize=3, label=t) for t in _color_map]
    plt.legend(handles=legend_handles, title='Node Type', loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)

    plt.show()


def plot_tsne(
    embeddings: np.ndarray,
    type_filters: Optional[list[str]] = None,
    sample_ratio: float = 1.0,
    perplexity: float = 50,
    max_iter: int = 2000,
    pca_components: int = 50,
    l2_normalize: bool = True,
    alpha: float = 0.6,
    point_size: float = 5,
):
    embeddings, types = _filter_embeddings(embeddings, type_filters, l2_normalize, sample_ratio)

    embeddings_pca = PCA(n_components=pca_components).fit_transform(embeddings)
    embeddings_2d = TSNE(
        n_components=2,
        perplexity=perplexity,
        max_iter=max_iter,
        learning_rate='auto',
        init='pca',
        metric='cosine',
        n_jobs=-1,
    ).fit_transform(embeddings_pca).T

    _plot(embeddings_2d, types, alpha, point_size)


def plot_umap(
    embeddings: np.ndarray,
    type_filters: Optional[list[str]] = None,
    sample_ratio: float = 1.0,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    pca_components: int = 50,
    l2_normalize: bool = True,
    alpha: float = 0.6,
    point_size: float = 5,
):
    embeddings, types = _filter_embeddings(embeddings, type_filters, l2_normalize, sample_ratio)

    embeddings_pca = PCA(n_components=pca_components).fit_transform(embeddings)
    embeddings_2d = UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric='cosine',
        n_jobs=-1,
    ).fit_transform(embeddings_pca).T

    _plot(embeddings_2d, types, alpha, point_size)
