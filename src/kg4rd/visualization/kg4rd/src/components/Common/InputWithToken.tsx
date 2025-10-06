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
    // 如果是自定义输入模式，只允许输入数字
    if (allowCustomInput) {
      // 只保留数字字符
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
      // 如果允许自定义输入，添加自定义值
      if (allowCustomInput) {
        const trimmedValue = searchValue.trim()
        // 验证是否为纯数字
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
        // 否则添加第一个匹配的选项
        handleTokenAdd(filteredOptions[0].value)
      }
    } else if (e.key === 'Backspace' && searchValue === '' && selectedTokens.length > 0) {
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
          min-h-[42px] px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700
          focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent
          transition-all duration-200 cursor-pointer
          ${disabled ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed' : ''}
          ${isOpen ? 'ring-2 ring-blue-500 border-transparent' : ''}
        `}
        onClick={() => inputRef.current?.focus()}
      >
        <div className="flex items-center gap-2">
          <div className="flex flex-wrap items-center gap-1 flex-1">
            {/* 已选择的标签 */}
            {selectedTokens.map((token) => (
              <span
                key={token}
                className="inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300"
              >
                {getTokenLabel(token)}
                {!disabled && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleTokenRemove(token)
                    }}
                    className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 focus:outline-none"
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
              className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 cursor-pointer"
            />
          </div>
          
          {/* 下拉箭头 - 仅在非自定义输入模式下显示 */}
          {!allowCustomInput && (
            <svg
              className={`w-5 h-5 text-gray-400 dark:text-gray-500 transition-transform duration-200 flex-shrink-0 ${
                isOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
        </div>
      </div>

      {/* 下拉选项 */}
      {isOpen && !disabled && !allowCustomInput && filteredOptions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg max-h-60 overflow-auto select-dropdown">
          {filteredOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleTokenAdd(option.value)}
              className="w-full px-3 py-2 text-left hover:bg-blue-50 dark:hover:bg-blue-900/30 focus:bg-blue-50 dark:focus:bg-blue-900/30 focus:outline-none transition-colors duration-150 text-gray-900 dark:text-gray-100 first:rounded-t-xl last:rounded-b-xl cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <span className="block truncate">{option.label}</span>
                <svg className="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 空状态提示 - 仅在非自定义输入模式下显示 */}
      {isOpen && !disabled && !allowCustomInput && filteredOptions.length === 0 && searchValue && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg p-3 text-sm text-gray-500 dark:text-gray-400 text-center">
          未找到匹配的选项
        </div>
      )}

      {/* 最大数量提示 */}
      {maxTokens && selectedTokens.length >= maxTokens && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg p-3 text-sm text-amber-600 dark:text-amber-400 text-center">
          最多只能选择 {maxTokens} 个选项
        </div>
      )}
    </div>
  )
}

export default InputWithToken