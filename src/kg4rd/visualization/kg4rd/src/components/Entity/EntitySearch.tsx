import React, { useState, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Input, Select, Button, Loading, Pagination } from '../Common'
import { entityService } from '../../services'
import type { EntityQuery, EntityDTO, MatchNodeType, MatchMode } from '../../types'
import { ResultCode } from '../../types'

const EntitySearch: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState<'node_index' | 'node_name'>('node_name')
  const [nodeType, setNodeType] = useState<MatchNodeType>('all')
  const [matchMode, setMatchMode] = useState<MatchMode>('contains')
  const [results, setResults] = useState<EntityDTO[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  const nodeTypeOptions = [
    { value: 'all', label: t('nodeTypes.all') },
    { value: 'disease', label: t('nodeTypes.disease') },
    { value: 'drug', label: t('nodeTypes.drug') },
    { value: 'gene/protein', label: t('nodeTypes.gene/protein') },
    { value: 'pathway', label: t('nodeTypes.pathway') },
    { value: 'effect/phenotype', label: t('nodeTypes.effect/phenotype') },
    { value: 'molecular_function', label: t('nodeTypes.molecular_function') },
    { value: 'cellular_component', label: t('nodeTypes.cellular_component') },
    { value: 'biological_process', label: t('nodeTypes.biological_process') }
  ]

  const queryTypeOptions = [
    { value: 'node_name', label: t('entity.search.queryByName') },
    { value: 'node_index', label: t('entity.search.queryByIndex') }
  ]

  const matchModeOptions = [
    { value: 'contains', label: t('entity.search.matchContains') },
    { value: 'strict', label: t('entity.search.matchStrict') },
    { value: 'prefix', label: t('entity.search.matchPrefix') },
    { value: 'regex', label: t('entity.search.matchRegex') }
  ]

  // 分页数据计算
  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    const endIndex = startIndex + pageSize
    return results.slice(startIndex, endIndex)
  }, [results, currentPage, pageSize])

  const totalPages = Math.ceil(results.length / pageSize)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1) // 重置到第一页
  }

  // 重置分页状态
  const resetPagination = () => {
    setCurrentPage(1)
  }

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setError(t('entity.search.errorEmpty'))
      setResults([])  // 清空之前的内容
      return
    }

    setLoading(true)
    setError(null)
    resetPagination() // 重置分页

    try {
      const queryParams: EntityQuery = {
        query_type: queryType,
        query_value: query.trim(),
        node_type: nodeType === 'all' ? undefined : nodeType,
        match_mode: matchMode
      }

      const response = await entityService.query(queryParams)
      
      if (response.code === ResultCode.QUERY_OK) {
        setResults(response.data || [])
      } else {
        setError(response.message || t('entity.search.errorQuery'))
      }
    } catch (err) {
      setError(t('entity.search.errorQuery'))
    } finally {
      setLoading(false)
    }
  }, [query, queryType, nodeType, matchMode, t])

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

  const optimizeNodeName = (name: string) => {
  // 如果名称中不包含空格，则将全部字母大写，如果包含空格，则将首字母和空格后的第一个字母大写
  if (!name.includes(' ')) {
    return name.toUpperCase()
  } else {
    return name.replace(/\b\w/g, (char) => char.toUpperCase())
  }
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* 搜索配置 */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('entity.search.queryMethod')}
            </label>
            <Select
              value={queryType}
              onChange={(value) => setQueryType(value as 'node_index' | 'node_name')}
              options={queryTypeOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('entity.search.nodeType')}
            </label>
            <Select
              value={nodeType}
              onChange={(value) => setNodeType(value as MatchNodeType)}
              options={nodeTypeOptions}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('entity.search.matchMode')}
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
              placeholder={queryType === 'node_index' ? t('entity.search.placeholderIndex') : t('entity.search.placeholder')}
              onKeyPress={handleKeyPress}
            />
          </div>
          <Button className='px-10' onClick={handleSearch} loading={loading}>
            {t('entity.search.searchButton')}
          </Button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
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
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 animate-fade-in transition-colors">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                {t('entity.search.searchResults')} ({t('common.totalResults', { count: results.length })})
              </h3>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {t('common.page', { current: currentPage, total: totalPages })}
              </div>
            </div>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {paginatedResults.map((entity, index) => (
              <div
                key={entity.node_index}
                onClick={() => handleEntityClick(entity)}
                className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-all duration-200 hover:shadow-sm"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-1">
                      {optimizeNodeName(entity.node_name)}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>{t('common.index')}: {entity.node_index}</span>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300">
                        {getNodeTypeLabel(entity.node_type)}
                      </span>
                    </div>
                  </div>
                  <div className="text-gray-400 dark:text-gray-500 transform transition-transform duration-200 group-hover:translate-x-1">
                    →
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* 分页组件 */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalItems={results.length}
              itemsPerPage={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              pageSizeOptions={[10, 20, 50, 100]}
            />
          </div>
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          {t('entity.search.noResults')}
        </div>
      )}
    </div>
  )
}

export default EntitySearch