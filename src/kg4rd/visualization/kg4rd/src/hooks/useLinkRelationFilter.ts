/**
 * 链接预测关系类型过滤Hook
 * 根据头节点和尾节点类型动态过滤可选的关系类型
 */

import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import type { NodeType, RelationType } from '../types'
import { relation2node } from '../utils/typeMap'
import { getRelationLabel } from '../utils/i18nTypeMap'

interface RelationOption {
  value: string
  label: string
}

export interface UseLinkRelationFilterProps {
  headNodeType?: NodeType | string
  tailNodeType?: NodeType | string
  headType?: 'entities' | 'type'
  tailType?: 'entities' | 'type'
}

/**
 * 根据头尾节点类型过滤链接预测关系类型的Hook
 */
export const useLinkRelationFilter = ({
  headNodeType,
  tailNodeType,
  headType,
  tailType
}: UseLinkRelationFilterProps = {}) => {
  const { t } = useTranslation()
  
  const filteredRelationOptions = useMemo(() => {
    const options: RelationOption[] = []
    
    // 如果头尾节点都是指定实体而不是按类型，返回所有关系类型
    if (headType === 'entities' && tailType === 'entities') {
      const allRelationTypes = Object.keys(relation2node) as RelationType[]
      allRelationTypes
        .sort()
        .forEach(relationType => {
          options.push({
            value: relationType,
            label: getRelationLabel(relationType, t)
          })
        })
      return options
    }
    
    // 获取可用的关系类型
    let availableRelations: RelationType[] = []
    
    // 遍历所有关系类型，检查是否匹配头尾节点类型
    Object.entries(relation2node).forEach(([relationType, nodeTypes]) => {
      const relation = relationType as RelationType
      const { in_type, out_type } = nodeTypes
      
      let headMatches = true
      let tailMatches = true
      
      // 检查头节点匹配
      if (headType === 'type' && headNodeType) {
        headMatches = in_type === headNodeType
      }
      
      // 检查尾节点匹配
      if (tailType === 'type' && tailNodeType) {
        tailMatches = out_type === tailNodeType
      }
      
      // 如果头尾节点都匹配，则该关系类型可用
      if (headMatches && tailMatches) {
        availableRelations.push(relation)
      }
    })
    
    // 去重并排序
    availableRelations = Array.from(new Set(availableRelations)).sort()
    
    // 转换为选项格式
    availableRelations.forEach(relationType => {
      options.push({
        value: relationType,
        label: getRelationLabel(relationType, t)
      })
    })
    
    return options
  }, [headNodeType, tailNodeType, headType, tailType, t])
  
  /**
   * 检查指定的关系类型是否在当前过滤条件下可用
   */
  const isRelationTypeAvailable = useMemo(() => {
    return (relationType: RelationType) => {
      return filteredRelationOptions.some(option => option.value === relationType)
    }
  }, [filteredRelationOptions])
  
  /**
   * 获取可用关系类型的数量
   */
  const availableRelationCount = useMemo(() => {
    return filteredRelationOptions.length
  }, [filteredRelationOptions])
  
  /**
   * 获取推荐的关系类型（基于头尾节点类型的常见组合）
   */
  const getRecommendedRelationTypes = useMemo(() => {
    return (): RelationType[] => {
      if (filteredRelationOptions.length === 0) return []
      
      // 根据头尾节点类型推荐常用关系
      const headType = headNodeType as NodeType
      const tailType = tailNodeType as NodeType
      
      const recommendations: Record<string, RelationType[]> = {
        'drug-disease': ['contraindication', 'indication', 'off-label use'],
        'drug-gene/protein': ['drug_protein'],
        'drug-drug': ['drug_drug'],
        'disease-effect/phenotype': ['disease_phenotype_positive', 'disease_phenotype_negative'],
        'disease-gene/protein': ['disease_protein'],
        'gene/protein-gene/protein': ['protein_protein'],
        'drug-pathway': ['drug_pathway'],
      }
      
      const key = `${headType}-${tailType}`
      const recommended = recommendations[key] || []
      
      // 过滤出实际可用的推荐关系
      const availableRecommended = recommended.filter(rel => 
        isRelationTypeAvailable(rel)
      )
      
      // 如果没有推荐的，返回前3个可用的
      if (availableRecommended.length === 0) {
        return filteredRelationOptions
          .slice(0, 3)
          .map(opt => opt.value as RelationType)
      }
      
      return availableRecommended
    }
  }, [filteredRelationOptions, headNodeType, tailNodeType, isRelationTypeAvailable])
  
  return {
    relationOptions: filteredRelationOptions,
    isRelationTypeAvailable,
    availableRelationCount,
    getRecommendedRelationTypes
  }
}

export default useLinkRelationFilter