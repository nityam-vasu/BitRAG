import { X, FileText } from 'lucide-react';

interface SourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: string[];
}

export function SourcesModal({ isOpen, onClose, sources }: SourcesModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#111111] border border-gray-300 dark:border-gray-800 rounded-lg max-w-md w-full">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-800">
          <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">Sources</h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          <div className="space-y-2">
            {sources.map((source, index) => (
              <div
                key={index}
                className="flex items-center gap-3 bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg px-4 py-3"
              >
                <FileText className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{source}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}