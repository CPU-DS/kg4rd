import * as XLSX from 'xlsx'
import { toSvg, toPng } from 'html-to-image'
import type { TFunction } from 'i18next'
import type { LinkResult } from '../types'
import { getNodeLabel, getRelationLabel } from './i18nTypeMap'

export interface ExportData {
  [key: string]: string | number
}

export const exportLinkResultToExcel = (results: LinkResult, t: TFunction, filename?: string) => {
  if (!results || results.length === 0) {
    alert(t('common.noData'))
    return
  }

  // 转换数据格式
  const exportData: ExportData[] = results.map((result) => ({
    [t('link.prediction.headEntityCol')]: result.x_name,
    [t('common.index') + ' (' + t('link.prediction.headEntityCol') + ')']: result.x_index,
    [t('common.type') + ' (' + t('link.prediction.headEntityCol') + ')']: getNodeLabel(result.x_type, t),
    [t('link.prediction.relationCol')]: getRelationLabel(result.relation_name, t),
    [t('link.prediction.tailEntityCol')]: result.y_name,
    [t('common.index') + ' (' + t('link.prediction.tailEntityCol') + ')']: result.y_index,
    [t('common.type') + ' (' + t('link.prediction.tailEntityCol') + ')']: getNodeLabel(result.y_type, t),
    [t('link.prediction.scoreCol')]: parseFloat(result.score.toFixed(4)),
    [t('link.prediction.typeCol')]: result.type === 'present' ? result.uid ? `${t('link.prediction.typePresent')}(${result.uid})`: t('link.prediction.typePresent') : t('link.prediction.typeAbsent')
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
  XLSX.utils.book_append_sheet(workbook, worksheet, t('link.prediction.results'))

  // 生成文件名
  const defaultFilename = `${t('link.prediction.results')}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
  const finalFilename = filename || defaultFilename

  // 导出文件
  XLSX.writeFile(workbook, finalFilename)
}

export const exportLinkResultToCSV = (results: LinkResult, t: TFunction, filename?: string) => {
  if (!results || results.length === 0) {
    alert(t('common.noData'))
    return
  }

  // 转换数据格式
  const exportData: ExportData[] = results.map((result) => ({
    [t('link.prediction.headEntityCol')]: result.x_name,
    [t('common.index') + ' (' + t('link.prediction.headEntityCol') + ')']: result.x_index,
    [t('common.type') + ' (' + t('link.prediction.headEntityCol') + ')']: getNodeLabel(result.x_type, t),
    [t('link.prediction.relationCol')]: getRelationLabel(result.relation_name, t),
    [t('link.prediction.tailEntityCol')]: result.y_name,
    [t('common.index') + ' (' + t('link.prediction.tailEntityCol') + ')']: result.y_index,
    [t('common.type') + ' (' + t('link.prediction.tailEntityCol') + ')']: getNodeLabel(result.y_type, t),
    [t('link.prediction.scoreCol')]: parseFloat(result.score.toFixed(4)),
    [t('link.prediction.typeCol')]: result.type === 'present' ? result.uid ? `${t('link.prediction.typePresent')}(${result.uid})`: t('link.prediction.typePresent') : t('link.prediction.typeAbsent')
  }))

  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  
  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(exportData)

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(workbook, worksheet, t('link.prediction.results'))

  // 生成文件名
  const defaultFilename = `${t('link.prediction.results')}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`
  const finalFilename = filename || defaultFilename

  // 导出CSV文件
  XLSX.writeFile(workbook, finalFilename, { bookType: 'csv' })
}

const downloadDataUrl = (dataUrl: string, filename: string) => {
  const a = document.createElement('a')
  a.href = dataUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const EXPORT_OPTIONS = {
  cacheBust: true,
  filter: (node: HTMLElement) => {
    return !node.hasAttribute?.('data-export-ignore')
  },
}

export const exportPageAsSvg = async (
  node: HTMLElement,
  filename: string = 'page.svg'
) => {
  const dataUrl = await toSvg(node, {
    ...EXPORT_OPTIONS,
    backgroundColor: getComputedStyle(node).backgroundColor || '#ffffff',
  })
  downloadDataUrl(dataUrl, filename)
}

export const exportPageAsPng = async (
  node: HTMLElement,
  filename: string = 'page_hd.png',
  scale: number = 3
) => {
  const dataUrl = await toPng(node, {
    ...EXPORT_OPTIONS,
    pixelRatio: scale,
    backgroundColor: getComputedStyle(node).backgroundColor || '#ffffff',
  })
  downloadDataUrl(dataUrl, filename)
}
