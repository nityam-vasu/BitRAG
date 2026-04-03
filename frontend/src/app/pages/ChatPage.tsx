import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { Upload, Send, ChevronRight, FileText, Download, AlertCircle, Loader2, Wifi, WifiOff } from "lucide-react";
import ProcessingCard from "../components/ProcessingCard";

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
  sources?: string[];
  thinking?: string;
}

interface ServerStatus {
  initialized: boolean;
  initializing: boolean;
  documentCount?: number;
}

export default function ChatPage() {
  const navigate = useNavigate();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [showProcessing, setShowProcessing] = useState(false);
  const [processingExpanded, setProcessingExpanded] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [serverStatus, setServerStatus] = useState<ServerStatus>({ initialized: false, initializing: true });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check server initialization status
  useEffect(() => {
    checkServerStatus();
    
    // Poll every 2 seconds while initializing
    const interval = setInterval(() => {
      checkServerStatus();
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('/api/debug');
      if (response.ok) {
        const data = await response.json();
        setServerStatus({
          initialized: data.initialized || false,
          initializing: data.initializing || false,
        });
      } else {
        // If response not ok, server might be initializing
        setServerStatus(prev => ({ ...prev, initializing: true }));
      }
    } catch (err) {
      // Network error - server not ready
      setServerStatus({ initialized: false, initializing: true });
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, showProcessing]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      
      const key = e.key.toLowerCase();
      switch (key) {
        case 'c':
          navigate('/');
          break;
        case 'd':
          navigate('/documents');
          break;
        case 'g':
          navigate('/graph');
          break;
        case 's':
          navigate('/settings');
          break;
        case 'o':
          navigate('/ollama-params');
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    if (!serverStatus.initialized) return;
    
    const userMessage = input.trim();
    setInput("");
    setError(null);
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setShowProcessing(true);
    setProcessingExpanded(true);
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to get response');
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.output || data.response || 'No response',
        sources: data.sources || [],
        thinking: data.thinking
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: err instanceof Error ? err.message : 'An error occurred'
      }]);
    } finally {
      setShowProcessing(false);
    }
  };

  const exportChat = (format: 'txt' | 'pdf') => {
    const chatContent = messages
      .map((msg) => `${msg.role.toUpperCase()}: ${msg.content}${msg.sources ? `\nSources: ${msg.sources.join(', ')}` : ''}`)
      .join('\n\n');
    
    if (format === 'txt') {
      const blob = new Blob([chatContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat-export-${Date.now()}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'pdf') {
      alert('PDF export would be implemented with a library like jsPDF');
    }
    setShowExportMenu(false);
  };
  
  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      {messages.length > 0 && (
        <div className="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Chat</h2>
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white transition-colors"
              >
                <Download size={16} />
                Export Chat
              </button>
              
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg z-10">
                  <button
                    onClick={() => exportChat('txt')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-t-lg transition-colors"
                  >
                    Export as TXT
                  </button>
                  <button
                    onClick={() => exportChat('pdf')}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-b-lg transition-colors"
                  >
                    Export as PDF
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            {(!serverStatus.initialized || serverStatus.initializing) ? (
              // Show loading when initializing
              <>
                <Loader2 className="animate-spin text-blue-500 mb-4" size={48} />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                  Initializing BitRAG
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Please wait while the server is starting...
                </p>
              </>
            ) : (
              // Show welcome when ready
              <>
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to BitRAG
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Upload documents in the Documents tab and start asking questions
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
            {/* Processing Card */}
            {showProcessing && (
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setProcessingExpanded(!processingExpanded)}
                  className="w-full flex items-center gap-3 p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <ChevronRight
                    className={`text-gray-400 transition-transform ${processingExpanded ? 'rotate-90' : ''}`}
                    size={18}
                  />
                  <FileText className="text-blue-500" size={20} />
                  <div className="flex-1">
                    <span className="text-gray-900 dark:text-white font-medium">Processing...</span>
                    <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">(llama3.2:1b)</span>
                  </div>
                </button>

                {processingExpanded && (
                  <div className="px-4 pb-4">
                    <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      Waiting for response...
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* Messages */}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.role === 'error'
                      ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  {message.role === 'error' && (
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle size={16} />
                      <span className="font-medium">Error</span>
                    </div>
                  )}
                  <div>{message.content}</div>
                  {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                      <button className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                        Sources ({message.sources.length}): {message.sources.join(', ')}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 transition-colors"
              title="Upload file"
            >
              <Upload size={20} />
            </button>
            
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={!serverStatus.initialized}
              className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50"
            />
            
            <button
              type="submit"
              className="p-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!input.trim() || !serverStatus.initialized}
              title="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
        
        {/* Keyboard shortcuts */}
        <div className="max-w-4xl mx-auto mt-2 flex items-center justify-center gap-4 text-xs text-gray-500 dark:text-gray-500">
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">C</kbd> Chat</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">D</kbd> Documents</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">G</kbd> Graph</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">S</kbd> Settings</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">O</kbd> Ollama</span>
        </div>
      </div>
    </div>
  );
}