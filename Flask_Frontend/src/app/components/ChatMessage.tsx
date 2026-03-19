import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SourcesModal } from './SourcesModal';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  query?: string;
  thinking?: string;
  output?: string;
  sources?: string[];
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [thinkingExpanded, setThinkingExpanded] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(false);

  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-3">
          <p className="text-gray-900 dark:text-gray-100">{message.query}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Thinking Section */}
      {message.thinking && (
        <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#0f0f0f]">
          <button
            onClick={() => setThinkingExpanded(!thinkingExpanded)}
            className="w-full flex items-center gap-2 px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-colors rounded-lg"
          >
            {thinkingExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            )}
            <span className="text-sm font-mono text-gray-500 dark:text-gray-400">Thinking...</span>
          </button>
          {thinkingExpanded && (
            <div className="px-4 pb-4">
              <div className="text-sm text-gray-600 dark:text-gray-400 font-mono whitespace-pre-wrap bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded p-3">
                {message.thinking}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Model Output */}
      {message.output && (
        <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#0f0f0f] p-4">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code: ({ className, children, ...props }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-gray-200 dark:bg-gray-900 px-1.5 py-0.5 rounded text-gray-700 dark:text-gray-300 font-mono text-sm" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className="block bg-gray-200 dark:bg-gray-900 p-3 rounded font-mono text-sm overflow-x-auto text-gray-800 dark:text-gray-200" {...props}>
                      {children}
                    </code>
                  );
                },
                p: ({ children }) => <p className="text-gray-700 dark:text-gray-300 mb-3 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="text-gray-700 dark:text-gray-300 mb-3 list-disc pl-6">{children}</ul>,
                ol: ({ children }) => <ol className="text-gray-700 dark:text-gray-300 mb-3 list-decimal pl-6">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                strong: ({ children }) => <strong className="text-gray-900 dark:text-white font-semibold">{children}</strong>,
              }}
            >
              {message.output}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Sources Button */}
      {message.sources && message.sources.length > 0 && (
        <div>
          <button
            onClick={() => setSourcesOpen(true)}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-mono border border-gray-300 dark:border-gray-800 px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            View Sources ({message.sources.length})
          </button>
        </div>
      )}

      {/* Sources Modal */}
      {message.sources && (
        <SourcesModal
          isOpen={sourcesOpen}
          onClose={() => setSourcesOpen(false)}
          sources={message.sources}
        />
      )}
    </div>
  );
}