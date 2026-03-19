import { useState, useEffect } from 'react';
import { X, Trash2 } from 'lucide-react';

interface ModelDeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onModelDeleted?: () => void;
}

export function ModelDeleteModal({ isOpen, onClose, onModelDeleted }: ModelDeleteModalProps) {
  const [installedModels, setInstalledModels] = useState<string[]>([]);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadModels();
    }
  }, [isOpen]);

  const loadModels = async () => {
    try {
      const response = await fetch('/api/models');
      const data = await response.json();
      if (data.models) {
        setInstalledModels(data.models);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const handleDelete = async (modelName: string) => {
    setDeleting(modelName);
    
    try {
      const response = await fetch('/api/models/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: modelName }),
      });

      const data = await response.json();

      if (response.ok) {
        setInstalledModels(installedModels.filter((m) => m !== modelName));
        if (onModelDeleted) onModelDeleted();
      } else {
        alert(`Error: ${data.error || 'Failed to delete model'}`);
      }
    } catch (error) {
      console.error('Error deleting model:', error);
      alert('Failed to delete model');
    } finally {
      setDeleting(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#111111] border border-gray-300 dark:border-gray-800 rounded-lg max-w-lg w-full">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-800">
          <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">Delete Model</h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          {installedModels.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-500 text-center py-8 font-mono">
              No models installed
            </p>
          ) : (
            <div className="space-y-2">
              {installedModels.map((model) => (
                <div
                  key={model}
                  className="flex items-center justify-between bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-3"
                >
                  <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{model}</span>
                  <button
                    onClick={() => handleDelete(model)}
                    disabled={deleting === model}
                    className="text-red-500 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300 transition-colors disabled:opacity-50"
                  >
                    {deleting === model ? (
                      <span className="text-xs font-mono">Deleting...</span>
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
