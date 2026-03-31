import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useTheme, type ThemeMode } from '../../contexts'

export interface ThemeSwitcherProps {
  className?: string
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ className = '' }) => {
  const { t } = useTranslation()
  const { theme, setTheme } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const themes: { value: ThemeMode; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: t('theme.light'), icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    )},
    { value: 'dark', label: t('theme.dark'), icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    )},
    { value: 'system', label: t('theme.system'), icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    )},
  ]

  const currentTheme = themes.find((t) => t.value === theme) || themes[2]

  const handleThemeChange = (newTheme: ThemeMode): void => {
    setTheme(newTheme)
    setIsOpen(false)
  }

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer"
        style={{
          background: 'var(--color-surface-raised)',
          border: '1px solid var(--color-border)',
          color: 'var(--color-text-secondary)',
        }}
        type="button"
        aria-label={t('theme.switchTheme')}
      >
        {currentTheme.icon}
        <span className="text-sm font-medium hidden sm:inline">
          {currentTheme.label}
        </span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-44 rounded-xl overflow-hidden py-1 z-50 animate-fade-in-down"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
             }}>
          {themes.map((themeOption) => (
            <button
              key={themeOption.value}
              onClick={() => handleThemeChange(themeOption.value)}
              className="w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-3 cursor-pointer"
              style={{
                background: theme === themeOption.value ? 'var(--color-brand-subtle)' : 'transparent',
                color: theme === themeOption.value ? 'var(--color-brand)' : 'var(--color-text-secondary)',
                fontWeight: theme === themeOption.value ? 500 : 400,
              }}
              onMouseEnter={(e) => {
                if (theme !== themeOption.value)
                  e.currentTarget.style.background = 'var(--color-surface-raised)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = theme === themeOption.value
                  ? 'var(--color-brand-subtle)' : 'transparent'
              }}
              type="button"
            >
              {themeOption.icon}
              <span>{themeOption.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
