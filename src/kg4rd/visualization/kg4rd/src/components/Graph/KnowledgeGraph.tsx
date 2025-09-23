import React, { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { Select, Loading } from '../Common'
import { relationService } from '../../services'
import type { Relation, RelationDirection, MatchRelationType } from '../../types'
import { ResultCode } from '../../types'

interface KnowledgeGraphProps {
  centerNodeIndex: number
  centerNodeName: string
}

interface GraphNode {
  id: string
  name: string
  category: number
  value: number
  symbolSize: number
}

interface GraphLink {
  source: string
  target: string
  name: string
  lineStyle?: {
    color?: string
    width?: number
  }
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  centerNodeIndex,
  centerNodeName
}) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const [relations, setRelations] = useState<Relation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hop, setHop] = useState(1)
  const [direction, setDirection] = useState<RelationDirection>('bidirection')
  const [relationType, setRelationType] = useState<MatchRelationType>('all')

  const hopOptions = [
    { value: '1', label: '1跳' },
    // { value: '2', label: '2跳' },  // 目前只支持1跳
    // { value: '3', label: '3跳' }
  ]

  const directionOptions = [
    { value: 'bidirection', label: '双向' },
    { value: 'out', label: '出度' },
    { value: 'in', label: '入度' }
  ]

  const relationTypeOptions = [
    { value: 'all', label: '全部关系' },
    { value: 'drug_drug', label: '药物-药物' },
    { value: 'protein_protein', label: '蛋白质-蛋白质' },
    { value: 'disease_phenotype_positive', label: '疾病-表型(正向)' },
    { value: 'bioprocess_protein', label: '生物过程-蛋白质' },
    { value: 'cellcomp_protein', label: '细胞组分-蛋白质' },
    { value: 'molfunc_protein', label: '分子功能-蛋白质' },
    { value: 'phenotype_protein', label: '表型-蛋白质' },
    { value: 'disease_protein', label: '疾病-蛋白质' },
    { value: 'disease_disease', label: '疾病-疾病' },
    { value: 'drug_effect', label: '药物-效应' },
    { value: 'pathway_protein', label: '通路-蛋白质' },
    { value: 'bioprocess_bioprocess', label: '生物过程-生物过程' },
    { value: 'drug_protein', label: '药物-蛋白质' },
    { value: 'phenotype_phenotype', label: '表型-表型' },
    { value: 'contraindication', label: '禁忌症' },
    { value: 'molfunc_molfunc', label: '分子功能-分子功能' },
    { value: 'indication', label: '适应症' },
    { value: 'cellcomp_cellcomp', label: '细胞组分-细胞组分' },
    { value: 'drug_pathway', label: '药物-通路' },
    { value: 'pathway_pathway', label: '通路-通路' },
    { value: 'off-label use', label: '超说明书用药' },
    { value: 'disease_phenotype_negative', label: '疾病-表型(负向)' }
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
        setError(response.message || '加载关系数据失败')
      }
    } catch (err) {
      setError('加载关系数据出错')
    } finally {
      setLoading(false)
    }
  }

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
          category: 1,
          value: 1,
          symbolSize: 25
        })
      }

      // 添加边
      links.push({
        source: relation.x_index.toString(),
        target: relation.y_index.toString(),
        name: relation.display_relation_name || relation.relation_name,
        lineStyle: {
          color: '#bdc3c7',
          width: 2
        }
      })
    })

    const nodes = Array.from(nodeMap.values())

    // 配置图表选项
    const option: echarts.EChartsOption = {
      title: {
        text: `${centerNodeName} 的关系图谱`,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `${params.data.name}<br/>索引: ${params.data.id}`
          } else if (params.dataType === 'edge') {
            return `关系: ${params.data.name}`
          }
          return ''
        }
      },
      legend: {
        data: ['中心节点', '关联节点'],
        bottom: 10,
        left: 'center'
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: [
          { name: '中心节点', itemStyle: { color: '#e74c3c' } },
          { name: '关联节点', itemStyle: { color: '#3498db' } }
        ],
        roam: true,
        focusNodeAdjacency: true,
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 12
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
          layoutAnimation: true
        }
      }],
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut'
    }

    chartInstance.current.setOption(option, true)

    // 添加点击事件
    chartInstance.current.off('click')
    chartInstance.current.on('click', (params: any) => {
      if (params.dataType === 'node' && params.data.id !== centerNodeIndex.toString()) {
        // 可以在这里添加节点点击事件，比如跳转到该节点的详情页
        console.log('点击节点:', params.data)
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
  }, [relations, centerNodeIndex, centerNodeName, loading])

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
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              跳数
            </label>
            <Select
              value={hop.toString()}
              onChange={(value) => setHop(parseInt(value))}
              options={hopOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              方向
            </label>
            <Select
              value={direction}
              onChange={(value) => setDirection(value as RelationDirection)}
              options={directionOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              关系类型
            </label>
            <Select
              value={relationType}
              onChange={(value) => setRelationType(value as MatchRelationType)}
              options={relationTypeOptions}
            />
          </div>
          {/* <div>
            <Button onClick={loadRelations} loading={loading}>
              重新加载
            </Button>
          </div> */}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* 图谱容器 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        {loading ? (
          <div className="flex justify-center items-center h-96">
            <Loading size="lg" />
          </div>
        ) : relations.length === 0 ? (
          <div className="flex justify-center items-center h-96 text-gray-500">
            暂无关系数据
          </div>
        ) : (
          <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
        )}
      </div>

      {/* 统计信息 */}
      {!loading && relations.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{relations.length}</div>
              <div className="text-sm text-gray-600">关系数量</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {new Set([...relations.map(r => r.x_index), ...relations.map(r => r.y_index)]).size}
              </div>
              <div className="text-sm text-gray-600">节点数量</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {new Set(relations.map(r => r.relation_name)).size}
              </div>
              <div className="text-sm text-gray-600">关系类型</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default KnowledgeGraph