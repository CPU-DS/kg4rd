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

  const themes: { value: ThemeMode; label: string; icon: string }[] = [
    { value: 'light', label: t('theme.light'), icon: '' },
    { value: 'dark', label: t('theme.dark'), icon: '' },
    { value: 'system', label: t('theme.system'), icon: '' },
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
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
        type="button"
        aria-label={t('theme.switchTheme')}
      >
        <span className="text-lg">{currentTheme.icon}</span>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
          {currentTheme.label}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50 animate-fade-in-down">
          {themes.map((themeOption) => (
            <button
              key={themeOption.value}
              onClick={() => handleThemeChange(themeOption.value)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-3 ${
                theme === themeOption.value
                  ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium'
                  : 'text-gray-700 dark:text-gray-200'
              }`}
              type="button"
            >
              <span className="text-lg">{themeOption.icon}</span>
              <span>{themeOption.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}