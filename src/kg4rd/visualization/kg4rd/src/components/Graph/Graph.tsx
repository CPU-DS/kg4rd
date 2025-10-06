import React, { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { Select, Loading } from '../Common'
import { relationService } from '../../services'
import type { Relation, RelationDirection, MatchRelationType, NodeType, RelationType } from '../../types'
import { ResultCode } from '../../types'
import { useRelationFilter } from '../../hooks/useRelationFilter'
import { getRelationLabel, getNodeLabel } from '../../utils/i18nTypeMap'
import { useTheme } from '../../contexts'
import { useTranslation } from 'react-i18next'

interface GraphProps {
  centerNodeIndex: number
  centerNodeName: string,
  centerNodeType: NodeType
}

interface GraphNode {
  id: string
  name: string
  type: string
  category: number
  value: number
  symbolSize: number
}

interface GraphLink {
  source: string
  target: string
  name: RelationType,
  uid?: string
  lineStyle?: {
    color?: string
    width?: number
  }
}

const Graph: React.FC<GraphProps> = ({
  centerNodeIndex,
  centerNodeName,
  centerNodeType
}) => {
  const { resolvedTheme } = useTheme()
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const [relations, setRelations] = useState<Relation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hop, setHop] = useState(1)
  const [direction, setDirection] = useState<RelationDirection>('bidirection')
  const [relationType, setRelationType] = useState<MatchRelationType>('all')
  const { t } = useTranslation()
  
  // 使用关系过滤Hook
  const { 
    relationOptions, 
    isRelationTypeAvailable, 
    getRecommendedRelationType,
    availableRelationCount 
  } = useRelationFilter({
    centerNodeType: centerNodeType as NodeType,
    direction,
    includeAll: true
  })

  const hopOptions = [
    { value: '1', label: t('graph.hop1') },
    // { value: '2', label: '2跳' },  // 目前只支持1跳
    // { value: '3', label: '3跳' }
  ]

  const directionOptions = [
    { value: 'bidirection', label: t('graph.bidirection') },
    { value: 'out', label: t('graph.outDirection') },
    { value: 'in', label: t('graph.inDirection') }
  ]


  const loadRelations = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await relationService.query({
        node_index: centerNodeIndex,
        direction,
        relation_type: relationType === 'all' ? undefined : relationType,
        hop
      })

      if (response.code === ResultCode.QUERY_OK) {
        setRelations(response.data || [])
      } else {
        setError(response.message || t('graph.errorLoadFailed'))
      }
    } catch (err) {
      setError(t('graph.errorLoadError'))
    } finally {
      setLoading(false)
    }
  }

  // 当方向改变时，检查当前选中的关系类型是否仍然可用
  useEffect(() => {
    if (!isRelationTypeAvailable(relationType)) {
      // 如果当前关系类型不可用，自动切换到推荐的关系类型
      const recommendedType = getRecommendedRelationType()
      setRelationType(recommendedType)
    }
  }, [direction, centerNodeType, isRelationTypeAvailable, relationType, getRecommendedRelationType])

  useEffect(() => {
    loadRelations()
  }, [centerNodeIndex, hop, direction, relationType])

  useEffect(() => {
    if (!chartRef.current || loading) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    // 构建节点和边数据
    const nodeMap = new Map<number, GraphNode>()
    const links: GraphLink[] = []

    // 添加中心节点
    nodeMap.set(centerNodeIndex, {
      id: centerNodeIndex.toString(),
      name: centerNodeName,
      type: getNodeLabel(centerNodeType, t),
      category: 0, // 中心节点类别
      value: 1,
      symbolSize: 40
    })

    // 添加关系节点和边
    relations.forEach((relation) => {
      // 添加 x 节点
      if (!nodeMap.has(relation.x_index)) {
        nodeMap.set(relation.x_index, {
          id: relation.x_index.toString(),
          name: relation.x_name,
          type: getNodeLabel(relation.x_type, t),
          category: 1,
          value: 1,
          symbolSize: 25
        })
      }

      // 添加 y 节点
      if (!nodeMap.has(relation.y_index)) {
        nodeMap.set(relation.y_index, {
          id: relation.y_index.toString(),
          name: relation.y_name,
          type: getNodeLabel(relation.y_type, t),
          category: 1,
          value: 1,
          symbolSize: 25
        })
      }

      // 添加边
      links.push({
        source: relation.x_index.toString(),
        target: relation.y_index.toString(),
        name: relation.relation_name,
        uid: relation.uid,
        lineStyle: {
          color: '#bdc3c7',
          width: 2
        }
      })
    })

    const nodes = Array.from(nodeMap.values())

    // 根据主题设置颜色
    const isDark = resolvedTheme === 'dark'
    const textColor = isDark ? '#e5e7eb' : '#374151'
    const backgroundColor = isDark ? 'transparent' : 'transparent'
    const legendTextColor = isDark ? '#d1d5db' : '#6b7280'
    const borderColor = isDark ? '#374151' : '#fff'
    
    // 配置图表选项
    const option: echarts.EChartsOption = {
      backgroundColor: backgroundColor,
      title: {
        text: `${t('graph.title', { name: centerNodeName })}`,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal',
          color: textColor
        }
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: isDark ? '#374151' : '#fff',
        borderColor: isDark ? '#4b5563' : '#e5e7eb',
        textStyle: {
          color: textColor
        },
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `${params.data.name}<br/>${params.data.type}|${params.data.id}`
          } else if (params.dataType === 'edge') {
            return `${t('graph.relationType')}: ${getRelationLabel(params.data.name as RelationType, t)}${params.data.uid ? `|(${params.data.uid})` : ''}`
          }
          return ''
        }
      },
      legend: {
        data: ['中心节点', '关联节点'],
        bottom: 10,
        left: 'center',
        textStyle: {
          color: legendTextColor
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        draggable: false,
        roam: true,
        data: nodes,
        links: links,
        categories: [
          { name: '中心节点', itemStyle: { color: '#e74c3c' } },
          { name: '关联节点', itemStyle: { color: '#3498db' } }
        ],
        focusNodeAdjacency: true,
        itemStyle: {
          borderColor: borderColor,
          borderWidth: 1,
          shadowBlur: 10,
          shadowColor: isDark ? 'rgba(0, 0, 0, 0.6)' : 'rgba(0, 0, 0, 0.3)'
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 12,
          color: textColor
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10
          }
        },
        force: {
          repulsion: 1000,
          gravity: 0.2,
          edgeLength: [50, 200],
          layoutAnimation: true,
          friction: 0.1  // 快速稳定
        }
      }],
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut'
    }

    chartInstance.current.setOption(option, true)

    chartInstance.current.off('click')
    chartInstance.current.on('click', (params: any) => {
      if (params.dataType === 'node' && params.data.id !== centerNodeIndex.toString()) {
      const nodeId = params.data.id
      if (nodeId) {
        window.open(`/entity/${nodeId}`, '_blank')
      }
      }
    })

    // 响应式处理
    const handleResize = () => {
      chartInstance.current?.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [relations, centerNodeIndex, centerNodeName, loading, resolvedTheme])

  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
        chartInstance.current = null
      }
    }
  }, [])

  return (
    <div className="w-full space-y-4">
      {/* 控制面板 */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 transition-colors">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              { t('graph.hop') }
            </label>
            <Select
              value={hop.toString()}
              onChange={(value) => setHop(parseInt(value))}
              options={hopOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              { t('graph.direction') }
            </label>
            <Select
              value={direction}
              onChange={(value) => setDirection(value as RelationDirection)}
              options={directionOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('graph.relationType')}
              <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                ({t('graph.available', { count: availableRelationCount })})
              </span>
            </label>
            <Select
              value={relationType}
              onChange={(value) => setRelationType(value as MatchRelationType)}
              options={relationOptions}
            />
          </div>
          {/* <div>
            <Button onClick={loadRelations} loading={loading}>
              重新加载
            </Button>
          </div> */}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* 图谱容器 */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 transition-colors">
        {loading ? (
          <div className="flex justify-center items-center h-96">
            <Loading size="lg" />
          </div>
        ) : relations.length === 0 ? (
          <div className="flex justify-center items-center h-96 text-gray-500 dark:text-gray-400">
            暂无关系数据
          </div>
        ) : (
          <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
        )}
      </div>
    </div>
  )
}

export default Graph