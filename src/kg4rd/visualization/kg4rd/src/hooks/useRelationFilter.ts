/**
 * 关系类型过滤Hook
 * 根据节点类型和方向动态过滤可选的关系类型
 */

import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import type { NodeType, RelationType, RelationDirection, MatchRelationType } from '../types'
import { node2relation, relation2node } from '../utils/typeMap'
import { getRelationLabel } from '../utils/i18nTypeMap'

interface RelationOption {
  value: string
  label: string
}

export interface UseRelationFilterProps {
  centerNodeType?: NodeType | string
  direction?: RelationDirection
  includeAll?: boolean // 是否包含"全部关系"选项
}

/**
 * 根据中心节点类型和方向过滤关系类型的Hook
 */
export const useRelationFilter = ({
  centerNodeType,
  direction = 'bidirection',
  includeAll = true
}: UseRelationFilterProps = {}) => {
  const { t } = useTranslation()
  
  const filteredRelationOptions = useMemo(() => {
    const options: RelationOption[] = []
    
    // 添加"全部关系"选项
    if (includeAll) {
      options.push({ value: 'all', label: t('graph.allTypes') })
    }
    
    // 如果没有指定节点类型，返回所有关系类型
    if (!centerNodeType || !(centerNodeType in node2relation)) {
      const allRelationTypes = Object.keys(relation2node) as RelationType[]
      allRelationTypes.forEach(relationType => {
        options.push({
          value: relationType,
          label: getRelationLabel(relationType, t)
        })
      })
      return options
    }
    
    const nodeType = centerNodeType as NodeType
    const nodeRelations = node2relation[nodeType]
    
    if (!nodeRelations) {
      return options
    }
    
    // 根据方向获取可用的关系类型
    let availableRelations: RelationType[] = []
    
    switch (direction) {
      case 'in':
        availableRelations = nodeRelations.in_relation_type
        break
      case 'out':
        availableRelations = nodeRelations.out_relation_type
        break
      case 'bidirection':
        // 双向时包含所有入向和出向关系
        availableRelations = [
          ...nodeRelations.in_relation_type,
          ...nodeRelations.out_relation_type
        ]
        // 去重
        availableRelations = Array.from(new Set(availableRelations))
        break
      default:
        availableRelations = [
          ...nodeRelations.in_relation_type,
          ...nodeRelations.out_relation_type
        ]
        availableRelations = Array.from(new Set(availableRelations))
    }
    
    // 转换为选项格式并排序
    availableRelations
      .sort() // 按字母顺序排序
      .forEach(relationType => {
        options.push({
          value: relationType,
          label: getRelationLabel(relationType, t)
        })
      })
    
    return options
  }, [centerNodeType, direction, includeAll, t])
  
  /**
   * 检查指定的关系类型是否在当前过滤条件下可用
   */
  const isRelationTypeAvailable = useMemo(() => {
    return (relationType: MatchRelationType) => {
      if (relationType === 'all') return includeAll
      return filteredRelationOptions.some(option => option.value === relationType)
    }
  }, [filteredRelationOptions, includeAll])
  
  /**
   * 获取可用关系类型的数量（不包括"全部关系"）
   */
  const availableRelationCount = useMemo(() => {
    return filteredRelationOptions.filter(option => option.value !== 'all').length
  }, [filteredRelationOptions])
  
  /**
   * 根据节点类型获取推荐的默认关系类型
   */
  const getRecommendedRelationType = useMemo(() => {
    return (): MatchRelationType => {
      if (includeAll) return 'all'
      
      // 如果有可用的关系类型，返回第一个
      const firstAvailable = filteredRelationOptions.find(option => option.value !== 'all')
      return (firstAvailable?.value as MatchRelationType) || 'all'
    }
  }, [filteredRelationOptions, includeAll])
  
  return {
    relationOptions: filteredRelationOptions,
    isRelationTypeAvailable,
    availableRelationCount,
    getRecommendedRelationType
  }
}

export default useRelationFilter