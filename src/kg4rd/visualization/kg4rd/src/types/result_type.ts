/**
 * API响应结果类型定义
 * 对应后端 result_model.py
 */

export enum ResultCode {
  QUERY_OK = 20011,
  QUERY_ERR = 40011
}

export interface Result<T = any> {
  code: ResultCode
  message: string
  data: T | null
}

export interface SuccessResult<T> extends Result<T> {
  code: ResultCode.QUERY_OK
  data: T
}

export interface ErrorResult extends Result<null> {
  code: ResultCode.QUERY_ERR
  data: null
}