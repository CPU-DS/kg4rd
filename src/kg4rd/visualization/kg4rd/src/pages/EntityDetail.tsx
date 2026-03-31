import React, { useRef, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button, Loading } from '../components/Common'
import { Graph } from '../components/Graph'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { ThemeSwitcher } from '../components/ThemeSwitcher'
import { entityService } from '../services'
import type { Entity, NodeType } from '../types'
import { ResultCode } from '../types'
import { getNodeLabel } from '../utils/i18nTypeMap'
import { exportPageAsSvg, exportPageAsPng } from '../utils/exportUtils'
import { useExportVisible } from '../hooks'

const EntityDetail: React.FC = () => {
  const { t } = useTranslation()
  const { nodeIndex } = useParams<{ nodeIndex: string }>()
  const navigate = useNavigate()
  const [entity, setEntity] = useState<Entity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copySuccess, setCopySuccess] = useState(false)
  const [exporting, setExporting] = useState(false)
  const pageRef = useRef<HTMLDivElement>(null)
  const { exportVisible } = useExportVisible()

  const getNodeTypeLabel = (type: NodeType) => {
    return getNodeLabel(type, t)
  }

  const removePrefix = (id_: string) => {
    if (id_.startsWith('kg4rd:')) {
      return id_.slice(6)
    }
    return id_
  }

  const handleCopyIndex = async () => {
    if (!entity) return
    
    try {
      await navigator.clipboard.writeText(entity.node_index.toString())
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleExport = async (type: 'svg' | 'png') => {
    if (!pageRef.current || exporting) return
    setExporting(true)
    try {
      const filename = `${entity?.node_name || 'entity'}_${new Date().toISOString().slice(0, 10)}`
      if (type === 'svg') {
        await exportPageAsSvg(pageRef.current, `${filename}.svg`)
      } else {
        await exportPageAsPng(pageRef.current, `${filename}_hd.png`)
      }
    } finally {
      setExporting(false)
    }
  }

  useEffect(() => {
    const loadEntity = async () => {
      if (!nodeIndex) {
        setError(t('entity.detail.errorInvalidIndex'))
        setLoading(false)
        return
      }

      const index = parseInt(nodeIndex)
      if (isNaN(index)) {
        setError(t('entity.detail.errorInvalidIndex'))
        setLoading(false)
        return
      }

      try {
        const response = await entityService.getByIndex(index)
        
        if (response.code === ResultCode.QUERY_OK) {
          setEntity(response.data)
        } else {
          setError(response.message || t('entity.detail.errorLoadFailed'))
        }
      } catch (err) {
        setError(t('entity.detail.errorLoadError'))
      } finally {
        setLoading(false)
      }
    }

    loadEntity()
  }, [nodeIndex, t])

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center transition-colors"
           style={{ backgroundColor: 'var(--color-surface)' }}>
        <Loading size="lg" />
      </div>
    )
  }

  if (error || !entity) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center transition-colors gradient-mesh"
           style={{ backgroundColor: 'var(--color-surface)' }}>
        <div className="text-center animate-fade-in">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center"
               style={{ background: 'var(--color-error-subtle)' }}>
            <svg className="w-10 h-10" style={{ color: 'var(--color-error)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold mb-2"
              style={{ color: 'var(--color-text-primary)' }}>
            {t('entity.detail.loadFailed')}
          </h1>
          <p className="mb-8 text-sm" style={{ color: 'var(--color-text-secondary)' }}>{error}</p>
          <Button onClick={() => navigate('/')}>
            {t('common.backToHome')}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div ref={pageRef} className="min-h-screen transition-colors gradient-mesh"
         style={{ backgroundColor: 'var(--color-surface)' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: 'var(--color-border)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <button onClick={() => navigate('/')}
                      data-export-ignore
                      className="flex items-center gap-2 text-sm font-medium transition-colors cursor-pointer"
                      style={{ color: 'var(--color-brand)' }}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                {t('common.backToHome')}
              </button>
              <span style={{ color: 'var(--color-border)' }}>/</span>
              <span className="text-sm font-medium"
                    style={{ color: 'var(--color-text-primary)' }}>
                {entity.node_name}
              </span>
            </div>
            <div className="flex items-center gap-2" data-export-ignore>
              {exportVisible && (
                <>
                  <Button variant="outline" size="sm" onClick={() => handleExport('svg')}
                          disabled={exporting} loading={exporting}>
                    {exporting ? t('export.exporting') : t('export.pageAsSvg')}
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleExport('png')}
                          disabled={exporting} loading={exporting}>
                    {exporting ? t('export.exporting') : t('export.pageAsPng')}
                  </Button>
                </>
              )}
              <ThemeSwitcher />
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8 animate-fade-in">
          {/* Entity info card */}
          <div className="card p-8">
            <div className="flex items-start justify-between mb-8">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <h2 className="text-2xl font-semibold tracking-tight"
                      style={{ color: 'var(--color-text-primary)' }}>
                    {entity.node_name}
                  </h2>
                  <span className="tag-brand">
                    {getNodeTypeLabel(entity.node_type)}
                  </span>
                </div>
                <div className="flex items-center gap-4">
                  <button
                    onClick={handleCopyIndex}
                    className="inline-flex items-center gap-1.5 text-sm transition-all cursor-pointer group"
                    style={{ color: 'var(--color-text-tertiary)' }}
                    title={t('entity.detail.copyIndex')}
                  >
                    <span className="mono text-xs" style={{
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: 'var(--color-surface-raised)',
                      border: '1px solid var(--color-border)',
                    }}>
                      {t('common.index')}: {entity.node_index}
                    </span>
                    <svg
                      className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      style={{ color: copySuccess ? 'var(--color-success)' : 'var(--color-brand)' }}
                    >
                      {copySuccess ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      )}
                    </svg>
                  </button>
                  <span className="mono text-xs" style={{
                    color: 'var(--color-text-tertiary)',
                    padding: '2px 8px',
                    borderRadius: '6px',
                    background: 'var(--color-surface-raised)',
                    border: '1px solid var(--color-border)',
                  }}>
                    ID: {removePrefix(entity.node_id)}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-wider mb-4"
                    style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.08em' }}>
                  {t('entity.detail.basicInfo')}
                </h3>
                <div className="card-inner p-4 space-y-3">
                  <div className="flex items-start">
                    <dt className="w-28 text-sm flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                      {t('common.name')}
                    </dt>
                    <dd className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                      {entity.node_name}
                    </dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-28 text-sm flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                      {t('common.type')}
                    </dt>
                    <dd className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                      {getNodeTypeLabel(entity.node_type)}
                    </dd>
                  </div>
                  <div className="flex items-start">
                    <dt className="w-28 text-sm flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                      {t('common.source')}
                    </dt>
                    <dd className="text-sm" style={{ color: 'var(--color-text-primary)' }}>
                      {entity.node_source}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm mb-2" style={{ color: 'var(--color-text-tertiary)' }}>
                      {t('common.sourceLink')}
                    </dt>
                    <dd className="flex flex-col gap-1.5 ml-2">
                      {entity.node_source_url.map((url, index) => (
                        <a
                          key={index}
                          href={url.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm inline-flex items-center gap-1 transition-colors"
                          style={{ color: 'var(--color-brand)' }}
                        >
                          <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          {url.name}
                        </a>
                      ))}
                    </dd>
                  </div>
                </div>
              </div>

              {Object.keys(entity.node_properties).length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wider mb-4"
                      style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.08em' }}>
                    {t('entity.detail.extendedInfo')}
                  </h3>
                  <div className="card-inner p-4 space-y-3">
                    {Object.entries(entity.node_properties).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-xs font-medium uppercase tracking-wider mb-1"
                            style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.05em' }}>
                          {key}
                        </dt>
                        <dd className="text-sm break-words" style={{ color: 'var(--color-text-primary)' }}>
                          {value}
                        </dd>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Knowledge graph */}
          <div>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-1 h-6 rounded-full" style={{ background: 'var(--color-brand)' }} />
              <h2 className="text-xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                {t('entity.detail.knowledgeGraph')}
              </h2>
            </div>
            <Graph
              centerNodeIndex={entity.node_index}
              centerNodeType={entity.node_type}
              centerNodeName={entity.node_name}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

export default EntityDetail
