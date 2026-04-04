import { useState, useEffect, useRef } from "react";
import { Upload, Send, ChevronRight, FileText, Download } from "lucide-react";
import ProcessingCard from "../components/ProcessingCard";
import { sendChat } from "../../api/index";
import { useServerStatus } from "../context/ServerStatusContext";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [showProcessing, setShowProcessing] = useState(false);
  const [processingExpanded, setProcessingExpanded] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const { serverStatus } = useServerStatus();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, showProcessing]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !serverStatus.initialized) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setShowProcessing(true);
    
    try {
      const response = await sendChat(input);
      setMessages(prev => [...prev, {
        id: response.id,
        role: 'assistant',
        content: response.content,
        sources: response.sources
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: err instanceof Error ? err.message : 'Failed to get response'
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
            {!serverStatus.initialized ? (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                  Initializing BitRAG...
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Please wait while the server is starting
                </p>
              </>
            ) : (
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
                  </div>
                </button>

                {processingExpanded && (
                  <div className="px-4 pb-4">
                    <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300">
                      Waiting for response...
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* Messages */}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }`}
                >
                  <div>{message.content}</div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600 text-sm opacity-75">
                      Sources: {message.sources.join(', ')}
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
        <div className="max-w-4xl mx-auto mt-2 flex items-center justify-center gap-6 text-xs text-gray-500 dark:text-gray-500">
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">C</kbd> → Chat</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">S</kbd> → Settings</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">D</kbd> → Documents</span>
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">G</kbd> → Graph</span>
        </div>
      </div>
    </div>
  );
}
