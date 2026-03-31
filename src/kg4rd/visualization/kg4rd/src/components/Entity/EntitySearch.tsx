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

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setError(t('entity.search.errorEmpty'))
      setResults([])
      return
    }

    setLoading(true)
    setError(null)
    resetPagination()

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
    if (!name.includes(' ')) {
      return name.toUpperCase()
    } else {
      return name.replace(/\b\w/g, (char) => char.toUpperCase())
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Search configuration */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('entity.search.queryMethod')}
            </label>
            <Select
              value={queryType}
              onChange={(value) => setQueryType(value as 'node_index' | 'node_name')}
              options={queryTypeOptions}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
              {t('entity.search.nodeType')}
            </label>
            <Select
              value={nodeType}
              onChange={(value) => setNodeType(value as MatchNodeType)}
              options={nodeTypeOptions}
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider mb-2"
                   style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}>
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
          <div className="mt-4 p-3 rounded-xl text-sm"
               style={{
                 background: 'var(--color-error-subtle)',
                 color: 'var(--color-error)',
                 border: '1px solid transparent',
               }}>
            {error}
          </div>
        )}
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
                {t('entity.search.searchResults')}
                <span className="ml-2 text-sm font-normal" style={{ color: 'var(--color-text-tertiary)' }}>
                  {t('common.totalResults', { count: results.length })}
                </span>
              </h3>
              <div className="text-xs mono" style={{ color: 'var(--color-text-tertiary)' }}>
                {t('common.page', { current: currentPage, total: totalPages })}
              </div>
            </div>
          </div>

          <div>
            {paginatedResults.map((entity, index) => (
              <div
                key={entity.node_index}
                onClick={() => handleEntityClick(entity)}
                className="px-6 py-4 cursor-pointer transition-all duration-200 animate-stagger group"
                style={{
                  borderBottom: '1px solid var(--color-border-subtle)',
                  animationDelay: `${index * 0.04}s`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--color-surface-raised)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold mb-1"
                        style={{ color: 'var(--color-text-primary)' }}>
                      {optimizeNodeName(entity.node_name)}
                    </h4>
                    <div className="flex items-center gap-3">
                      <span className="mono text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        {t('common.index')}: {entity.node_index}
                      </span>
                      <span className="tag-brand">
                        {getNodeTypeLabel(entity.node_type)}
                      </span>
                    </div>
                  </div>
                  <svg className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1"
                       style={{ color: 'var(--color-text-tertiary)' }}
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))}
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

      {!loading && results.length === 0 && query && (
        <div className="text-center py-12 animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
               style={{ background: 'var(--color-surface-raised)' }}>
            <svg className="w-8 h-8" style={{ color: 'var(--color-text-tertiary)' }}
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
            {t('entity.search.noResults')}
          </p>
        </div>
      )}
    </div>
  )
}

export default EntitySearch
