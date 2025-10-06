import React, { useState, useRef, useEffect } from 'react'

interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  value: string
  onChange: (value: string) => void
  options: SelectOption[]
  placeholder?: string
  disabled?: boolean
  className?: string
}

const Select: React.FC<SelectProps> = ({
  value,
  onChange,
  options,
  placeholder,
  disabled = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const selectRef = useRef<HTMLDivElement>(null)

  const selectedOption = options.find(option => option.value === value)
  const displayText = selectedOption?.label || placeholder || '请选择'

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
    }
  }

  const handleSelect = (option: SelectOption) => {
    onChange(option.value)
    setIsOpen(false)
  }

  return (
    <div ref={selectRef} className={`relative ${className}`}>
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={`
          w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl text-left
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          transition-all duration-200 bg-white dark:bg-gray-700
          ${disabled 
            ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed text-gray-400 dark:text-gray-500' 
            : 'hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer'
          }
          ${isOpen ? 'border-blue-500 ring-2 ring-blue-500' : ''}
        `}
      >
        <div className="flex items-center justify-between">
          <span className={`block truncate ${!selectedOption && placeholder ? 'text-gray-400 dark:text-gray-500' : 'text-gray-900 dark:text-gray-100'}`}>
            {displayText}
          </span>
          <svg
            className={`w-5 h-5 text-gray-400 dark:text-gray-500 transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg max-h-60 overflow-auto select-dropdown">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleSelect(option)}
              className={`
                w-full px-3 py-2 text-left hover:bg-blue-50 dark:hover:bg-blue-900/30 focus:bg-blue-50 dark:focus:bg-blue-900/30
                focus:outline-none transition-colors duration-150
                ${value === option.value 
                  ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium' 
                  : 'text-gray-900 dark:text-gray-100'
                }
                first:rounded-t-xl last:rounded-b-xl
              `}
            >
              <div className="flex items-center justify-between">
                <span className="block truncate">{option.label}</span>
                {value === option.value && (
                  <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default Select