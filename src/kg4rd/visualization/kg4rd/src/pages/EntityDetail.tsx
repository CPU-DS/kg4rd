import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, Loading } from '../components/Common'
import { Graph } from '../components/Graph'
import { entityService } from '../services'
import type { Entity, NodeType } from '../types'
import { ResultCode } from '../types'
import { nodeLabels } from '../utils/typeMap'

const EntityDetail: React.FC = () => {
  const { nodeIndex } = useParams<{ nodeIndex: string }>()
  const navigate = useNavigate()
  const [entity, setEntity] = useState<Entity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const getNodeTypeLabel = (type: NodeType) => {
    return nodeLabels[type] || type
  }

  useEffect(() => {
    const loadEntity = async () => {
      if (!nodeIndex) {
        setError('无效的节点索引')
        setLoading(false)
        return
      }

      const index = parseInt(nodeIndex)
      if (isNaN(index)) {
        setError('无效的节点索引')
        setLoading(false)
        return
      }

      try {
        const response = await entityService.getByIndex(index)
        
        if (response.code === ResultCode.QUERY_OK) {
          setEntity(response.data)
        } else {
          setError(response.message || '加载实体信息失败')
        }
      } catch (err) {
        setError('加载实体信息出错')
      } finally {
        setLoading(false)
      }
    }

    loadEntity()
  }, [nodeIndex])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <Loading size="lg" />
      </div>
    )
  }

  if (error || !entity) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center">
        <div className="text-center">
          <div className="text-6xl text-gray-400 mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">加载失败</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button onClick={() => navigate('/') }>
            返回首页
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 返回按钮 */}
        <div className="mb-6">
          <Button variant="primary" onClick={() => navigate('/')}>
            ← 返回首页
          </Button>
        </div>
        
        <div className="space-y-8">
          {/* 实体基本信息 */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {entity.node_name}
                </h2>
                <div className="flex items-center space-x-4">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    {getNodeTypeLabel(entity.node_type)}
                  </span>
                  <span className="text-sm text-gray-500">
                    索引: {entity.node_index}
                  </span>
                  <span className="text-sm text-gray-500">
                    ID: {entity.node_id}
                  </span>
                </div>
              </div>
            </div>

            {/* 基本属性 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-3">基本信息</h3>
                <dl className="space-y-2">
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500">名称:</dt>
                    <dd className="text-sm text-gray-900">{entity.node_name}</dd>
                  </div>
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500">类型:</dt>
                    <dd className="text-sm text-gray-900">{getNodeTypeLabel(entity.node_type)}</dd>
                  </div>
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500">来源:</dt>
                    <dd className="text-sm text-gray-900">{entity.node_source}</dd>
                  </div>
                  <div className="flex flex-col">
                    <dt className="text-sm font-medium text-gray-500 mb-1">来源链接:</dt>
                    <dd className="text-sm ml-5">
                      {entity.node_source_url.map((url, index) => (
                        <a
                          key={index}
                          href={url.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 underline block"
                        >
                          {url.name}
                        </a>
                      ))}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* 扩展信息 */}
              {Object.keys(entity.node_properties).length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">扩展信息</h3>
                  <dl className="space-y-2">
                    {Object.entries(entity.node_properties).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <dt className="text-sm font-medium text-gray-500">{key}:</dt>
                        <dd className="text-sm text-gray-900 mt-1 break-words">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </div>
          </div>

          {/* 知识图谱 */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">知识图谱</h2>
            <Graph
              centerNodeIndex={entity.node_index}
              centerNodeType={entity.node_type}
              centerNodeName={entity.node_name}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default EntityDetail