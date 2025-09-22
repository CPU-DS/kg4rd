/**
 * 链接预测服务
 * 对应后端 link_service.py
 */

import { api } from './api'
import type { LinkRequest, LinkResult, Result } from '../types'

export class LinkService {
  private readonly baseUrl = '/link'

  async predict(request: LinkRequest): Promise<Result<LinkResult>> {
    return api.post<LinkResult>(`${this.baseUrl}/predict`, request)
  }

  async getModelNames(): Promise<Result<string[]>> {
    return api.get<string[]>(`${this.baseUrl}/model_names`)
  }
}

export const linkService = new LinkService()