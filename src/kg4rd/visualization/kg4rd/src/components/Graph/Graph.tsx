import React, { useCallback, useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { Select, Loading, Button } from '../Common'
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

  const downloadFile = useCallback((url: string, filename: string) => {
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }, [])

  const exportAsSVG = useCallback(() => {
    if (!chartInstance.current) return
    const svgDataUrl = chartInstance.current.getDataURL({ type: 'svg' })
    downloadFile(svgDataUrl, `${centerNodeName}_graph.svg`)
  }, [centerNodeName, downloadFile])

  const exportAsHDPNG = useCallback(() => {
    if (!chartInstance.current || !chartRef.current) return
    const svgEl = chartRef.current.querySelector('svg')
    if (!svgEl) return

    const svgData = new XMLSerializer().serializeToString(svgEl)
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)
    const img = new Image()

    const scale = 4
    const width = svgEl.clientWidth * scale
    const height = svgEl.clientHeight * scale

    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')!
      ctx.fillStyle = resolvedTheme === 'dark' ? '#0c1222' : '#ffffff'
      ctx.fillRect(0, 0, width, height)
      ctx.drawImage(img, 0, 0, width, height)
      URL.revokeObjectURL(url)

      canvas.toBlob((blob) => {
        if (!blob) return
        const pngUrl = URL.createObjectURL(blob)
        downloadFile(pngUrl, `${centerNodeName}_graph_hd.png`)
        URL.revokeObjectURL(pngUrl)
      }, 'image/png')
    }
    img.src = url
  }, [centerNodeName, resolvedTheme, downloadFile])

  useEffect(() => {
    if (!isRelationTypeAvailable(relationType)) {
      const recommendedType = getRecommendedRelationType()
      setRelationType(recommendedType)
    }
  }, [direction, centerNodeType, isRelationTypeAvailable, relationType, getRecommendedRelationType])

  useEffect(() => {
    loadRelations()
  }, [centerNodeIndex, hop, direction, relationType])

  useEffect(() => {
    if (!chartRef.current || loading) return

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, undefined, {
        renderer: 'svg',
      })
    }

    const nodeMap = new Map<number, GraphNode>()
    const links: GraphLink[] = []

    nodeMap.set(centerNodeIndex, {
      id: centerNodeIndex.toString(),
      name: centerNodeName,
      type: getNodeLabel(centerNodeType, t),
      category: 0,
      value: 1,
      symbolSize: 40
    })

    relations.forEach((relation) => {
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

      links.push({
        source: relation.x_index.toString(),
        target: relation.y_index.toString(),
        name: relation.relation_name,
        uid: relation.uid,
        lineStyle: {
          color: '#94a3b8',
          width: 1.5
        }
      })
    })

    const nodes = Array.from(nodeMap.values())

    const isDark = resolvedTheme === 'dark'
    const textColor = isDark ? '#e2e8f0' : '#0f172a'
    const legendTextColor = isDark ? '#94a3b8' : '#64748b'
    const borderColor = isDark ? '#1e3048' : '#ffffff'
    const tooltipBg = isDark ? '#111a2e' : '#ffffff'
    const tooltipBorder = isDark ? '#1e3048' : '#e2e8f0'
    
    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      title: {
        text: `${t('graph.title', { name: centerNodeName })}`,
        left: 'center',
        textStyle: {
          fontSize: 15,
          fontWeight: 500,
          color: textColor,
          fontFamily: 'DM Sans, system-ui, sans-serif',
        }
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: tooltipBg,
        borderColor: tooltipBorder,
        borderWidth: 1,
        padding: [10, 14],
        textStyle: {
          color: textColor,
          fontSize: 13,
          fontFamily: 'DM Sans, system-ui, sans-serif',
        },
        extraCssText: 'border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `<strong>${params.data.name}</strong><br/><span style="opacity:0.7">${params.data.type} | #${params.data.id}</span>`
          } else if (params.dataType === 'edge') {
            return `<span style="opacity:0.7">${t('graph.relationType')}:</span> ${getRelationLabel(params.data.name as RelationType, t)}${params.data.uid ? ` <span style="opacity:0.5">(${params.data.uid})</span>` : ''}`
          }
          return ''
        }
      },
      legend: {
        data: ['中心节点', '关联节点'],
        bottom: 10,
        left: 'center',
        textStyle: {
          color: legendTextColor,
          fontFamily: 'DM Sans, system-ui, sans-serif',
          fontSize: 12,
        },
        itemWidth: 12,
        itemHeight: 12,
        itemGap: 20,
      },
      series: [{
        type: 'graph',
        layout: 'force',
        draggable: false,
        roam: true,
        data: nodes,
        links: links,
        categories: [
          { name: '中心节点', itemStyle: { color: '#0d9488' } },
          { name: '关联节点', itemStyle: { color: '#d97706' } }
        ],
        focusNodeAdjacency: true,
        itemStyle: {
          borderColor: borderColor,
          borderWidth: 2,
          shadowBlur: 8,
          shadowColor: isDark ? 'rgba(13, 148, 136, 0.3)' : 'rgba(13, 148, 136, 0.15)'
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 11,
          color: textColor,
          fontFamily: 'DM Sans, system-ui, sans-serif',
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3,
          opacity: 0.6,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4,
            opacity: 1,
          }
        },
        force: {
          repulsion: 1000,
          gravity: 0.2,
          edgeLength: [50, 200],
          layoutAnimation: true,
          friction: 0.1
        }
      }],
      animationDuration: 1200,
      animationEasingUpdate: 'cubicInOut'
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
      {/* Controls */}
      <div className="card p-5">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('graph.hop')}
            </label>
            <Select
              value={hop.toString()}
              onChange={(value) => setHop(parseInt(value))}
              options={hopOptions}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('graph.direction')}
            </label>
            <Select
              value={direction}
              onChange={(value) => setDirection(value as RelationDirection)}
              options={directionOptions}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('graph.relationType')}
              <span className="ml-2 normal-case tracking-normal font-medium"
                    style={{ color: 'var(--color-brand)' }}>
                ({t('graph.available', { count: availableRelationCount })})
              </span>
            </label>
            <Select
              value={relationType}
              onChange={(value) => setRelationType(value as MatchRelationType)}
              options={relationOptions}
            />
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl text-sm"
               style={{
                 background: 'var(--color-error-subtle)',
                 color: 'var(--color-error)',
               }}>
            {error}
          </div>
        )}
      </div>

      {/* Chart container */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-[500px]">
            <Loading size="lg" />
          </div>
        ) : relations.length === 0 ? (
          <div className="flex flex-col justify-center items-center h-[500px]">
            <div className="w-16 h-16 mb-4 rounded-2xl flex items-center justify-center"
                 style={{ background: 'var(--color-surface-raised)' }}>
              <svg className="w-8 h-8" style={{ color: 'var(--color-text-tertiary)' }}
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
              </svg>
            </div>
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              暂无关系数据
            </p>
          </div>
        ) : (
          <>
            <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
            <div className="flex justify-end gap-2 px-5 pb-4">
              <Button variant="outline" size="sm" onClick={exportAsSVG}>
                {t('graph.exportSVG')}
              </Button>
              {/* <Button variant="secondary" size="sm" onClick={exportAsHDPNG}>
                {t('graph.exportPNG')}
              </Button> */}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Graph
