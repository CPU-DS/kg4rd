import React, { useState, useEffect } from 'react'
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

const EntityDetail: React.FC = () => {
  const { t } = useTranslation()
  const { nodeIndex } = useParams<{ nodeIndex: string }>()
  const navigate = useNavigate()
  const [entity, setEntity] = useState<Entity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copySuccess, setCopySuccess] = useState(false)

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
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex justify-center items-center transition-colors">
        <Loading size="lg" />
      </div>
    )
  }

  if (error || !entity) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center items-center transition-colors">
        <div className="text-center">
          <div className="text-6xl text-gray-400 dark:text-gray-600 mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">{t('entity.detail.loadFailed')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
          <Button onClick={() => navigate('/') }>
            {t('common.backToHome')}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 头部：返回按钮和设置 */}
        <div className="mb-6 flex items-center justify-between">
          <Button variant="primary" onClick={() => navigate('/')}>
            ← {t('common.backToHome')}
          </Button>
          <div className="flex gap-3">
            <ThemeSwitcher />
            <LanguageSwitcher />
          </div>
        </div>
        
        <div className="space-y-8">
          {/* 实体基本信息 */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {entity.node_name}
                </h2>
                <div className="flex items-center space-x-4">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300">
                    {getNodeTypeLabel(entity.node_type)}
                  </span>
                  <button
                    onClick={handleCopyIndex}
                    className="inline-flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer group"
                    title={t('entity.detail.copyIndex')}
                  >
                    <span>{t('common.index')}: {entity.node_index}</span>
                    <svg
                      className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      {copySuccess ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      )}
                    </svg>
                  </button>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    ID: {removePrefix(entity.node_id)}
                  </span>
                </div>
              </div>
            </div>

            {/* 基本属性 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">{t('entity.detail.basicInfo')}</h3>
                <dl className="space-y-2">
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500 dark:text-gray-400">{t('common.name')}:</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-200">{entity.node_name}</dd>
                  </div>
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500 dark:text-gray-400">{t('common.type')}:</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-200">{getNodeTypeLabel(entity.node_type)}</dd>
                  </div>
                  <div className="flex">
                    <dt className="w-24 text-sm font-medium text-gray-500 dark:text-gray-400">{t('common.source')}:</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-200">{entity.node_source}</dd>
                  </div>
                  <div className="flex flex-col">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{t('common.sourceLink')}:</dt>
                    <dd className="text-sm ml-5">
                      {entity.node_source_url.map((url, index) => (
                        <a
                          key={index}
                          href={url.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline block mt-1"
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
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">{t('entity.detail.extendedInfo')}</h3>
                  <dl className="space-y-2">
                    {Object.entries(entity.node_properties).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{key}:</dt>
                        <dd className="text-sm text-gray-900 dark:text-gray-200 mt-1 break-words">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </div>
          </div>

          {/* 知识图谱 */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">{t('entity.detail.knowledgeGraph')}</h2>
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