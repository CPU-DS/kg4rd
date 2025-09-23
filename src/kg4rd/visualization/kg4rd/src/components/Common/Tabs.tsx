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
    <div className={`inline-flex bg-gray-100 rounded-xl p-1 ${className}`}>
      {items.map((item) => (
        <button
          key={item.key}
          onClick={() => onChange(item.key)}
          className={`
            px-6 py-2 font-medium text-sm rounded-lg transition-all duration-200
            ${
              activeKey === item.key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
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