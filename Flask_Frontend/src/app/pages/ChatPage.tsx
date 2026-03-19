import { useState, useEffect, useRef } from 'react';
import { Layout } from '../components/Layout';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { Upload } from 'lucide-react';
import { useNavigate } from 'react-router';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  query?: string;
  thinking?: string;
  output?: string;
  sources?: string[];
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const [serverReady, setServerReady] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Check server status on mount
  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      if (data.status === 'initializing') {
        setServerReady(false);
        setIsInitializing(true);
        // Keep checking
        const interval = setInterval(async () => {
          try {
            const res = await fetch('/api/status');
            const statusData = await res.json();
            if (statusData.status === 'ready') {
              setServerReady(true);
              setIsInitializing(false);
              clearInterval(interval);
            }
          } catch {
            // Continue polling
          }
        }, 2000);
      }
    } catch {
      // Server might still be starting
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!serverReady) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'assistant',
        thinking: '',
        output: 'Server is still initializing. Please wait a moment...',
        sources: []
      }]);
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      query: message,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Add placeholder for AI response
    const aiMessageId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, {
      id: aiMessageId,
      type: 'assistant',
      thinking: 'Thinking...',
      output: '',
      sources: []
    }]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: message }),
      });

      const data = await response.json();

      if (data.error) {
        setMessages(prev => prev.map(msg => 
          msg.id === aiMessageId 
            ? { 
                ...msg, 
                output: data.message || data.error,
                thinking: 'Error occurred'
              }
            : msg
        ));
      } else {
        setMessages(prev => prev.map(msg => 
          msg.id === aiMessageId 
            ? { 
                ...msg, 
                thinking: data.thinking || '',
                output: data.output || '',
                sources: data.sources || []
              }
            : msg
        ));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { 
              ...msg, 
              output: 'Failed to connect to server',
              thinking: 'Connection error'
            }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadFiles = () => {
    navigate('/documents');
  };

  return (
    <Layout>
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6">
          {isInitializing && !serverReady ? (
            <div className="text-center py-12">
              <div className="animate-spin w-8 h-8 border-2 border-gray-600 dark:border-gray-400 border-t-transparent rounded-full mx-auto mb-4"></div>
              <h2 className="text-xl font-mono text-gray-600 dark:text-gray-400 mb-2">
                Initializing...
              </h2>
              <p className="text-sm font-mono text-gray-500 dark:text-gray-500">
                Loading embedding model and connecting to Ollama
              </p>
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-12">
              <h2 className="text-xl font-mono text-gray-600 dark:text-gray-400 mb-2">
                Welcome to BitRAG
              </h2>
              <p className="text-sm font-mono text-gray-500 dark:text-gray-500">
                Upload documents in the Documents tab and start asking questions
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#111111] p-6">
          <div className="flex items-end gap-3">
            <button
              onClick={handleUploadFiles}
              className="p-3 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              title="Upload files"
            >
              <Upload className="w-5 h-5" />
            </button>
            <ChatInput onSend={handleSendMessage} disabled={isLoading || !serverReady} />
          </div>
        </div>
      </div>
    </Layout>
  );
}