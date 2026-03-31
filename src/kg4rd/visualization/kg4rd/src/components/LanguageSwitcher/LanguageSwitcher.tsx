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
        className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer"
        style={{
          background: 'var(--color-surface-raised)',
          border: '1px solid var(--color-border)',
          color: 'var(--color-text-secondary)',
        }}
        type="button"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.8}
            d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
          />
        </svg>
        <span className="text-sm font-medium hidden sm:inline">
          {LANGUAGES[currentLanguage].nativeLabel}
        </span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-44 rounded-xl overflow-hidden py-1 z-50 animate-fade-in-down"
             style={{
               background: 'var(--color-surface)',
               border: '1px solid var(--color-border)',
               boxShadow: 'var(--shadow-lg)',
             }}>
          {Object.entries(LANGUAGES).map(([lang, { nativeLabel }]) => (
            <button
              key={lang}
              onClick={() => handleLanguageChange(lang as Language)}
              className="w-full text-left px-4 py-2.5 text-sm transition-colors cursor-pointer"
              style={{
                background: currentLanguage === lang ? 'var(--color-brand-subtle)' : 'transparent',
                color: currentLanguage === lang ? 'var(--color-brand)' : 'var(--color-text-secondary)',
                fontWeight: currentLanguage === lang ? 500 : 400,
              }}
              onMouseEnter={(e) => {
                if (currentLanguage !== lang)
                  e.currentTarget.style.background = 'var(--color-surface-raised)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = currentLanguage === lang
                  ? 'var(--color-brand-subtle)' : 'transparent'
              }}
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
