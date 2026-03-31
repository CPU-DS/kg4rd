import type { EnvironmentConfig } from '../types'

export const productionConfig: EnvironmentConfig = {
  api: {
    baseURL: 'http://localhost:5555/api/v1',
    timeout: 300000, // 5分钟超时，适应长时间推理
  },
  app: {
    name: 'kg4rd',
    version: '0.1.0',
  },
}