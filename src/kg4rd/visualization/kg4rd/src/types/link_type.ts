/**
 * 链接预测相关类型定义
 * 对应后端 link_model.py
 */

import type { NodeType } from './entity_type'
import type { RelationType } from './relation_type'

export interface LinkRequest {
  head: number[] | NodeType
  rel: RelationType[]
  tail: number[] | NodeType
  model_name: string
  limit?: number
}

export type LinkRelationType = 'present' | 'absent'

export interface LinkRelation {
  relation_name: string
  x_index: number
  x_name: string
  x_type: NodeType
  y_index: number
  y_name: string
  y_type: NodeType
  score: number
  type: LinkRelationType
}

export type LinkResult = LinkRelation[]