/**
 * 实体相关类型定义
 * 对应后端 entity_model.py
 */

export type NodeType = 
  | 'disease'
  | 'drug'
  | 'gene/protein'
  | 'pathway'
  | 'effect/phenotype'
  | 'molecular_function'
  | 'cellular_component'
  | 'biological_process'

export type MatchNodeType = 'all' | NodeType

export type MatchMode = 'strict' | 'contains' | 'prefix' | 'regex'

export interface Entity {
  node_index: number
  node_id: string
  node_name: string
  node_type: NodeType
  node_source: string
  node_source_url: string[]
  node_properties: Record<string, string>
}

export interface EntityDTO {
  node_index: number
  node_name: string
  node_type: string
}

export interface EntityQuery {
  query_type: 'node_index' | 'node_name'
  query_value: string
  node_type?: MatchNodeType
  match_mode?: MatchMode
  limit?: number
}