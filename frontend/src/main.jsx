import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import IdeasView from './IdeasView.jsx'
import IdeaBreakdown from './IdeaBreakdown.jsx'
import SimilarityView from './SimilarityView.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/ideas" element={<IdeasView />} />
        <Route path="/breakdown" element={<IdeaBreakdown />} />
        <Route path="/similarity" element={<SimilarityView />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
