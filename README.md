# kg4rd

## Install

```bash
git clone https://github.com/CPU-DS/kg4rd.git
cd kg4rd
uv sync
```

If you encounter the following error when installing dependencies by using `uv add` or `pip install`, please add `-f https://data.dgl.ai/wheels/torch-2.1/cu121/repo.html` to your installation command.

```bash
error: Distribution `dgl==2.2.1 @ registry+https://pypi.org/simple` can't be installed because it doesn't have a source distribution or wheel for the current platform
```

## Download data

```bash
hf download wangtao2001/kg4rd --repo-type=dataset --local-dir=data
```

## Table of Contents

```bash
.
├── data/               # project data, use `hf download` to download and store here.
├── src/kg4rd/          # source code.
│   ├── data_process/   # data process and build knowledge graph.
│   ├── dock/           # molecular docking related.
│   ├── extract/        # extract triples by llm.
│   ├── feature/        # get entity features and entity embeddings.
│   ├── gcl/            # graph contrastive learning.
│   ├── kg/             # knowledge graph structure.
│   ├── kg2neo4j/       # export knowledge graph to neo4j.
│   ├── kge/            # knowledge graph embedding.
│   ├── overview/       # overview of the knowledge graph.
│   ├── pubmed/         # get abstracts from pubmed.
│   ├── synonyms/       # get entity synonyms.
│   └── visualization/  # visualize the knowledge graph, including backend and web frontend.
├── .gitignore
├── .python-version
├── README.md
└── pyproject.toml
```

## Quick Start

- Build knowledge graph, execute the notebook `src/kg4rd/data_process/build_graph.ipynb`.
- Split data for training and testing, execute the notebook `src/kg4rd/kge/data_split.ipynb`.
- Use distributed training to train TransE model:

```bash
source .venv/bin/activate
accelerate config
accelerate launch src/kg4rd/kge/src/scripts/TransE_entire.py --config src/kg4rd/kge/src/config/TransE_entire_Accel_20250910.yaml
```

- Use link prediction for relationships you are interested in, here we execute the notebook `src/kg4rd/kge/src/link_predict/drug_TAK1_TransE.ipynb` to predict the relationship between protein target `TAK1` and all drugs.