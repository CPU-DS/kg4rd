/**
 * 实体服务
 * 对应后端 entity_service.py
 */

import { api } from './api'
import type { Entity, EntityDTO, EntityQuery, Result } from '../types'

export class EntityService {
  private readonly baseUrl = '/entity'

  async query(query: EntityQuery): Promise<Result<EntityDTO[]>> {
    return api.post<EntityDTO[]>(`${this.baseUrl}/query`, query)
  }

  async getByIndex(nodeIndex: number): Promise<Result<Entity>> {
    return api.get<Entity>(`${this.baseUrl}/get/${nodeIndex}`)
  }

}

export const entityService = new EntityService()