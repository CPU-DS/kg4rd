import 'i18next'
import zh from '../i18n/locales/zh'

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation'
    resources: {
      translation: typeof zh
    }
  }
}