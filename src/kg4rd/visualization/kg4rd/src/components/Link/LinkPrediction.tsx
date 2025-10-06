import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Select, Button, Loading, Input, InputWithToken, Pagination } from '../Common'
import { linkService } from '../../services'
import type { LinkRequest, LinkResult, NodeType, RelationType } from '../../types'
import { ResultCode } from '../../types'
import { exportLinkResultToExcel, exportLinkResultToCSV } from '../../utils/exportUtils'
import { useLinkRelationFilter } from '../../hooks/useLinkRelationFilter'

const LinkPrediction: React.FC = () => {
  const { t } = useTranslation()
  const [modelNames, setModelNames] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [headType, setHeadType] = useState<'entities' | 'type'>('entities')
  const [headEntities, setHeadEntities] = useState<string[]>([])
  const [headNodeType, setHeadNodeType] = useState<NodeType>('disease')
  const [tailType, setTailType] = useState<'entities' | 'type'>('entities')
  const [tailEntities, setTailEntities] = useState<string[]>([])
  const [tailNodeType, setTailNodeType] = useState<NodeType>('drug')
  const [relationTypes, setRelationTypes] = useState<string[]>([])
  const [results, setResults] = useState<LinkResult>([])
  const [loading, setLoading] = useState(false)
  const [modelsLoading, setModelsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // 限制数量设置
  const [limitType, setLimitType] = useState<'unlimited' | 'custom'>('custom')
  const [customLimit, setCustomLimit] = useState('100')
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  // 使用链接关系过滤Hook
  const { 
    relationOptions, 
    isRelationTypeAvailable,
    availableRelationCount
  } = useLinkRelationFilter({
    headNodeType: headType === 'type' ? headNodeType : undefined,
    tailNodeType: tailType === 'type' ? tailNodeType : undefined,
    headType,
    tailType
  })

  const nodeTypeOptions = [
    { value: 'disease', label: t('nodeTypes.disease') },
    { value: 'drug', label: t('nodeTypes.drug') },
    { value: 'gene/protein', label: t('nodeTypes.gene/protein') },
    { value: 'pathway', label: t('nodeTypes.pathway') },
    { value: 'effect/phenotype', label: t('nodeTypes.effect/phenotype') },
    { value: 'molecular_function', label: t('nodeTypes.molecular_function') },
    { value: 'cellular_component', label: t('nodeTypes.cellular_component') },
    { value: 'biological_process', label: t('nodeTypes.biological_process') }
  ]


  const headTypeOptions = [
    { value: 'entities', label: t('link.prediction.specifyEntities') },
    { value: 'type', label: t('link.prediction.byType') }
  ]

  const tailTypeOptions = [
    { value: 'entities', label: t('link.prediction.specifyEntities') },
    { value: 'type', label: t('link.prediction.byType') }
  ]

  useEffect(() => {
    let isMounted = true
    let retryCount = 0

    const loadModelNamesWithRetry = async () => {
      try {
        const response = await linkService.getModelNames()
        if (!isMounted) return
        if (response.code === ResultCode.QUERY_OK) {
          setModelNames(response.data || [])
          if (response.data && response.data.length > 0) {
            setSelectedModel(response.data[0])
          }
          setModelsLoading(false)
        } else {
          // 失败，递增重试
          retryCount += 1
          const delay = retryCount * 1000
          if (retryCount <= 10) {
            setTimeout(loadModelNamesWithRetry, delay)
          } else {
            setError(t('link.prediction.errorLoadModels'))
            setModelsLoading(false)
          }
        }
      } catch (err) {
        if (!isMounted) return
        retryCount += 1
        const delay = retryCount * 1000
        if (retryCount <= 10) {
          setTimeout(loadModelNamesWithRetry, delay)
        } else {
          setError(t('link.prediction.errorLoadModelsError'))
          setModelsLoading(false)
        }
      }
    }

    loadModelNamesWithRetry()

    return () => {
      isMounted = false
    }
  }, [])

  // 当头尾节点类型或选择方式变化时，只保留有效的关系类型选择
  useEffect(() => {
    // 只保留当前选中的有效关系类型，不自动添加推荐的关系类型
    const validCurrentRelations = relationTypes.filter(rel => 
      isRelationTypeAvailable(rel as RelationType)
    )
    
    // 如果当前选中的关系类型有变化，更新选择
    if (validCurrentRelations.length !== relationTypes.length) {
      setRelationTypes(validCurrentRelations)
    }
  }, [headType, headNodeType, tailType, tailNodeType, isRelationTypeAvailable, relationTypes])

  const handleRelationTypeChange = (tokens: string[]) => {
    setRelationTypes(tokens)
  }

  const handleLimitTypeChange = (type: 'unlimited' | 'custom') => {
    setLimitType(type)
  }

  const handleCustomLimitChange = (value: string) => {
    // 只允许输入数字
    if (value === '' || /^\d+$/.test(value)) {
      setCustomLimit(value)
    }
  }

  function truncateString(str: string, length = 40) {
    if (str.length <= length) {
      return str
    }
    return str.slice(0, length) + '...'
  }

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

  // 导出功能
  const handleExportExcel = () => {
    exportLinkResultToExcel(results, t)
  }

  const handleExportCSV = () => {
    exportLinkResultToCSV(results, t)
  }

  // 跳转到实体详情页
  const handleEntityClick = (nodeIndex: number) => {
    window.open(`/entity/${nodeIndex}`, '_blank', 'noopener,noreferrer')
  }

  const handlePredict = useCallback(async () => {
    if (!selectedModel) {
      setError(t('link.prediction.errorSelectModel'))
      return
    }

    if (relationTypes.length === 0) {
      setError(t('link.prediction.errorSelectRelation'))
      return
    }

    if (limitType === 'custom' && (!customLimit || parseInt(customLimit) <= 0)) {
      setError(t('link.prediction.errorInvalidLimit'))
      return
    }

    let headParam: number[] | NodeType
    let tailParam: number[] | NodeType

    if (headType === 'entities') {
      if (headEntities.length === 0) {
        setError(t('link.prediction.errorHeadIndex'))
        return
      }
      try {
        headParam = headEntities.map(id => parseInt(id)).filter(id => !isNaN(id))
        if (headParam.length === 0) {
          setError(t('link.prediction.errorHeadFormat'))
          return
        }
      } catch {
        setError(t('link.prediction.errorHeadFormat'))
        return
      }
    } else {
      headParam = headNodeType
    }

    if (tailType === 'entities') {
      if (tailEntities.length === 0) {
        setError(t('link.prediction.errorTailIndex'))
        return
      }
      try {
        tailParam = tailEntities.map(id => parseInt(id)).filter(id => !isNaN(id))
        if (tailParam.length === 0) {
          setError(t('link.prediction.errorTailFormat'))
          return
        }
      } catch {
        setError(t('link.prediction.errorTailFormat'))
        return
      }
    } else {
      tailParam = tailNodeType
    }

    setLoading(true)
    setError(null)
    resetPagination() // 重置分页

    try {
      const request: LinkRequest = {
        head: headParam,
        rel: relationTypes as RelationType[],
        tail: tailParam,
        model_name: selectedModel,
        ...(limitType === 'custom' && customLimit ? { limit: parseInt(customLimit) } : {})
      }

      const response = await linkService.predict(request)
      
      if (response.code === ResultCode.QUERY_OK) {
        setResults(response.data || [])
      } else {
        setError(response.message || t('link.prediction.errorPredictFailed'))
      }
    } catch (err) {
      setError(t('link.prediction.errorPredictError'))
    } finally {
      setLoading(false)
    }
  }, [selectedModel, headType, headEntities, headNodeType, tailType, tailEntities, tailNodeType, relationTypes, limitType, customLimit, t])

  const getNodeTypeLabel = (type: string) => {
    const option = nodeTypeOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  const getRelationTypeLabel = (type: string) => {
    const option = relationOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  if (modelsLoading) {
    return (
      <div className="flex justify-center py-8">
        <Loading size="lg" />
      </div>
    )
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* 预测配置 */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-6">{t('link.prediction.title')}</h3>
        
        <div className="space-y-6">
          {/* 模型选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('link.prediction.model')}
            </label>
            <Select
              value={selectedModel}
              onChange={setSelectedModel}
              options={modelNames.map(name => ({ value: name, label: ''+name }))}
              placeholder={t('link.prediction.modelPlaceholder')}
            />
          </div>

          {/* 头实体配置 */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-xl p-4">
            <h4 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-4">{t('link.prediction.headEntity')}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('link.prediction.configMethod')}
                </label>
                <Select
                  value={headType}
                  onChange={(value) => setHeadType(value as 'entities' | 'type')}
                  options={headTypeOptions}
                />
              </div>
              
              {headType === 'entities' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('link.prediction.entityIndex')}
                  </label>
                  <InputWithToken
                    selectedTokens={headEntities}
                    onChange={setHeadEntities}
                    options={[]}
                    placeholder={t('link.prediction.entityIndexPlaceholder')}
                    allowCustomInput={true}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('link.prediction.nodeType')}
                  </label>
                  <Select
                    value={headNodeType}
                    onChange={(value) => setHeadNodeType(value as NodeType)}
                    options={nodeTypeOptions}
                  />
                </div>
              )}
            </div>
          </div>

          {/* 尾实体配置 */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-xl p-4">
            <h4 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-4">{t('link.prediction.tailEntity')}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('link.prediction.configMethod')}
                </label>
                <Select
                  value={tailType}
                  onChange={(value) => setTailType(value as 'entities' | 'type')}
                  options={tailTypeOptions}
                />
              </div>
              
              {tailType === 'entities' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('link.prediction.entityIndex')}
                  </label>
                  <InputWithToken
                    selectedTokens={tailEntities}
                    onChange={setTailEntities}
                    options={[]}
                    placeholder={t('link.prediction.entityIndexPlaceholder')}
                    allowCustomInput={true}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('link.prediction.nodeType')}
                  </label>
                  <Select
                    value={tailNodeType}
                    onChange={(value) => setTailNodeType(value as NodeType)}
                    options={nodeTypeOptions}
                  />
                </div>
              )}
            </div>
          </div>

          {/* 关系类型选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('link.prediction.relationType')} 
              <span className="ml-2 text-xs text-blue-600 dark:text-blue-400">
                {t('link.prediction.relationAvailable', { available: availableRelationCount, selected: relationTypes.length })}
              </span>
            </label>
            {availableRelationCount === 0 ? (
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-lg text-yellow-700 dark:text-yellow-400 text-sm">
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {t('link.prediction.relationWarning')}
                </div>
              </div>
            ) : (
              <InputWithToken
                selectedTokens={relationTypes}
                onChange={handleRelationTypeChange}
                options={relationOptions}
                placeholder={t('link.prediction.relationPlaceholder')}
              />
            )}
          </div>

          {/* 结果数量限制 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('link.prediction.resultLimit')}
              </label>
              <div className="flex items-center flex-wrap gap-3">
                <label className="flex items-center cursor-pointer whitespace-nowrap">
                  <input
                    type="radio"
                    name="limitType"
                    value="unlimited"
                    checked={limitType === 'unlimited'}
                    onChange={() => handleLimitTypeChange('unlimited')}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t('link.prediction.unlimited')}</span>
                </label>
                <label className="flex items-center cursor-pointer whitespace-nowrap">
                  <input
                    type="radio"
                    name="limitType"
                    value="custom"
                    checked={limitType === 'custom'}
                    onChange={() => handleLimitTypeChange('custom')}
                    className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t('link.prediction.customLimit')}</span>
                </label>
                
                {limitType === 'custom' && (
                  <>
                    <Input
                      value={customLimit}
                      onChange={handleCustomLimitChange}
                      placeholder={t('link.prediction.limitPlaceholder')}
                      className="w-24"
                    />
                  </>
                )}
              </div>
            </div>
          </div>

          {/* 配置总结 */}
          {/* <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
            <h4 className="font-medium text-gray-900 mb-3">当前配置总结:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p><span className="font-medium">头节点:</span> 
                  {headType === 'entities' 
                    ? `指定实体 (${headEntities.split(',').filter(e => e.trim()).length} 个)` 
                    : `按类型 (${getNodeTypeLabel(headNodeType)})`}
                </p>
                <p><span className="font-medium">尾节点:</span> 
                  {tailType === 'entities' 
                    ? `指定实体 (${tailEntities.split(',').filter(e => e.trim()).length} 个)` 
                    : `按类型 (${getNodeTypeLabel(tailNodeType)})`}
                </p>
              </div>
              <div>
                <p><span className="font-medium">关系类型:</span> {relationTypes.length} / {availableRelationCount} 个</p>
                <p><span className="font-medium">预测模型:</span> {selectedModel}</p>
              </div>
            </div>
            <div className="mt-3">
              <p className="font-medium mb-2">选中的关系类型:</p>
              {relationTypes.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {relationTypes.slice(0, 6).map(rel => (
                    <span key={rel} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {getRelationTypeLabel(rel)}
                    </span>
                  ))}
                  {relationTypes.length > 6 && (
                    <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                      +{relationTypes.length - 6} 个更多
                    </span>
                  )}
                </div>
              ) : (
                <div className="text-gray-500 text-sm italic">
                  请选择要预测的关系类型
                </div>
              )}
            </div>
          </div> */}

          <div className="flex justify-center">
            <Button 
              onClick={handlePredict} 
              loading={loading} 
              size="lg"
              disabled={relationTypes.length === 0 || !selectedModel}
            >
              {t('link.prediction.predictButton')}
            </Button>
          </div>

          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* 预测结果 */}
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
                {t('link.prediction.results')} ({t('common.totalResults', { count: results.length })})
              </h3>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportExcel}
                    className="text-sm"
                  >
                    {t('link.prediction.exportExcel')}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportCSV}
                    className="text-sm"
                  >
                    {t('link.prediction.exportCSV')}
                  </Button>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t('common.page', { current: currentPage, total: totalPages })}
                </div>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {t('link.prediction.headEntityCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {t('link.prediction.relationCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {t('link.prediction.tailEntityCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {t('link.prediction.scoreCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {t('link.prediction.typeCol')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {paginatedResults.map((result, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.x_index)}
                          className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline cursor-pointer text-left"
                        >
                          {truncateString(result.x_name)}
                        </button>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {getNodeTypeLabel(result.x_type)} | {t('common.index')}: {result.x_index}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300">
                        {getRelationTypeLabel(result.relation_name)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.y_index)}
                          className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline cursor-pointer text-left"
                        >
                          {truncateString(result.y_name)}
                        </button>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {getNodeTypeLabel(result.y_type)} | {t('common.index')}: {result.y_index}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mr-2">
                          {result.score.toFixed(4)}
                        </div>
                        <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(result.score * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        result.type === 'present' 
                          ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300' 
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                      }`}>
                        {result.type === 'present' ? result.uid ? `${t('link.prediction.typePresent')}(${result.uid})`: t('link.prediction.typePresent') : t('link.prediction.typeAbsent')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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

      {!loading && results.length === 0 && selectedModel && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          {t('common.noResults')}
        </div>
      )}
    </div>
  )
}

export default LinkPrediction