/**
 * 关系相关类型定义
 * 对应后端 relation_model.py
 */

import type { NodeType } from './entity_type'

export type RelationDirection = 'in' | 'out' | 'bidirection'

export type RelationType = 
  | 'drug_drug'
  | 'protein_protein'
  | 'disease_phenotype_positive'
  | 'bioprocess_protein'
  | 'cellcomp_protein'
  | 'molfunc_protein'
  | 'phenotype_protein'
  | 'disease_protein'
  | 'disease_disease'
  | 'drug_effect'
  | 'pathway_protein'
  | 'bioprocess_bioprocess'
  | 'drug_protein'
  | 'phenotype_phenotype'
  | 'contraindication'
  | 'molfunc_molfunc'
  | 'indication'
  | 'cellcomp_cellcomp'
  | 'drug_pathway'
  | 'pathway_pathway'
  | 'off-label use'
  | 'disease_phenotype_negative'

export type MatchRelationType = 'all' | RelationType

export interface Relation {
  relation_name: string
  x_index: number
  x_name: string
  x_type: NodeType
  y_index: number
  y_name: string
  y_type: NodeType
  uid?: string
  display_relation_name?: string
}

export interface RelationQuery {
  node_index: number
  direction?: RelationDirection
  relation_type?: MatchRelationType
  hop?: number
}