import React, { useState, useRef, useEffect } from 'react'

interface TokenOption {
  value: string
  label: string
}

interface InputWithTokenProps {
  selectedTokens: string[]
  onChange: (tokens: string[]) => void
  options: TokenOption[]
  placeholder?: string
  disabled?: boolean
  className?: string
  maxTokens?: number
  allowCustomInput?: boolean
}

const InputWithToken: React.FC<InputWithTokenProps> = ({
  selectedTokens,
  onChange,
  options,
  placeholder = '选择关系类型...',
  disabled = false,
  className = '',
  maxTokens,
  allowCustomInput = false
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchValue, setSearchValue] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const filteredOptions = options.filter(option => 
    !selectedTokens.includes(option.value) &&
    option.label.toLowerCase().includes(searchValue.toLowerCase())
  )

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchValue('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleInputFocus = () => {
    if (!disabled) {
      setIsOpen(true)
    }
  }

  const handleInputChange = (value: string) => {
    if (allowCustomInput) {
      const numericValue = value.replace(/\D/g, '')
      setSearchValue(numericValue)
    } else {
      setSearchValue(value)
      setIsOpen(true)
    }
  }

  const handleTokenAdd = (value: string) => {
    if (maxTokens && selectedTokens.length >= maxTokens) {
      return
    }
    onChange([...selectedTokens, value])
    setSearchValue('')
    inputRef.current?.focus()
  }

  const handleTokenRemove = (tokenToRemove: string) => {
    onChange(selectedTokens.filter(token => token !== tokenToRemove))
    inputRef.current?.focus()
  }

  const getTokenLabel = (value: string) => {
    const option = options.find(opt => opt.value === value)
    return option?.label || value
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchValue.trim() !== '') {
      e.preventDefault()
      if (allowCustomInput) {
        const trimmedValue = searchValue.trim()
        if (!/^\d+$/.test(trimmedValue)) {
          return
        }
        if (!selectedTokens.includes(trimmedValue)) {
          if (maxTokens && selectedTokens.length >= maxTokens) {
            return
          }
          handleTokenAdd(trimmedValue)
        }
      } else if (filteredOptions.length > 0) {
        handleTokenAdd(filteredOptions[0].value)
      }
    } else if (e.key === 'Backspace' && searchValue === '' && selectedTokens.length > 0) {
      handleTokenRemove(selectedTokens[selectedTokens.length - 1])
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setSearchValue('')
    }
  }

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div
        className="min-h-[42px] px-3 py-2 rounded-xl cursor-pointer transition-all duration-200"
        style={{
          background: disabled ? 'var(--color-surface-overlay)' : 'var(--color-surface)',
          border: isOpen
            ? '1px solid var(--color-brand)'
            : '1px solid var(--color-border)',
          boxShadow: isOpen ? '0 0 0 2px rgba(13, 148, 136, 0.2)' : 'none',
          opacity: disabled ? 0.5 : 1,
        }}
        onClick={() => inputRef.current?.focus()}
      >
        <div className="flex items-center gap-2">
          <div className="flex flex-wrap items-center gap-1.5 flex-1">
            {selectedTokens.map((token) => (
              <span
                key={token}
                className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                style={{
                  background: 'var(--color-brand-subtle)',
                  color: 'var(--color-brand)',
                }}
              >
                {getTokenLabel(token)}
                {!disabled && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleTokenRemove(token)
                    }}
                    className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full transition-colors cursor-pointer"
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
            
            <input
              ref={inputRef}
              type="text"
              value={searchValue}
              onChange={(e) => handleInputChange(e.target.value)}
              onFocus={handleInputFocus}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={selectedTokens.length === 0 ? placeholder : ''}
              className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm cursor-pointer"
              style={{
                color: 'var(--color-text-primary)',
                fontFamily: 'var(--font-sans)',
              }}
            />
          </div>
          
          {!allowCustomInput && (
            <svg
              className="w-4 h-4 transition-transform duration-200 flex-shrink-0"
              style={{
                color: 'var(--color-text-tertiary)',
                transform: isOpen ? 'rotate(180deg)' : 'none',
              }}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
      </div>

      {isOpen && !disabled && !allowCustomInput && filteredOptions.length > 0 && (
        <div className="absolute z-50 w-full mt-1.5 rounded-xl overflow-hidden max-h-60 overflow-y-auto select-dropdown"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
             }}>
          {filteredOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleTokenAdd(option.value)}
              className="w-full px-4 py-2.5 text-left text-sm transition-colors duration-150 cursor-pointer"
              style={{
                color: 'var(--color-text-primary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--color-surface-raised)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <div className="flex items-center justify-between">
                <span className="block truncate">{option.label}</span>
                <svg className="w-3.5 h-3.5 flex-shrink-0" style={{ color: 'var(--color-text-tertiary)' }}
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      )}

      {isOpen && !disabled && !allowCustomInput && filteredOptions.length === 0 && searchValue && (
        <div className="absolute z-50 w-full mt-1.5 rounded-xl p-3 text-sm text-center"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
               color: 'var(--color-text-tertiary)',
             }}>
          未找到匹配的选项
        </div>
      )}

      {maxTokens && selectedTokens.length >= maxTokens && (
        <div className="absolute z-50 w-full mt-1.5 rounded-xl p-3 text-sm text-center"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
               color: 'var(--color-warning)',
             }}>
          最多只能选择 {maxTokens} 个选项
        </div>
      )}
    </div>
  )
}

export default InputWithToken
