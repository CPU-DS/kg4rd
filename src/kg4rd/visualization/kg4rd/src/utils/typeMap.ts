import type { NodeType } from '../types/entity_type'
import type { RelationType } from '../types/relation_type'

export const relation2node: Record<
    RelationType, 
    { in_type: NodeType, out_type: NodeType }
> = {
    'drug_drug': {
        in_type: 'drug',
        out_type: 'drug'
    },
    'protein_protein': {
        in_type: 'gene/protein',
        out_type: 'gene/protein'
    },
    'disease_phenotype_positive': {
        in_type: 'disease',
        out_type: 'effect/phenotype'
    },
    'bioprocess_protein': {
        in_type: 'gene/protein',
        out_type: 'biological_process'
    },
    'cellcomp_protein': {
        in_type: 'gene/protein',
        out_type: 'cellular_component'
    },
    'molfunc_protein': {
        in_type: 'gene/protein',
        out_type: 'molecular_function'
    },
    'disease_protein': {
        in_type: 'gene/protein',
        out_type: 'disease'
    },
    'disease_disease': {
        in_type: 'disease',
        out_type: 'disease'
    },
    'pathway_protein': {
        in_type: 'gene/protein',
        out_type: 'pathway'
    },
    'bioprocess_bioprocess': {
        in_type: 'biological_process',
        out_type: 'biological_process'
    },
    'drug_protein': {
        in_type: 'drug',
        out_type: 'gene/protein'
    },
    'phenotype_phenotype': {
        in_type: 'effect/phenotype',
        out_type: 'effect/phenotype'
    },
    'contraindication': {
        in_type: 'drug',
        out_type: 'disease'
    },
    'molfunc_molfunc': {
        in_type: 'molecular_function',
        out_type: 'molecular_function'
    },
    'indication': {
        in_type: 'drug',
        out_type: 'disease'
    },
    'cellcomp_cellcomp': {
        in_type: 'cellular_component',
        out_type: 'cellular_component'
    },
    'drug_pathway': {
        in_type: 'drug',
        out_type: 'pathway'
    },
    'pathway_pathway': {
        in_type: 'pathway',
        out_type: 'pathway'
    },
    'off-label use': {
        in_type: 'drug',
        out_type: 'disease'
    },
    'disease_phenotype_negative': {
        in_type: 'disease',
        out_type: 'effect/phenotype'
    },
    'phenotype_protein': {
        in_type: 'gene/protein',
        out_type: 'effect/phenotype'
    },
    'drug_effect': {
        in_type: 'drug',
        out_type: 'effect/phenotype'
    }
}

export const node2relation: Record<
    NodeType, 
    {in_relation_type: RelationType[], out_relation_type: RelationType[]}
> = {
    'disease': {
        in_relation_type: ['disease_disease', 'contraindication', 'indication', 'off-label use', 'disease_protein'],
        out_relation_type: ['disease_phenotype_positive', 'disease_phenotype_negative', 'disease_disease'],
    },
    'drug': {
        in_relation_type: ['drug_drug'],
        out_relation_type: ['drug_drug', 'drug_pathway', 'drug_protein', 'drug_effect', 'contraindication', 'off-label use', 'indication']
    },
    'effect/phenotype': {
        in_relation_type: ['phenotype_phenotype', 'phenotype_protein', 'drug_effect', 'disease_phenotype_negative', 'disease_phenotype_positive'],
        out_relation_type: ['phenotype_phenotype']
    },
    'gene/protein': {
        in_relation_type: ['protein_protein', 'drug_protein'],
        out_relation_type: ['protein_protein', 'disease_protein', 'phenotype_protein', 'pathway_protein', 'molfunc_protein', 'cellcomp_protein', 'bioprocess_protein']
    },
    'pathway': {
        in_relation_type: ['pathway_pathway', 'drug_pathway', 'pathway_protein'],
        out_relation_type: ['pathway_pathway']
    },
    'biological_process': {
        in_relation_type: ['bioprocess_bioprocess', 'bioprocess_protein'],
        out_relation_type: ['bioprocess_bioprocess']
    },
    'molecular_function': {
        in_relation_type: ['molfunc_molfunc', 'molfunc_protein'],
        out_relation_type: ['molfunc_molfunc']
    },
    'cellular_component': {
        in_relation_type: ['cellcomp_cellcomp', 'cellcomp_protein'],
        out_relation_type: ['cellcomp_cellcomp']
    }
}

export const relationLabels: Record<RelationType, string> = {
    'drug_drug': '药物-药物',
    'protein_protein': '蛋白质-蛋白质',
    'disease_phenotype_positive': '疾病-表型(正向)',
    'bioprocess_protein': '生物过程-蛋白质',
    'cellcomp_protein': '细胞组分-蛋白质',
    'molfunc_protein': '分子功能-蛋白质',
    'phenotype_protein': '表型-蛋白质',
    'disease_protein': '疾病-蛋白质',
    'disease_disease': '疾病-疾病',
    'drug_effect': '药物-效应',
    'pathway_protein': '通路-蛋白质',
    'bioprocess_bioprocess': '生物过程-生物过程',
    'drug_protein': '药物-蛋白质',
    'phenotype_phenotype': '表型-表型',
    'contraindication': '禁忌症',
    'molfunc_molfunc': '分子功能-分子功能',
    'indication': '适应症',
    'cellcomp_cellcomp': '细胞组分-细胞组分',
    'drug_pathway': '药物-通路',
    'pathway_pathway': '通路-通路',
    'off-label use': '超说明书用药',
    'disease_phenotype_negative': '疾病-表型(负向)'
  }

export  const nodeLabels: Record<NodeType, string> = {
    'disease': '疾病',
    'drug': '药物',
    'gene/protein': '基因/蛋白质',
    'pathway': '通路',
    'effect/phenotype': '效应/表型',
    'molecular_function': '分子功能',
    'cellular_component': '细胞组分',
    'biological_process': '生物过程'
  }