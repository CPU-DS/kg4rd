# extract triples

> Only diseases included in the `Orphanet` database and that can be mapped to the `MeSH` database are extracted here.

## Get Abstracts from PubMed

Use `pubmed/pubmed.py` to retrieve disease-related abstracts from PubMed, and only extract subject terms for diseases (i.e., `mesh` prefixed with `D`).

The data is stored in the `data/data_abstract/` directory, with filenames in the format `{mesh_id}.csv`, where each row represents a literature article.

## Extract Triples

Use the Mesh terms included in the literature to determine the scope of the extracted relationships, and specify through prompts that the extracted relationships can only be within the specified scope.

## Name Map

The names of entities and relationships used in `PrimeKG` may differ from those in the entity and relationship definition files here, so mapping is required.

## UID

Each triple extracted by the model has a unique ID, which uses the form `{mesh_id}:{pmid}:{short-uuid}`.

## Post Processing

Use `triple_supplement/data_parse.py` for post-processing of the extracted results, including the following processes:

1. Determine the IDs of the head and tail entities through synonym search.

2. Determine whether the relationship is within the specified range.

3. Determine whether both entities are already in the knowledge graph (some entities are in the original data files but not in the knowledge graph).

4. Determine whether the triple already exists in the knowledge graph.

The final available files are in the `data/data_abstract/approved_triples_node_exist` directory.

## Generate Supplementary Files

Use `triple_supplement/supplement.py` to aggregate and deduplicate the above triples, generate supplementary triples, and store them in `src/kg4rd/kg/kg_supplement.csv` and `src/kg4rd/kg/edges_supplement.csv` files.
