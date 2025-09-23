import * as XLSX from 'xlsx'
import type { LinkResult, NodeType, RelationType } from '../types'
import { relationLabels, nodeLabels } from '../utils/typeMap'

export interface ExportData {
  '头实体名称': string
  '头实体索引': number
  '头实体类型': string
  '关系类型': string
  '尾实体名称': string
  '尾实体索引': number
  '尾实体类型': string
  '预测分数': number
  '关系状态': string
}

const getNodeTypeLabel = (type: NodeType): string => {
  return nodeLabels[type] || type
}

const getRelationTypeLabel = (type: RelationType): string => {
  return relationLabels[type] || type
}

export const exportLinkResultToExcel = (results: LinkResult, filename?: string) => {
  if (!results || results.length === 0) {
    alert('没有数据可导出')
    return
  }

  // 转换数据格式
  const exportData: ExportData[] = results.map((result) => ({
    '头实体名称': result.x_name,
    '头实体索引': result.x_index,
    '头实体类型': getNodeTypeLabel(result.x_type),
    '关系类型': getRelationTypeLabel(result.relation_name),
    '尾实体名称': result.y_name,
    '尾实体索引': result.y_index,
    '尾实体类型': getNodeTypeLabel(result.y_type),
    '预测分数': parseFloat(result.score.toFixed(4)),
    '关系状态': result.type === 'present' ? result.uid ? `存在(${result.uid})`: '存在' : '不存在'
  }))

  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  
  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(exportData)

  // 设置列宽
  const columnWidths = [
    { wch: 25 }, // 头实体名称
    { wch: 12 }, // 头实体索引
    { wch: 15 }, // 头实体类型
    { wch: 20 }, // 关系类型
    { wch: 25 }, // 尾实体名称
    { wch: 12 }, // 尾实体索引
    { wch: 15 }, // 尾实体类型
    { wch: 12 }, // 预测分数
    { wch: 10 }  // 关系状态
  ]
  worksheet['!cols'] = columnWidths

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(workbook, worksheet, '链接预测结果')

  // 生成文件名
  const defaultFilename = `链接预测结果_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
  const finalFilename = filename || defaultFilename

  // 导出文件
  XLSX.writeFile(workbook, finalFilename)
}

export const exportLinkResultToCSV = (results: LinkResult, filename?: string) => {
  if (!results || results.length === 0) {
    alert('没有数据可导出')
    return
  }

  // 转换数据格式
  const exportData: ExportData[] = results.map((result) => ({
    '头实体名称': result.x_name,
    '头实体索引': result.x_index,
    '头实体类型': getNodeTypeLabel(result.x_type),
    '关系类型': getRelationTypeLabel(result.relation_name),
    '尾实体名称': result.y_name,
    '尾实体索引': result.y_index,
    '尾实体类型': getNodeTypeLabel(result.y_type),
    '预测分数': parseFloat(result.score.toFixed(4)),
    '关系状态': result.type === 'present' ? result.uid ? `存在(${result.uid})`: '存在' : '不存在'
  }))

  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  
  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(exportData)

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(workbook, worksheet, '链接预测结果')

  // 生成文件名
  const defaultFilename = `链接预测结果_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`
  const finalFilename = filename || defaultFilename

  // 导出CSV文件
  XLSX.writeFile(workbook, finalFilename, { bookType: 'csv' })
}