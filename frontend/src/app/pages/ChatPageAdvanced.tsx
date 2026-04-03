import { useState } from "react";
import { Upload, Send, Mic, ChevronRight, FileText } from "lucide-react";

export default function ChatPageAdvanced() {
  const [input, setInput] = useState("");
  const [showProcessing, setShowProcessing] = useState(true);
  const [processingExpanded, setProcessingExpanded] = useState(false);

  const mockProcessingContent = `The provided context appears to be about creating a comic page composition tool that allows users to manually control panel size, arrangement, and flow. It also mentions implementing post-processing steps for adding dialogue in scene images using a Large Language Model (LLM). However, the main focus is on developing a non-AI, user-based interface component.

Based on this context, I can provide a concise summary:

The goal is to create a comic page composition tool with manual control over panel size and arrangement. The tool will also include post-processing steps for adding dialogue in scene images using an LLM.`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* Summarize button */}
          <div className="flex justify-end">
            <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg text-gray-900 dark:text-white transition-colors">
              Summarize it
            </button>
          </div>

          {/* Processing Card */}
          {showProcessing && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setProcessingExpanded(!processingExpanded)}
                className="w-full flex items-center gap-3 p-4 text-left"
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
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300">
                    {mockProcessingContent}
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                    <button className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                      View Sources (3)
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
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
              className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
            
            <button
              type="button"
              className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 transition-colors"
              title="Voice input"
            >
              <Mic size={20} />
            </button>
            
            <button
              type="submit"
              className="p-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
          <span><kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">U</kbd> → Upload</span>
        </div>
      </div>
    </div>
  );
}
