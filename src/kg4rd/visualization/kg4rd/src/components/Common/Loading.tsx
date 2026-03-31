import React from 'react'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const Loading: React.FC<LoadingProps> = ({ size = 'md', className = '' }) => {
  const sizeMap = {
    sm: { outer: 16, inner: 12, stroke: 2 },
    md: { outer: 28, inner: 20, stroke: 2.5 },
    lg: { outer: 40, inner: 28, stroke: 3 },
  }

  const s = sizeMap[size]

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className="relative" style={{ width: s.outer, height: s.outer }}>
        <svg
          className="animate-spin"
          width={s.outer}
          height={s.outer}
          viewBox={`0 0 ${s.outer} ${s.outer}`}
          fill="none"
        >
          <circle
            cx={s.outer / 2}
            cy={s.outer / 2}
            r={s.inner / 2}
            stroke="var(--color-border)"
            strokeWidth={s.stroke}
          />
          <path
            d={`M ${s.outer / 2} ${(s.outer - s.inner) / 2}
                A ${s.inner / 2} ${s.inner / 2} 0 0 1 ${s.outer / 2 + s.inner / 2} ${s.outer / 2}`}
            stroke="var(--color-brand)"
            strokeWidth={s.stroke}
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  )
}

export default Loading
