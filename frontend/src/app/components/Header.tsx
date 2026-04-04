import { MessageSquare, FileText, Network, Settings, HelpCircle, Moon, Sun, Activity, X } from "lucide-react";
import { NavLink } from "react-router";
import { useState, useEffect } from "react";

export default function Header() {
  const [isDark, setIsDark] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    // Check saved theme or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
    
    // Apply immediately
    if (dark) {
      document.documentElement.classList.add('dark');
    }
    setIsDark(dark);
  }, []);

  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    
    if (newIsDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <header className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Logo */}
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">BitRAG</h1>
          
          {/* Navigation */}
          <nav className="flex items-center gap-1">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                }`
              }
            >
              <MessageSquare size={18} />
              <span>Chat</span>
            </NavLink>
            
            <NavLink
              to="/documents"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                }`
              }
            >
              <FileText size={18} />
              <span>Documents</span>
            </NavLink>
            
            <NavLink
              to="/graph"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                }`
              }
            >
              <Network size={18} />
              <span>Graph</span>
            </NavLink>
            
            <NavLink
              to="/ollama-params"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                }`
              }
            >
              <Activity size={18} />
              <span>Params</span>
            </NavLink>
          </nav>
        </div>
        
        {/* Right side actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAbout(true)}
            className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
            title="About BitRAG"
          >
            <HelpCircle size={20} />
          </button>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            title={isDark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDark ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          
          <NavLink
            to="/settings"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <Settings size={18} />
            <span>Settings</span>
          </NavLink>
        </div>
      </div>

      {/* About Modal */}
      {showAbout && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowAbout(false)}
        >
          <div 
            className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl border border-gray-200 dark:border-gray-700 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xl">B</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                    BitRAG
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Version 1.0.0</p>
                </div>
              </div>
              <button
                onClick={() => setShowAbout(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Why BitRAG?</h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  BitRAG stands for "Bit" (lightweight, minimal footprint) + "RAG" (Retrieval-Augmented Generation). 
                  Designed to run efficiently on minimal CPU resources with low operational costs - perfect for 
                  home labs, laptops, and resource-constrained environments.
                </p>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">About</h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  BitRAG is a comprehensive Retrieval-Augmented Generation (RAG) application that combines 
                  document management with AI-powered chat capabilities. Upload your documents, build 
                  knowledge graphs, and interact with your data through an intelligent conversational interface.
                </p>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Quick Guide</h4>
                <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">1.</span>
                    <span><strong>Upload Documents:</strong> Go to Documents tab and upload PDF, TXT, DOC, etc.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">2.</span>
                    <span><strong>Start Chatting:</strong> Ask questions about your documents in the Chat tab</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">3.</span>
                    <span><strong>View Graph:</strong> Explore document relationships in the Graph tab</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">4.</span>
                    <span><strong>Configure:</strong> Select models and adjust settings in the Settings tab</span>
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Features</h4>
                <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <span><strong>AI-Powered Chat:</strong> Interact with your documents using natural language</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <span><strong>Document Management:</strong> Upload and organize various file types</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <span><strong>Knowledge Graph:</strong> Visualize relationships between documents</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <span><strong>Ollama Integration:</strong> Configure and fine-tune AI model parameters</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <span><strong>System Monitoring:</strong> Real-time CPU, Memory, and GPU usage tracking</span>
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Technology Stack</h4>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    React
                  </span>
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    TypeScript
                  </span>
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    Tailwind CSS
                  </span>
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    Ollama
                  </span>
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                    React Router
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Built with ❤️ for intelligent document retrieval and analysis
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setShowAbout(false)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}