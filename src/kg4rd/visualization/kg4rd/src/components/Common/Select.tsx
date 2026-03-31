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
          w-full px-4 py-2.5 rounded-xl text-left text-sm
          transition-all duration-200 cursor-pointer
          focus:outline-none focus:ring-2
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        style={{
          background: 'var(--color-surface)',
          border: isOpen ? '1px solid var(--color-brand)' : '1px solid var(--color-border)',
          color: selectedOption ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
          boxShadow: isOpen ? '0 0 0 2px rgba(13, 148, 136, 0.2)' : 'none',
        }}
      >
        <div className="flex items-center justify-between">
          <span className="block truncate">{displayText}</span>
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
        </div>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1.5 rounded-xl overflow-hidden max-h-60 overflow-y-auto select-dropdown"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
             }}>
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleSelect(option)}
              className="w-full px-4 py-2.5 text-left text-sm transition-colors duration-150 cursor-pointer"
              style={{
                background: value === option.value ? 'var(--color-brand-subtle)' : 'transparent',
                color: value === option.value ? 'var(--color-brand)' : 'var(--color-text-primary)',
                fontWeight: value === option.value ? 500 : 400,
              }}
              onMouseEnter={(e) => {
                if (value !== option.value)
                  e.currentTarget.style.background = 'var(--color-surface-raised)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = value === option.value
                  ? 'var(--color-brand-subtle)' : 'transparent'
              }}
            >
              <div className="flex items-center justify-between">
                <span className="block truncate">{option.label}</span>
                {value === option.value && (
                  <svg className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--color-brand)' }}
                       fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd" />
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
