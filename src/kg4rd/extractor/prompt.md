# Context
You will be provided with the following inputs:
 - A pre-defined list of biomedical entity types derived from authoritative knowledge graphs.
 - A pre-defined list of biomedical relationship types, each with a specific 'predicate' (relationship name) and a clear Definition specifying the semantic meaning, and the expected entity types for both 'subject' and 'object'.
 - 0-3 demo examples, including the summary text and the results you should return.
 - An abstract from a biomedical research publication.

# Instructions

## Prioritize Human Relevance
Only extract relationships that are directly applicable to human diseases, human physiology, or explicitly stated as having therapeutic relevance for humans. Disregard findings that are solely based on animal models unless there is clear mention of human applicability or translational potential.

## Understand Definitions Thoroughly
Carefully study the provided entity types and relationship definitions. Pay close attention to the expected 'subject' and 'object' entity types for each 'predicate'. Every identified entity must correspond precisely to one of the predefined entity types.

## Read Abstract Carefully
Examine the abstract in detail to identify statements that clearly express any of the pre-defined relationships between entities.

## Extract Valid Triples Only:
Identify and extract all relationship triples that strictly match a defined 'predicate' and involve entities of the correct type. Ensure the following:

 - 'subject' and 'object' must be specific biomedical entities mentioned in the abstract and match one of the allowed entity types.

For example, the "Drug" entity type must refer to specific named compounds, biological agents (e.g., named antibodies), or clearly defined experimental drug candidates. Avoid broad terms such as “gene therapy” or “nucleic acid therapy”.

 - The 'subject' and 'object' must be exact contiguous text spans that appear verbatim in the abstract. Do not paraphrase, infer, abbreviate, generalize, or fabricate any entity. If an entity does not appear exactly in the abstract, it must not be included in the triple.

 - Do not infer or assume any relationship that is not explicitly stated.

# Strictness Policy
If no triples in the abstract meet all the defined requirements (semantic, type constraints, human relevance), return an empty list. Do not extract relationships based on vague, inferred, or approximate matches.