# data process

## Build knowledge graph

The relevant data acquisition and processing have already been prepared in the `data/` directory. You only need to run the notebook `build_graph.ipynb`. If you need to re-acquire and process the data, please refer to the [PrimeKG](#primekg) section.

### Result

The knowledge graph is stored in the `src/kg4rd/kg/` directory and contains the following files:

- `kg.csv`: Contains all relationships in the knowledge graph. The head entity is indicated by `x_`, and the tail entity by `y_`. All relationships are unidirectional and do not include reverse relationships.

- `edges.csv`: A subset of columns from `kg.csv`.

- `nodes.csv`: Contains all entities in the knowledge graph. `index` represents the entity's index in the knowledge graph, and `id` represents the entity's index in the original data source.

- `auxiliary/`: Intermediate directory.

## PrimeKG

First, clone the repository:

```bash
git clone https://github.com/mims-harvard/PrimeKG.git
```

The data acquisition script is `PrimeKG/datasets/primary_data_resources.sh`, and the data processing script is stored in the `PrimeKG/datasets/processing_scripts` directory.

> For some scripts, you may need to modify the data path.

### Differences

- Some entities in MONDO were removed because their IDs are not numeric, making effective entity mapping impossible. The processed data file is `mondo_terms_2.csv`.

- Added a script to process protein-protein interactions missing in PrimeKG. The corresponding file is `ppi.py`.

- Added relationships between drugs and pathways. Used `drug-mappings.tsv` from [drug_id_mapping](https://github.com/iit-Demokritos/drug_id_mapping) to map DrugBank IDs of drugs to KEGG IDs, and used `mappings/kegg_reactome.csv` from [ComPath](https://github.com/ComPath/compath-resources) to map KEGG IDs of pathways to REACTOME IDs. All related processing is in `kegg_drug_path.ipynb`.

- Used Docker to process the drugcentral database and exported drug-disease relationships. The corresponding file is `drugcentral.sh`.

- In the knowledge graph construction file `build_graph.ipynb`, bidirectional relationships, disease clustering, add a prefix `kg4rd:` to all entity `id`, and the entities and relationships of `exposure` and `anatomy` were removed. 

## Disease Clustering

The new disease clustering logic can be found in the `disease_clustering.ipynb` file.
