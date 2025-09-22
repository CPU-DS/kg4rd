/**
 * 关系服务
 * 对应后端 relation_service.py
 */

import { api } from './api'
import type { Relation, RelationQuery, Result } from '../types'


export class RelationService {
  private readonly baseUrl = '/relation'

  async query(query: RelationQuery): Promise<Result<Relation[]>> {
    return api.post<Relation[]>(`${this.baseUrl}/query`, query)
  }
}

export const relationService = new RelationService()