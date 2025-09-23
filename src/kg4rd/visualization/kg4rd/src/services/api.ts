

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ResultCode } from '../types'
import type { Result } from '../types'

export interface APIConfig {
  baseURL: string
  timeout?: number
  headers?: Record<string, string>
}

const DEFAULT_CONFIG: APIConfig = {
  baseURL: 'http://10.4.3.155:5555/api/v1',
  timeout: 300000, // 5分钟超时，适应长时间推理
  headers: {
    'Content-Type': 'application/json',
  },
}


export class API {
  private instance: AxiosInstance

  constructor(config: Partial<APIConfig> = {}) {
    const finalConfig = { ...DEFAULT_CONFIG, ...config }
    
    this.instance = axios.create({
      baseURL: finalConfig.baseURL,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    })

    this.instance.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    this.instance.interceptors.response.use(
      (response: AxiosResponse<Result>) => {
        const { data } = response
        
        if (data.code === ResultCode.QUERY_OK) {
          return response
        } else {
          throw new Error(data.message || 'API业务错误')
        }
      },
      (error) => {
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<Result<T>> {
    const response = await this.instance.get<Result<T>>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<Result<T>> {
    const response = await this.instance.post<Result<T>>(url, data, config)
    return response.data
  }

  getAxiosInstance(): AxiosInstance {
    return this.instance
  }
}

export const api = new API()