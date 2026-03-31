import React from 'react'
import { useTranslation } from 'react-i18next'

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (pageSize: number) => void
  pageSizeOptions?: number[]
  className?: string
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50, 100],
  className = ''
}) => {
  const { t } = useTranslation()
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  const getVisiblePages = () => {
    const delta = 2
    const range = []
    const rangeWithDots = []

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i)
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...')
    } else {
      rangeWithDots.push(1)
    }

    rangeWithDots.push(...range)

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages)
    } else {
      if (totalPages > 1) {
        rangeWithDots.push(totalPages)
      }
    }

    return rangeWithDots
  }

  const visiblePages = getVisiblePages()

  if (totalItems === 0) {
    return null
  }

  const pageButtonStyle = (isActive: boolean): React.CSSProperties => ({
    background: isActive
      ? 'linear-gradient(135deg, var(--color-brand), var(--color-brand-dark))'
      : 'var(--color-surface)',
    color: isActive ? '#ffffff' : 'var(--color-text-secondary)',
    border: isActive ? 'none' : '1px solid var(--color-border)',
    boxShadow: isActive ? '0 2px 6px rgba(13, 148, 136, 0.25)' : 'none',
  })

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div className="flex items-center gap-4">
        <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          {t('pagination.showing')}{' '}
          <span className="font-medium mono" style={{ color: 'var(--color-text-primary)' }}>{startItem}</span>
          {' '}{t('pagination.to')}{' '}
          <span className="font-medium mono" style={{ color: 'var(--color-text-primary)' }}>{endItem}</span>，
          {t('pagination.total')}{' '}
          <span className="font-medium mono" style={{ color: 'var(--color-text-primary)' }}>{totalItems}</span>
          {' '}{t('pagination.items')}
        </div>

        {onPageSizeChange && (
          <div className="flex items-center gap-2">
            <label className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              {t('pagination.perPage')}:
            </label>
            <select
              value={itemsPerPage}
              onChange={(e) => onPageSizeChange(parseInt(e.target.value))}
              className="px-2.5 py-1.5 rounded-lg text-sm focus:outline-none focus:ring-2 cursor-pointer"
              style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-primary)',
                fontFamily: 'var(--font-mono)',
                // @ts-expect-error CSS custom property
                '--tw-ring-color': 'var(--color-brand)',
              }}
            >
              {pageSizeOptions.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: 'var(--color-surface)',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border)',
            }}
          >
            {t('pagination.previous')}
          </button>

          {visiblePages.map((page, index) => (
            <React.Fragment key={index}>
              {page === '...' ? (
                <span className="px-2 py-2 text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                  ···
                </span>
              ) : (
                <button
                  onClick={() => onPageChange(page as number)}
                  className="w-9 h-9 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer mono"
                  style={pageButtonStyle(currentPage === page)}
                >
                  {page}
                </button>
              )}
            </React.Fragment>
          ))}

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: 'var(--color-surface)',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border)',
            }}
          >
            {t('pagination.next')}
          </button>
        </div>
      )}
    </div>
  )
}

export default Pagination
