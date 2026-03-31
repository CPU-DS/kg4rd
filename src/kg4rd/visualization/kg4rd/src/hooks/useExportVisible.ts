import { useCallback, useEffect, useState } from 'react'

export const useExportVisible = () => {
  const [visible, setVisible] = useState(false)

  const toggle = useCallback(() => setVisible((v) => !v), [])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'e') {
        e.preventDefault()
        toggle()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [toggle])

  return { exportVisible: visible, toggleExportVisible: toggle }
}
