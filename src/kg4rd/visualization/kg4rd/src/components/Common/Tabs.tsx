import React from 'react'

interface TabItem {
  key: string
  label: string
}

interface TabsProps {
  items: TabItem[]
  activeKey: string
  onChange: (key: string) => void
  className?: string
}

const Tabs: React.FC<TabsProps> = ({ items, activeKey, onChange, className = '' }) => {
  return (
    <div className={`inline-flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 transition-colors ${className}`}>
      {items.map((item) => (
        <button
          key={item.key}
          onClick={() => onChange(item.key)}
          className={`
            px-6 py-2 font-medium text-sm rounded-lg transition-all duration-200
            ${
              activeKey === item.key
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
            }
          `}
        >
          {item.label}
        </button>
      ))}
    </div>
  )
}

export default Tabs