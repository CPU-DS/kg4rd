import React from 'react'

interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  className?: string
  type?: 'button' | 'submit' | 'reset'
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  type = 'button'
}) => {
  const sizeClasses = {
    sm: 'px-3.5 py-1.5 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'px-7 py-3 text-base'
  }

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          background: 'linear-gradient(135deg, var(--color-brand), var(--color-brand-dark))',
          color: '#ffffff',
          border: 'none',
          boxShadow: disabled ? 'none' : '0 2px 8px rgba(13, 148, 136, 0.3)',
        }
      case 'secondary':
        return {
          background: 'var(--color-surface-raised)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }
      case 'outline':
        return {
          background: 'transparent',
          color: 'var(--color-brand)',
          border: '1px solid var(--color-brand)',
        }
    }
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center font-medium rounded-xl
        transition-all duration-200 cursor-pointer
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${sizeClasses[size]}
        ${(disabled || loading) ? 'opacity-50 cursor-not-allowed' : 'hover:brightness-110 active:scale-[0.98]'}
        ${className}
      `}
      style={{
        ...getVariantStyles(),
        fontFamily: 'var(--font-sans)',
      }}
    >
      {loading && (
        <div className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}

export default Button
