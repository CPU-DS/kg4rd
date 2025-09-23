import React, { useState } from 'react'
import { Tabs } from '../components/Common'
import { EntitySearch } from '../components/Entity'
import { LinkPrediction } from '../components/Link'

const Index: React.FC = () => {
  const [activeTab, setActiveTab] = useState('entity')

  const tabItems = [
    { key: 'entity', label: '实体查询' },
    { key: 'link', label: '链接预测' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
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