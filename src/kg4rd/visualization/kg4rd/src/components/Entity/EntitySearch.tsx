import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Input, Select, Button, Loading } from '../Common'
import { entityService } from '../../services'
import type { EntityQuery, EntityDTO, MatchNodeType, MatchMode } from '../../types'
import { ResultCode } from '../../types'

const EntitySearch: React.FC = () => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState<'node_index' | 'node_name'>('node_name')
  const [nodeType, setNodeType] = useState<MatchNodeType>('all')
  const [matchMode, setMatchMode] = useState<MatchMode>('contains')
  const [results, setResults] = useState<EntityDTO[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const nodeTypeOptions = [
    { value: 'all', label: '全部类型' },
    { value: 'disease', label: '疾病' },
    { value: 'drug', label: '药物' },
    { value: 'gene/protein', label: '基因/蛋白质' },
    { value: 'pathway', label: '通路' },
    { value: 'effect/phenotype', label: '效应/表型' },
    { value: 'molecular_function', label: '分子功能' },
    { value: 'cellular_component', label: '细胞组分' },
    { value: 'biological_process', label: '生物过程' }
  ]

  const queryTypeOptions = [
    { value: 'node_name', label: '按名称查询' },
    { value: 'node_index', label: '按索引查询' }
  ]

  const matchModeOptions = [
    { value: 'contains', label: '包含' },
    { value: 'strict', label: '精确匹配' },
    { value: 'prefix', label: '前缀匹配' },
    { value: 'regex', label: '正则表达式' }
  ]

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setError('请输入查询内容')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const queryParams: EntityQuery = {
        query_type: queryType,
        query_value: query.trim(),
        node_type: nodeType === 'all' ? undefined : nodeType,
        match_mode: matchMode,
        limit: 50
      }

      const response = await entityService.query(queryParams)
      
      if (response.code === ResultCode.QUERY_OK) {
        setResults(response.data || [])
      } else {
        setError(response.message || '查询失败')
      }
    } catch (err) {
      setError('查询出错，请稍后重试')
    } finally {
      setLoading(false)
    }
  }, [query, queryType, nodeType, matchMode])

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleEntityClick = (entity: EntityDTO) => {
    navigate(`/entity/${entity.node_index}`)
  }

  const getNodeTypeLabel = (type: string) => {
    const option = nodeTypeOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* 搜索配置 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              查询方式
            </label>
            <Select
              value={queryType}
              onChange={(value) => setQueryType(value as 'node_index' | 'node_name')}
              options={queryTypeOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              节点类型
            </label>
            <Select
              value={nodeType}
              onChange={(value) => setNodeType(value as MatchNodeType)}
              options={nodeTypeOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              匹配模式
            </label>
            <Select
              value={matchMode}
              onChange={(value) => setMatchMode(value as MatchMode)}
              options={matchModeOptions}
            />
          </div>
        </div>
        
        <div className="flex gap-3">
          <div className="flex-1">
            <Input
              value={query}
              onChange={setQuery}
              placeholder={queryType === 'node_index' ? '请输入节点索引' : '请输入实体名称'}
              onKeyPress={handleKeyPress}
            />
          </div>
          <Button onClick={handleSearch} loading={loading}>
            搜索
          </Button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* 搜索结果 */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loading size="lg" />
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 animate-fade-in">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              搜索结果 ({results.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {results.map((entity, index) => (
              <div
                key={entity.node_index}
                onClick={() => handleEntityClick(entity)}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-all duration-200 hover:shadow-sm"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-base font-medium text-gray-900 mb-1">
                      {entity.node_name}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>索引: {entity.node_index}</span>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {getNodeTypeLabel(entity.node_type)}
                      </span>
                    </div>
                  </div>
                  <div className="text-gray-400 transform transition-transform duration-200 group-hover:translate-x-1">
                    →
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <div className="text-center py-8 text-gray-500">
          未找到匹配的实体
        </div>
      )}
    </div>
  )
}

export default EntitySearch