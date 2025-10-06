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
        w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl 
        bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
        placeholder:text-gray-400 dark:placeholder:text-gray-500
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
        disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
        transition-colors duration-200
        ${className}
      `}
    />
  )
}

export default Input