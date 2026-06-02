import type { EnvironmentConfig } from '../types'

export const developmentConfig: EnvironmentConfig = {
  api: {
    baseURL: 'http://10.4.0.141:5555/api/v1',
    timeout: 300000, // 5分钟超时，适应长时间推理
  },
  app: {
    name: 'kg4rd',
    version: '0.1.0',
  },
}