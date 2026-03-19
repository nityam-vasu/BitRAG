import { useState } from 'react';
import { X, Download } from 'lucide-react';

interface ModelDownloadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onModelDownloaded?: () => void;
}

export function ModelDownloadModal({ isOpen, onClose, onModelDownloaded }: ModelDownloadModalProps) {
  const [customModel, setCustomModel] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [currentModel, setCurrentModel] = useState('');
  const [error, setError] = useState<string | null>(null);

  const availableModels = [
    'llama3.2',
    'mistral',
    'phi3',
    'qwen2.5',
    'codellama',
    'deepseek-coder',
  ];

  const handleDownload = async (modelName: string) => {
    setDownloading(true);
    setCurrentModel(modelName);
    setError(null);

    try {
      const response = await fetch('/api/models/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: modelName }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Failed to download model');
        return;
      }

      // Success - close modal
      setTimeout(() => {
        setDownloading(false);
        setCurrentModel('');
        if (onModelDownloaded) onModelDownloaded();
        onClose();
      }, 1000);
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      // Keep UI showing progress for a moment
      setTimeout(() => {
        setDownloading(false);
        setCurrentModel('');
      }, 2000);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#111111] border border-gray-300 dark:border-gray-800 rounded-lg max-w-lg w-full">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-800">
          <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">Download Model</h2>
          <button
            onClick={onClose}
            disabled={downloading}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Available Models */}
          <div>
            <h3 className="text-sm font-mono text-gray-600 dark:text-gray-400 mb-3">Available Models</h3>
            <div className="space-y-2">
              {availableModels.map((model) => (
                <button
                  key={model}
                  onClick={() => handleDownload(model)}
                  disabled={downloading}
                  className="w-full flex items-center justify-between bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-3 hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{model}</span>
                  {downloading && currentModel === model ? (
                    <span className="text-xs text-gray-500 dark:text-gray-400">Downloading...</span>
                  ) : (
                    <Download className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Model */}
          <div>
            <h3 className="text-sm font-mono text-gray-600 dark:text-gray-400 mb-3">Custom Model</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={customModel}
                onChange={(e) => setCustomModel(e.target.value)}
                placeholder="Enter model name..."
                disabled={downloading}
                className="flex-1 bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-2 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-600 focus:outline-none focus:border-gray-400 dark:focus:border-gray-700 disabled:opacity-50"
              />
              <button
                onClick={() => customModel && handleDownload(customModel)}
                disabled={!customModel || downloading}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Download
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-800/50 rounded-lg px-3 py-2">
              <p className="text-xs text-red-800 dark:text-red-200 font-mono">
                {error}
              </p>
            </div>
          )}

          {/* Progress Bar */}
          {downloading && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                  Downloading {currentModel}...
                </span>
                <div className="animate-spin w-4 h-4 border-2 border-gray-600 dark:border-gray-400 border-t-transparent rounded-full"></div>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-900 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gray-600 dark:bg-gray-600 h-full transition-all duration-300 animate-pulse"
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
