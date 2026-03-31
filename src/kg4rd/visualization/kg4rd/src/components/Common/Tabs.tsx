import React from 'react'

interface TabItem {
  key: string
  label: string
  icon?: React.ReactNode
}

interface TabsProps {
  items: TabItem[]
  activeKey: string
  onChange: (key: string) => void
  className?: string
}

const Tabs: React.FC<TabsProps> = ({ items, activeKey, onChange, className = '' }) => {
  return (
    <div className={`inline-flex p-1 rounded-xl transition-colors ${className}`}
         style={{ background: 'var(--color-surface-raised)', border: '1px solid var(--color-border)' }}>
      {items.map((item) => {
        const isActive = activeKey === item.key
        return (
          <button
            key={item.key}
            onClick={() => onChange(item.key)}
            className="relative px-5 py-2.5 font-medium text-sm rounded-lg transition-all duration-250 flex items-center gap-2 cursor-pointer"
            style={{
              background: isActive ? 'var(--color-brand)' : 'transparent',
              color: isActive ? '#ffffff' : 'var(--color-text-secondary)',
              boxShadow: isActive ? 'var(--shadow-md)' : 'none',
            }}
          >
            {item.icon}
            {item.label}
          </button>
        )
      })}
    </div>
  )
}

export default Tabs
