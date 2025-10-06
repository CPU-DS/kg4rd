import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { LANGUAGES, type Language } from '../../i18n/types'

export interface LanguageSwitcherProps {
  className?: string
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { i18n } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const currentLanguage = (i18n.language || 'zh') as Language

  const handleLanguageChange = (lang: Language): void => {
    i18n.changeLanguage(lang)
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
      >
        <svg
          className="w-5 h-5 text-gray-600 dark:text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
          />
        </svg>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {LANGUAGES[currentLanguage].nativeLabel}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 py-1 z-50 animate-fade-in-down">
          {Object.entries(LANGUAGES).map(([lang, { nativeLabel }]) => (
            <button
              key={lang}
              onClick={() => handleLanguageChange(lang as Language)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                currentLanguage === lang ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-700 dark:text-gray-300'
              }`}
              type="button"
            >
              {nativeLabel}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}