import { X, Keyboard, Upload, MessageSquare, Settings, FileText } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#111111] border border-gray-300 dark:border-gray-800 rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-800">
          <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">Help & Guide</h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Keyboard Shortcuts */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Keyboard className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">Keyboard Shortcuts</h3>
            </div>
            <div className="space-y-2 bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-mono text-gray-700 dark:text-gray-300">Navigate to Chat</span>
                <kbd className="px-3 py-1 bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded text-sm text-gray-700 dark:text-gray-300 font-mono">C</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-mono text-gray-700 dark:text-gray-300">Navigate to Settings</span>
                <kbd className="px-3 py-1 bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded text-sm text-gray-700 dark:text-gray-300 font-mono">S</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-mono text-gray-700 dark:text-gray-300">Navigate to Documents</span>
                <kbd className="px-3 py-1 bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded text-sm text-gray-700 dark:text-gray-300 font-mono">U</kbd>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">Chat Interface</h3>
            </div>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 font-mono">
              <p>• Type your question about uploaded documents in the chat input</p>
              <p>• Press <kbd className="px-2 py-0.5 bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded text-xs">Enter</kbd> or click Send to submit</p>
              <p>• Click "View Sources" to see which documents were referenced</p>
              <p>• Expand "Thinking..." to see the AI's reasoning process</p>
              <p>• Use the upload button to quickly add documents while chatting</p>
            </div>
          </div>

          {/* Document Management */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">Document Management</h3>
            </div>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 font-mono">
              <p>• Click "Upload Document" to add files to your knowledge base</p>
              <p>• Select multiple documents at once for batch upload</p>
              <p>• Supported formats: PDF, TXT, DOC, DOCX, MD</p>
              <p>• Each file is indexed individually with progress tracking</p>
              <p>• Delete documents you no longer need from the list</p>
            </div>
          </div>

          {/* Settings */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">Settings</h3>
            </div>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 font-mono">
              <p><strong className="text-gray-900 dark:text-white">Ollama Configuration:</strong> Set your local Ollama server port</p>
              <p><strong className="text-gray-900 dark:text-white">Model Selection:</strong> Choose which AI model to use for responses</p>
              <p><strong className="text-gray-900 dark:text-white">Dual Model Mode:</strong> Use two models simultaneously for comparison</p>
              <p><strong className="text-gray-900 dark:text-white">Hybrid Retrieval:</strong> Adjust between vector search, hybrid, or keyword search</p>
              <p>• Download new models or delete unused ones to manage storage</p>
            </div>
          </div>

          {/* Tips */}
          <div>
            <div className="mb-3">
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">💡 Tips</h3>
            </div>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 font-mono bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg p-4">
              <p>• Upload relevant documents before asking questions for better answers</p>
              <p>• Use specific questions to get more accurate responses</p>
              <p>• Check the sources to verify which documents were used</p>
              <p>• Try different retrieval modes for different document types</p>
              <p>• Dual model mode is useful for comparing response quality</p>
            </div>
          </div>

          {/* System Requirements */}
          <div>
            <div className="mb-3">
              <h3 className="text-base font-mono text-gray-900 dark:text-gray-100">⚙️ System Requirements</h3>
            </div>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300 font-mono">
              <p>• Ollama must be installed and running locally</p>
              <p>• At least one AI model must be downloaded</p>
              <p>• Recommended: 8GB+ RAM for smooth operation</p>
              <p>• GPU acceleration recommended for larger models</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
