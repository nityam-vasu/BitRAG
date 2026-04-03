import { Loader2 } from "lucide-react";

export default function LoadingPage() {
  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Status message */}
      <div className="px-6 py-3 text-sm text-gray-600 dark:text-gray-400">
        Loading system info...
      </div>

      {/* Loading content */}
      <div className="flex-1 flex flex-col items-center justify-center">
        <Loader2 className="w-16 h-16 animate-spin text-gray-400 dark:text-gray-500 mb-6" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Initializing...
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Loading embedding model and connecting to Ollama
        </p>
      </div>

      {/* Bottom input area (disabled) */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 opacity-50">
            <button
              disabled
              className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
            >
              📤
            </button>
            
            <input
              type="text"
              disabled
              placeholder="Ask a question about your documents..."
              className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            />
            
            <button
              disabled
              className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
            >
              🎤
            </button>
            
            <button
              disabled
              className="p-3 rounded-lg bg-gray-300 dark:bg-gray-600 text-white"
            >
              ➤
            </button>
          </div>
        </div>
        
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
