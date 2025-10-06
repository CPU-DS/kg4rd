import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Tabs } from '../components/Common'
import { EntitySearch } from '../components/Entity'
import { LinkPrediction } from '../components/Link'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { ThemeSwitcher } from '../components/ThemeSwitcher'

const Index: React.FC = () => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('entity')

  const tabItems = [
    { key: 'entity', label: t('nav.entitySearch') },
    { key: 'link', label: t('nav.linkPrediction') }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* 头部语言和主题切换 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="flex justify-end gap-3">
          <ThemeSwitcher />
          <LanguageSwitcher />
        </div>
      </div>

      {/* 内容区域 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab 导航 */}
        <div className="flex justify-center mb-8">
          <Tabs
            items={tabItems}
            activeKey={activeTab}
            onChange={setActiveTab}
          />
        </div>

        {/* 功能内容 */}
        {activeTab === 'entity' && <EntitySearch />}
        {activeTab === 'link' && <LinkPrediction />}
      </div>
    </div>
  )
}

export default Index