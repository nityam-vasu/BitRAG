import { Link, useLocation } from 'react-router';
import { FileText, Settings, MessageSquare, HelpCircle, Network } from 'lucide-react';
import { SystemStatus } from './SystemStatus';
import { ShortcutsBar } from './ShortcutsBar';
import { ThemeToggle } from './ThemeToggle';
import { HelpModal } from './HelpModal';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [helpModalOpen, setHelpModalOpen] = useState(false);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only trigger if no input is focused
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key.toLowerCase() === 'c') {
        navigate('/');
      } else if (e.key.toLowerCase() === 's') {
        navigate('/settings');
      } else if (e.key.toLowerCase() === 'u') {
        navigate('/documents');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [navigate]);

  // Helper function for navigation to prevent full refresh
  const handleNavigation = (e: React.MouseEvent, path: string) => {
    e.preventDefault();
    navigate(path);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-[#0d0d0d] text-gray-900 dark:text-gray-100 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#111111]">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <a 
              href="/" 
              onClick={(e) => handleNavigation(e, '/')}
              className="text-xl font-mono tracking-tight text-gray-900 dark:text-gray-100 hover:text-gray-700 dark:hover:text-white transition-colors"
            >
              BitRAG
            </a>
            <a
              href="/"
              onClick={(e) => handleNavigation(e, '/')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/'
                  ? 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-800/50'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Chat
            </a>
            <a
              href="/documents"
              onClick={(e) => handleNavigation(e, '/documents')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/documents'
                  ? 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-800/50'
              }`}
            >
              <FileText className="w-4 h-4" />
              Documents
            </a>
            <a
              href="/graph"
              onClick={(e) => handleNavigation(e, '/graph')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/graph'
                  ? 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-800/50'
              }`}
            >
              <Network className="w-4 h-4" />
              Graph
            </a>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setHelpModalOpen(true)}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              title="Help & Guide"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
            <ThemeToggle />
            <a
              href="/settings"
              onClick={(e) => handleNavigation(e, '/settings')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/settings'
                  ? 'bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-800/50'
              }`}
            >
              <Settings className="w-4 h-4" />
              Settings
            </a>
          </div>
        </div>
        
        {/* System Status */}
        <SystemStatus />
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {children}
      </main>

      {/* Shortcuts Bar */}
      <ShortcutsBar />

      {/* Help Modal */}
      <HelpModal isOpen={helpModalOpen} onClose={() => setHelpModalOpen(false)} />
    </div>
  );
}