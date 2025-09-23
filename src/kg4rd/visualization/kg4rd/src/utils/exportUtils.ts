import * as XLSX from 'xlsx'
import type { LinkResult } from '../types'

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

const nodeTypeLabels: Record<string, string> = {
  'disease': '疾病',
  'drug': '药物',
  'gene/protein': '基因/蛋白质',
  'pathway': '通路',
  'effect/phenotype': '效应/表型',
  'molecular_function': '分子功能',
  'cellular_component': '细胞组分',
  'biological_process': '生物过程'
}

const relationTypeLabels: Record<string, string> = {
  'drug_drug': '药物-药物',
  'protein_protein': '蛋白质-蛋白质',
  'disease_phenotype_positive': '疾病-表型(正向)',
  'bioprocess_protein': '生物过程-蛋白质',
  'cellcomp_protein': '细胞组分-蛋白质',
  'molfunc_protein': '分子功能-蛋白质',
  'phenotype_protein': '表型-蛋白质',
  'disease_protein': '疾病-蛋白质',
  'disease_disease': '疾病-疾病',
  'drug_effect': '药物-效应',
  'pathway_protein': '通路-蛋白质',
  'bioprocess_bioprocess': '生物过程-生物过程',
  'drug_protein': '药物-蛋白质',
  'phenotype_phenotype': '表型-表型',
  'contraindication': '禁忌症',
  'molfunc_molfunc': '分子功能-分子功能',
  'indication': '适应症',
  'cellcomp_cellcomp': '细胞组分-细胞组分',
  'drug_pathway': '药物-通路',
  'pathway_pathway': '通路-通路',
  'off-label use': '超说明书用药',
  'disease_phenotype_negative': '疾病-表型(负向)'
}

const getNodeTypeLabel = (type: string): string => {
  return nodeTypeLabels[type] || type
}

const getRelationTypeLabel = (type: string): string => {
  return relationTypeLabels[type] || type
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