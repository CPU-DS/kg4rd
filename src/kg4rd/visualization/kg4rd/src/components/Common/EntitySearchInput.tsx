import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { entityService } from '../../services'
import type { EntityDTO, EntityQuery } from '../../types'
import { ResultCode } from '../../types'

interface SelectedEntity {
  index: number
  name: string
  type: string
}

interface EntitySearchInputProps {
  selectedEntities: SelectedEntity[]
  onChange: (entities: SelectedEntity[]) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

const EntitySearchInput: React.FC<EntitySearchInputProps> = ({
  selectedEntities,
  onChange,
  placeholder,
  disabled = false,
  className = '',
}) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [searchValue, setSearchValue] = useState('')
  const [searchResults, setSearchResults] = useState<EntityDTO[]>([])
  const [searching, setSearching] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchValue('')
        setSearchResults([])
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const doSearch = useCallback(async (query: string) => {
    if (query.trim().length === 0) {
      setSearchResults([])
      setSearching(false)
      return
    }

    setSearching(true)
    try {
      const isNumeric = /^\d+$/.test(query.trim())
      const queryParams: EntityQuery = {
        query_type: isNumeric ? 'node_index' : 'node_name',
        query_value: query.trim(),
        match_mode: isNumeric ? 'strict' : 'contains',
        limit: 20,
      }
      const response = await entityService.query(queryParams)
      if (response.code === ResultCode.QUERY_OK) {
        setSearchResults(response.data || [])
      } else {
        setSearchResults([])
      }
    } catch {
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }, [])

  const handleInputChange = (value: string) => {
    setSearchValue(value)
    setIsOpen(true)

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (value.trim().length === 0) {
      setSearchResults([])
      setSearching(false)
      return
    }

    setSearching(true)
    debounceRef.current = setTimeout(() => {
      doSearch(value)
    }, 300)
  }

  const handleEntitySelect = (entity: EntityDTO) => {
    if (selectedEntities.some(e => e.index === entity.node_index)) {
      return
    }
    onChange([...selectedEntities, {
      index: entity.node_index,
      name: entity.node_name,
      type: entity.node_type,
    }])
    setSearchValue('')
    setSearchResults([])
    inputRef.current?.focus()
  }

  const handleEntityRemove = (index: number) => {
    onChange(selectedEntities.filter(e => e.index !== index))
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && searchValue === '' && selectedEntities.length > 0) {
      handleEntityRemove(selectedEntities[selectedEntities.length - 1].index)
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setSearchValue('')
      setSearchResults([])
    } else if (e.key === 'Enter' && searchValue.trim()) {
      e.preventDefault()
      if (/^\d+$/.test(searchValue.trim())) {
        const idx = parseInt(searchValue.trim())
        if (!selectedEntities.some(e => e.index === idx)) {
          const matchedResult = searchResults.find(r => r.node_index === idx)
          onChange([...selectedEntities, {
            index: idx,
            name: matchedResult?.node_name || `#${idx}`,
            type: matchedResult?.node_type || '',
          }])
          setSearchValue('')
          setSearchResults([])
        }
      } else if (searchResults.length > 0) {
        handleEntitySelect(searchResults[0])
      }
    }
  }

  const selectedIndexSet = new Set(selectedEntities.map(e => e.index))
  const availableResults = searchResults.filter(r => !selectedIndexSet.has(r.node_index))

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div
        className="min-h-[42px] px-3 py-2 rounded-xl cursor-pointer transition-all duration-200"
        style={{
          background: disabled ? 'var(--color-surface-overlay)' : 'var(--color-surface)',
          border: isOpen ? '1px solid var(--color-brand)' : '1px solid var(--color-border)',
          boxShadow: isOpen ? '0 0 0 2px rgba(13, 148, 136, 0.2)' : 'none',
          opacity: disabled ? 0.5 : 1,
        }}
        onClick={() => inputRef.current?.focus()}
      >
        <div className="flex flex-wrap items-center gap-1.5">
          {selectedEntities.map((entity) => (
            <span
              key={entity.index}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium"
              style={{
                background: 'var(--color-brand-subtle)',
                color: 'var(--color-brand)',
              }}
            >
              <span className="max-w-[140px] truncate">{entity.name}</span>
              <span className="mono opacity-60">#{entity.index}</span>
              {!disabled && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleEntityRemove(entity.index)
                  }}
                  className="ml-0.5 inline-flex items-center justify-center w-4 h-4 rounded-full transition-colors cursor-pointer"
                  style={{ opacity: 0.7 }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '1' }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '0.7' }}
                >
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </span>
          ))}

          <div className="flex-1 min-w-[140px] flex items-center gap-1">
            <svg className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={searchValue}
              onChange={(e) => handleInputChange(e.target.value)}
              onFocus={() => { if (!disabled) setIsOpen(true) }}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={selectedEntities.length === 0
                ? (placeholder || t('link.prediction.entitySearchPlaceholder'))
                : t('link.prediction.entitySearchContinue')}
              className="flex-1 bg-transparent border-none outline-none text-sm cursor-pointer"
              style={{
                color: 'var(--color-text-primary)',
                fontFamily: 'var(--font-sans)',
              }}
            />
          </div>
        </div>
      </div>

      {isOpen && !disabled && searchValue.trim().length > 0 && (
        <div className="absolute z-50 w-full mt-1.5 rounded-xl overflow-hidden max-h-72 overflow-y-auto select-dropdown"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
             }}>
          {searching ? (
            <div className="px-4 py-6 flex flex-col items-center gap-2">
              <div className="w-5 h-5 border-2 rounded-full animate-spin"
                   style={{ borderColor: 'var(--color-border)', borderTopColor: 'var(--color-brand)' }} />
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                {t('common.loading')}
              </span>
            </div>
          ) : availableResults.length > 0 ? (
            availableResults.map((entity) => (
              <button
                key={entity.node_index}
                type="button"
                onClick={() => handleEntitySelect(entity)}
                className="w-full px-4 py-3 text-left transition-colors duration-150 cursor-pointer"
                style={{ color: 'var(--color-text-primary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--color-surface-raised)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium truncate">{entity.node_name}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="tag-brand" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                        {t(`nodeTypes.${entity.node_type}` as any) || entity.node_type}
                      </span>
                      <span className="mono text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        #{entity.node_index}
                      </span>
                    </div>
                  </div>
                  <svg className="w-3.5 h-3.5 flex-shrink-0 ml-2" style={{ color: 'var(--color-text-tertiary)' }}
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
              </button>
            ))
          ) : (
            <div className="px-4 py-6 text-center">
              <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                {t('link.prediction.entitySearchNoResults')}
              </p>
              {/^\d+$/.test(searchValue.trim()) && (
                <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)', opacity: 0.7 }}>
                  {t('link.prediction.entitySearchEnterToAdd')}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default EntitySearchInput
