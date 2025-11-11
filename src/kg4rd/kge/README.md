# knowledge graph embedding

## Data

Use `data_split.ipynb` to create a dataset that meets the format requirements of the `UniKE` framework from the knowledge graph and store it in the `data/` directory.

The first line of all data files contains the number of data rows included in the file, and the official data starts from the second line.

All data files and their descriptions are as follows:

- `entity2id.txt`: Mapping from entities to IDs, in the format of `{entity_name}:{entity_type}\t{entity_id}`

- `relation2id.txt`: Mapping from relations to IDs, in the format of `{relation_name}\t{relation_id}`

- `all2id.txt`: All triples in the knowledge graph

- `train2id.txt`, `valid2id.txt`, `test2id.txt`: Triples for the training set, validation set, and test set

- `*_base.txt`: Triples on the unreplenished knowledge graph

- `*_head_200.txt`: The first 200 rows of data in the corresponding dataset, used for quick testing and can be ignored

All triple files are in the format of `{head_entity_id}\t{tail_entity_id}\t{relation_id}`

## Models

All model training, testing, and evaluation scripts are located in the `src/kg4rd/kge/src/scripts/` directory. They are all named in the format of [model name] + [suffix], where the suffixes include:

- `hpo`: Hyperparameter search

- `eval`: Testing and evaluation

- `entire`: Training on the entire knowledge graph, which does not include evaluation and testing steps

- `PreEv2`: An improved model that uses GCL results as pre-embeddings. The `PreE` model, as the v1 version, can be ignored

## Config

All training adopts the method of separating scripts and parameters. The parameters are located in the `src/kg4rd/kge/config/` directory, all in YAML format. 

In addition to the various suffixes introduced above, the `Accel` suffix indicates the use of `Accelerate` for distributed training. The last 8-digit number roughly represents the creation date, but it is only used to distinguish files with the same name and has no actual significance.

## Notebook

Experimental result record file.

## Link Prediction

The trained model can be used to perform link prediction tasks. For specific usage, please refer to the example notebook in the `src/link_predict` directory.

When calling the link.link method, provide one or more IDs of the head entity, relationship, or tail entity, and the system will automatically generate the corresponding Cartesian product triples and calculate their prediction scores.

You can also use the provided visualization page for quick link prediction.
