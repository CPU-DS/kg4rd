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
}

const InputWithToken: React.FC<InputWithTokenProps> = ({
  selectedTokens,
  onChange,
  options,
  placeholder = '选择关系类型...',
  disabled = false,
  className = '',
  maxTokens
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchValue, setSearchValue] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // 过滤掉已选择的选项和根据搜索值过滤
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
    setSearchValue(value)
    setIsOpen(true)
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
    if (e.key === 'Backspace' && searchValue === '' && selectedTokens.length > 0) {
      // 删除最后一个token
      handleTokenRemove(selectedTokens[selectedTokens.length - 1])
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setSearchValue('')
    }
  }

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div
        className={`
          min-h-[42px] px-3 py-2 border border-gray-300 rounded-xl bg-white
          focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent
          transition-all duration-200 cursor-text
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}
          ${isOpen ? 'ring-2 ring-blue-500 border-transparent' : ''}
        `}
        onClick={() => inputRef.current?.focus()}
      >
        <div className="flex flex-wrap items-center gap-1">
          {/* 已选择的标签 */}
          {selectedTokens.map((token) => (
            <span
              key={token}
              className="inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-medium bg-blue-100 text-blue-800"
            >
              {getTokenLabel(token)}
              {!disabled && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleTokenRemove(token)
                  }}
                  className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200 focus:outline-none"
                >
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </span>
          ))}
          
          {/* 输入框 */}
          <input
            ref={inputRef}
            type="text"
            value={searchValue}
            onChange={(e) => handleInputChange(e.target.value)}
            onFocus={handleInputFocus}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={selectedTokens.length === 0 ? placeholder : ''}
            className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm placeholder-gray-400"
          />
        </div>
      </div>

      {/* 下拉选项 */}
      {isOpen && !disabled && filteredOptions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-xl shadow-lg max-h-60 overflow-auto select-dropdown">
          {filteredOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleTokenAdd(option.value)}
              className="w-full px-3 py-2 text-left hover:bg-blue-50 focus:bg-blue-50 focus:outline-none transition-colors duration-150 text-gray-900 first:rounded-t-xl last:rounded-b-xl"
            >
              <div className="flex items-center justify-between">
                <span className="block truncate">{option.label}</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 空状态提示 */}
      {isOpen && !disabled && filteredOptions.length === 0 && searchValue && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-xl shadow-lg p-3 text-sm text-gray-500 text-center">
          未找到匹配的选项
        </div>
      )}

      {/* 最大数量提示 */}
      {maxTokens && selectedTokens.length >= maxTokens && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-xl shadow-lg p-3 text-sm text-amber-600 text-center">
          最多只能选择 {maxTokens} 个选项
        </div>
      )}
    </div>
  )
}

export default InputWithToken