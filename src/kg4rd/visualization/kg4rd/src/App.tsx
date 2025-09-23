import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Index from './pages/Index'
import EntityDetail from './pages/EntityDetail'

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/entity/:nodeIndex" element={<EntityDetail />} />
    </Routes>
  )
}

export default App
