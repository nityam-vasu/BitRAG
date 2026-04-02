import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ChatPage from './pages/ChatPage'
import DocumentsPage from './pages/DocumentsPage'
import GraphPage from './pages/GraphPage'
import SettingsPage from './pages/SettingsPage'
import OllamaParamsPage from './pages/OllamaParamsPage'
import Sidebar from './components/Sidebar'

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-900 text-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/ollama-params" element={<OllamaParamsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
