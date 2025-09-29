export interface EnvironmentConfig {
  api: {
    baseURL: string
    timeout: number
  }
  app: {
    name: string
    version: string
  }
}

export type Environment = 'development' | 'production'