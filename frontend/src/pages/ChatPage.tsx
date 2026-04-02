import { useState, useRef, useEffect } from 'react'
import { Send, Download, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { sendChat, ChatMessage, getDocuments, getCurrentChatExportUrl } from '../api'

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasDocuments, setHasDocuments] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check if documents exist
  useEffect(() => {
    getDocuments().then(docs => setHasDocuments(docs.length > 0))
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChat(input.trim())
      setMessages(prev => [...prev, response])
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'assistant',
        content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    // Use the export endpoint to get the formatted export
    const url = getCurrentChatExportUrl()
    window.open(url, '_blank')
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Chat</h2>
          <button
            onClick={handleExport}
            disabled={messages.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50"
          >
            <Download size={16} />
            Export Chat
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!hasDocuments && (
          <div className="text-center py-8 text-gray-400">
            <p>No documents indexed yet.</p>
            <p className="text-sm mt-2">Go to Documents page to upload PDFs.</p>
          </div>
        )}

        {messages.map(message => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-4 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-100'
              }`}
            >
              {message.type === 'user' ? (
                <p>{message.content}</p>
              ) : (
                <>
                  {message.thinking && (
                    <details className="mb-2 text-sm opacity-75">
                      <summary className="cursor-pointer">Thinking...</summary>
                      <pre className="mt-1 p-2 bg-gray-800 rounded text-xs whitespace-pre-wrap">
                        {message.thinking}
                      </pre>
                    </details>
                  )}
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-600 text-xs text-gray-300">
                      Sources: {message.sources.join(', ')}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 rounded-lg p-4">
              <Loader2 className="animate-spin" size={20} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700 bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={hasDocuments ? 'Ask a question...' : 'Upload documents first...'}
            disabled={!hasDocuments || loading}
            className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || !hasDocuments || loading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
            Send
          </button>
        </div>
      </form>
    </div>
  )
}
