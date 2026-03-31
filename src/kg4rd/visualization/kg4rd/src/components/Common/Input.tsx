import React from 'react'

interface InputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
  onKeyPress?: (e: React.KeyboardEvent<HTMLInputElement>) => void
}

const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  className = '',
  onKeyPress
}) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      onKeyPress={onKeyPress}
      className={`
        w-full px-4 py-2.5 rounded-xl text-sm
        transition-all duration-200
        focus:outline-none focus:ring-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        color: 'var(--color-text-primary)',
        fontFamily: 'var(--font-sans)',
        // @ts-expect-error CSS custom property
        '--tw-ring-color': 'var(--color-brand)',
      }}
    />
  )
}

export default Input
