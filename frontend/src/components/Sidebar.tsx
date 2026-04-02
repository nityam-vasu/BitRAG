import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, Network, Settings } from 'lucide-react'

const navItems = [
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/documents', icon: FileText, label: 'Documents' },
  { to: '/graph', icon: Network, label: 'Graph' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-blue-400">BitRAG</h1>
        <p className="text-xs text-gray-400">Local RAG Chat</p>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map(({ to, icon: Icon, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`
                }
              >
                <Icon size={20} />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500">
          Powered by Ollama & ChromaDB
        </p>
      </div>
    </aside>
  )
}
