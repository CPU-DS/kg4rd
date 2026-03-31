import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Select, Button, Loading, Input, InputWithToken, EntitySearchInput, Pagination } from '../Common'
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
  const [headEntities, setHeadEntities] = useState<{ index: number; name: string; type: string }[]>([])
  const [headNodeType, setHeadNodeType] = useState<NodeType>('disease')
  const [tailType, setTailType] = useState<'entities' | 'type'>('entities')
  const [tailEntities, setTailEntities] = useState<{ index: number; name: string; type: string }[]>([])
  const [tailNodeType, setTailNodeType] = useState<NodeType>('drug')
  const [relationTypes, setRelationTypes] = useState<string[]>([])
  const [results, setResults] = useState<LinkResult>([])
  const [loading, setLoading] = useState(false)
  const [modelsLoading, setModelsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [limitType, setLimitType] = useState<'unlimited' | 'custom'>('custom')
  const [customLimit, setCustomLimit] = useState('100')
  
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

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

  useEffect(() => {
    const validCurrentRelations = relationTypes.filter(rel => 
      isRelationTypeAvailable(rel as RelationType)
    )
    
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
    setCurrentPage(1)
  }

  const resetPagination = () => {
    setCurrentPage(1)
  }

  const handleExportExcel = () => {
    exportLinkResultToExcel(results, t)
  }

  const handleExportCSV = () => {
    exportLinkResultToCSV(results, t)
  }

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
      headParam = headEntities.map(e => e.index)
    } else {
      headParam = headNodeType
    }

    if (tailType === 'entities') {
      if (tailEntities.length === 0) {
        setError(t('link.prediction.errorTailIndex'))
        return
      }
      tailParam = tailEntities.map(e => e.index)
    } else {
      tailParam = tailNodeType
    }

    setLoading(true)
    setError(null)
    resetPagination()

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
      <div className="flex justify-center py-12">
        <Loading size="lg" />
      </div>
    )
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Prediction config */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-1 h-5 rounded-full" style={{ background: 'var(--color-brand)' }} />
          <h3 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {t('link.prediction.title')}
          </h3>
        </div>
        
        <div className="space-y-6">
          {/* Model selection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('link.prediction.model')}
            </label>
            <Select
              value={selectedModel}
              onChange={setSelectedModel}
              options={modelNames.map(name => ({ value: name, label: ''+name }))}
              placeholder={t('link.prediction.modelPlaceholder')}
            />
          </div>

          {/* Head entity */}
          <div className="card-inner p-5">
            <h4 className="text-sm font-semibold mb-4" style={{ color: 'var(--color-text-primary)' }}>
              {t('link.prediction.headEntity')}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                       style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
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
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                         style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.entitySelect')}
                  </label>
                  <EntitySearchInput
                    selectedEntities={headEntities}
                    onChange={setHeadEntities}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                         style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
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

          {/* Tail entity */}
          <div className="card-inner p-5">
            <h4 className="text-sm font-semibold mb-4" style={{ color: 'var(--color-text-primary)' }}>
              {t('link.prediction.tailEntity')}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                       style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
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
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                         style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.entitySelect')}
                  </label>
                  <EntitySearchInput
                    selectedEntities={tailEntities}
                    onChange={setTailEntities}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                         style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
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

          {/* Relation type */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('link.prediction.relationType')} 
              <span className="ml-2 normal-case tracking-normal font-medium"
                    style={{ color: 'var(--color-brand)' }}>
                {t('link.prediction.relationAvailable', { available: availableRelationCount, selected: relationTypes.length })}
              </span>
            </label>
            {availableRelationCount === 0 ? (
              <div className="p-3 rounded-xl text-sm flex items-center gap-2"
                   style={{
                     background: 'var(--color-warning-subtle)',
                     color: 'var(--color-warning)',
                   }}>
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {t('link.prediction.relationWarning')}
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

          {/* Result limit */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                     style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                {t('link.prediction.resultLimit')}
              </label>
              <div className="flex items-center flex-wrap gap-4">
                <label className="flex items-center cursor-pointer gap-2">
                  <input
                    type="radio"
                    name="limitType"
                    value="unlimited"
                    checked={limitType === 'unlimited'}
                    onChange={() => handleLimitTypeChange('unlimited')}
                    className="w-4 h-4 cursor-pointer"
                    style={{ accentColor: 'var(--color-brand)' }}
                  />
                  <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    {t('link.prediction.unlimited')}
                  </span>
                </label>
                <label className="flex items-center cursor-pointer gap-2">
                  <input
                    type="radio"
                    name="limitType"
                    value="custom"
                    checked={limitType === 'custom'}
                    onChange={() => handleLimitTypeChange('custom')}
                    className="w-4 h-4 cursor-pointer"
                    style={{ accentColor: 'var(--color-brand)' }}
                  />
                  <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    {t('link.prediction.customLimit')}
                  </span>
                </label>
                
                {limitType === 'custom' && (
                  <Input
                    value={customLimit}
                    onChange={handleCustomLimitChange}
                    placeholder={t('link.prediction.limitPlaceholder')}
                    className="w-24"
                  />
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-center pt-2">
            <Button 
              onClick={handlePredict} 
              loading={loading} 
              size="lg"
              disabled={relationTypes.length === 0 || !selectedModel}
              className="px-12"
            >
              {t('link.prediction.predictButton')}
            </Button>
          </div>

          {error && (
            <div className="p-3 rounded-xl text-sm"
                 style={{
                   background: 'var(--color-error-subtle)',
                   color: 'var(--color-error)',
                 }}>
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {loading && (
        <div className="flex justify-center py-12">
          <Loading size="lg" />
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="card animate-fade-in overflow-hidden">
          <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--color-border)' }}>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                {t('link.prediction.results')}
                <span className="ml-2 text-sm font-normal" style={{ color: 'var(--color-text-tertiary)' }}>
                  {t('common.totalResults', { count: results.length })}
                </span>
              </h3>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={handleExportExcel}>
                    {t('link.prediction.exportExcel')}
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleExportCSV}>
                    {t('link.prediction.exportCSV')}
                  </Button>
                </div>
                <span className="text-xs mono" style={{ color: 'var(--color-text-tertiary)' }}>
                  {t('common.page', { current: currentPage, total: totalPages })}
                </span>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr style={{ background: 'var(--color-surface-raised)' }}>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.headEntityCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.relationCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.tailEntityCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.scoreCol')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
                    {t('link.prediction.typeCol')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedResults.map((result, index) => (
                  <tr key={index}
                      className="transition-colors duration-150"
                      style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'var(--color-surface-raised)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent'
                      }}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.x_index)}
                          className="text-sm font-medium cursor-pointer text-left transition-colors"
                          style={{ color: 'var(--color-brand)' }}
                        >
                          {truncateString(result.x_name, length=20)}
                        </button>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                            {getNodeTypeLabel(result.x_type)}
                          </span>
                          <span className="mono text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                            #{result.x_index}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="tag-accent">
                        {getRelationTypeLabel(result.relation_name)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <button
                          onClick={() => handleEntityClick(result.y_index)}
                          className="text-sm font-medium cursor-pointer text-left transition-colors"
                          style={{ color: 'var(--color-brand)' }}
                        >
                          {truncateString(result.y_name)}
                        </button>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                            {getNodeTypeLabel(result.y_type)}
                          </span>
                          <span className="mono text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                            #{result.y_index}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2.5">
                        <span className="mono text-sm font-medium"
                              style={{ color: 'var(--color-text-primary)' }}>
                          {result.score.toFixed(4)}
                        </span>
                        <div className="w-20 h-1.5 rounded-full overflow-hidden"
                             style={{ background: 'var(--color-border)' }}>
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${Math.min(result.score * 100, 100)}%`,
                              background: 'linear-gradient(90deg, var(--color-brand), var(--color-brand-light))',
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={result.type === 'present' ? 'tag-success' : 'tag-brand'}
                            style={result.type !== 'present' ? {
                              background: 'var(--color-surface-overlay)',
                              color: 'var(--color-text-tertiary)',
                            } : {}}>
                        {result.type === 'present' 
                          ? result.uid 
                            ? `${t('link.prediction.typePresent')}(PMDI: ${result.uid.split(':')[1]})`
                            : t('link.prediction.typePresent') 
                          : t('link.prediction.typeAbsent')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="px-6 py-4" style={{ borderTop: '1px solid var(--color-border)' }}>
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
        <div className="text-center py-12 animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
               style={{ background: 'var(--color-surface-raised)' }}>
            <svg className="w-8 h-8" style={{ color: 'var(--color-text-tertiary)' }}
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
            {t('common.noResults')}
          </p>
        </div>
      )}
    </div>
  )
}

export default LinkPrediction
