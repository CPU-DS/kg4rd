import React, { useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Tabs, Button } from '../components/Common'
import { EntitySearch } from '../components/Entity'
import { LinkPrediction } from '../components/Link'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { ThemeSwitcher } from '../components/ThemeSwitcher'
import { exportPageAsSvg, exportPageAsPng } from '../utils/exportUtils'
import { useExportVisible } from '../hooks'

const Index: React.FC = () => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('entity')
  const [exporting, setExporting] = useState(false)
  const pageRef = useRef<HTMLDivElement>(null)
  const { exportVisible } = useExportVisible()

  const handleExport = async (type: 'svg' | 'png') => {
    if (!pageRef.current || exporting) return
    setExporting(true)
    try {
      const filename = `kg4rd_${activeTab}_${new Date().toISOString().slice(0, 10)}`
      if (type === 'svg') {
        await exportPageAsSvg(pageRef.current, `${filename}.svg`)
      } else {
        await exportPageAsPng(pageRef.current, `${filename}_hd.png`)
      }
    } finally {
      setExporting(false)
    }
  }

  const tabItems = [
    { key: 'entity', label: t('nav.entitySearch'), icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    )},
    { key: 'link', label: t('nav.linkPrediction'), icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
    )}
  ]

  return (
    <div ref={pageRef} className="min-h-screen transition-colors gradient-mesh"
         style={{ backgroundColor: 'var(--color-surface)' }}>
      {/* Header */}
      <header className="border-b" style={{ borderColor: 'var(--color-border)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div />
            <div className="flex items-center gap-2" data-export-ignore>
              {exportVisible && (
                <>
                  <Button variant="outline" size="sm" onClick={() => handleExport('svg')}
                          disabled={exporting} loading={exporting}>
                    {exporting ? t('export.exporting') : t('export.pageAsSvg')}
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleExport('png')}
                          disabled={exporting} loading={exporting}>
                    {exporting ? t('export.exporting') : t('export.pageAsPng')}
                  </Button>
                </>
              )}
              <ThemeSwitcher />
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center mb-8">
          <Tabs
            items={tabItems}
            activeKey={activeTab}
            onChange={setActiveTab}
          />
        </div>

        <div className="animate-fade-in">
          {activeTab === 'entity' && <EntitySearch />}
          {activeTab === 'link' && <LinkPrediction />}
        </div>
      </main>
    </div>
  )
}

export default Index
