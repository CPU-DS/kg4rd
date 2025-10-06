export type Language = 'zh' | 'en'

export const LANGUAGES: Record<Language, { label: string; nativeLabel: string }> = {
  zh: { label: 'Chinese', nativeLabel: '简体中文' },
  en: { label: 'English', nativeLabel: 'English' },
}

export const DEFAULT_LANGUAGE: Language = 'zh'