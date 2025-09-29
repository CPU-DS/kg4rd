import type { Environment, EnvironmentConfig } from './types'
import { developmentConfig } from './environments/development'
import { productionConfig } from './environments/production'

const configs: Record<Environment, EnvironmentConfig> = {
  development: developmentConfig,
  production: productionConfig,
}

/**
 * 获取当前环境
 * 优先级：VITE_APP_ENV > NODE_ENV > 'development'
 */
function getCurrentEnvironment(): Environment {
  const viteEnv = import.meta.env.VITE_APP_ENV as Environment
  const nodeEnv = import.meta.env.NODE_ENV as Environment
  
  if (viteEnv && ['development', 'production'].includes(viteEnv)) {
    return viteEnv
  }
  
  if (nodeEnv && ['development', 'production'].includes(nodeEnv)) {
    return nodeEnv
  }
  
  return 'development'
}

/**
 * 获取当前环境的配置
 */
export function getConfig(): EnvironmentConfig {
  const env = getCurrentEnvironment()
  const config = configs[env]
  
  return config
}

/**
 * 获取当前环境名称
 */
export function getEnvironment(): Environment {
  return getCurrentEnvironment()
}

/**
 * 检查是否为开发环境
 */
export function isDevelopment(): boolean {
  return getCurrentEnvironment() === 'development'
}

/**
 * 检查是否为生产环境
 */
export function isProduction(): boolean {
  return getCurrentEnvironment() === 'production'
}

// 导出类型
export type { Environment, EnvironmentConfig } from './types'