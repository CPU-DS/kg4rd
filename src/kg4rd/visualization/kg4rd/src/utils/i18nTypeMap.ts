import type { TFunction } from 'i18next'
import type { NodeType, RelationType } from '../types'

/**
 * 获取关系类型的国际化标签
 */
export const getRelationLabel = (relationType: RelationType, t: TFunction): string => {
  return t(`relationTypes.${relationType}`, { defaultValue: relationType })
}

/**
 * 获取节点类型的国际化标签
 */
export const getNodeLabel = (nodeType: NodeType, t: TFunction): string => {
  return t(`nodeTypes.${nodeType}`, { defaultValue: nodeType })
}

/**
 * 获取所有关系类型的国际化标签映射
 */
export const getRelationLabels = (t: TFunction): Record<RelationType, string> => {
  const relationTypes: RelationType[] = [
    'drug_drug',
    'protein_protein',
    'disease_phenotype_positive',
    'bioprocess_protein',
    'cellcomp_protein',
    'molfunc_protein',
    'phenotype_protein',
    'disease_protein',
    'disease_disease',
    'drug_effect',
    'pathway_protein',
    'bioprocess_bioprocess',
    'drug_protein',
    'phenotype_phenotype',
    'contraindication',
    'molfunc_molfunc',
    'indication',
    'cellcomp_cellcomp',
    'drug_pathway',
    'pathway_pathway',
    'off-label use',
    'disease_phenotype_negative',
  ]

  const labels = {} as Record<RelationType, string>
  relationTypes.forEach(relationType => {
    labels[relationType] = getRelationLabel(relationType, t)
  })

  return labels
}

/**
 * 获取所有节点类型的国际化标签映射
 */
export const getNodeLabels = (t: TFunction): Record<NodeType, string> => {
  const nodeTypes: NodeType[] = [
    'disease',
    'drug',
    'gene/protein',
    'pathway',
    'effect/phenotype',
    'molecular_function',
    'cellular_component',
    'biological_process',
  ]

  const labels = {} as Record<NodeType, string>
  nodeTypes.forEach(nodeType => {
    labels[nodeType] = getNodeLabel(nodeType, t)
  })

  return labels
}
