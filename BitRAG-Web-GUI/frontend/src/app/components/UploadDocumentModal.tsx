import { useState, useRef } from 'react';
import { X, Upload, CheckCircle, File, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

interface UploadDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete: (fileName: string) => void;
}

interface FileProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export function UploadDocumentModal({ isOpen, onClose, onUploadComplete }: UploadDocumentModalProps) {
  const [selectedFiles, setSelectedFiles] = useState<FileProgress[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const fileProgresses: FileProgress[] = files.map(file => ({
      file,
      progress: 0,
      status: 'pending'
    }));
    setSelectedFiles(fileProgresses);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);

    // Process files sequentially
    for (let i = 0; i < selectedFiles.length; i++) {
      await processFile(i);
    }

    // Wait a moment to show completion, then close
    setTimeout(() => {
      const successfulFiles = selectedFiles.filter(fp => fp.status === 'success');
      successfulFiles.forEach(fp => {
        onUploadComplete(fp.file.name);
      });
      handleClose();
    }, 1000);
  };

  const processFile = (index: number): Promise<void> => {
    return new Promise((resolve) => {
      // Update status to uploading
      setSelectedFiles(prev => {
        const updated = [...prev];
        updated[index] = { ...updated[index], status: 'uploading', progress: 0 };
        return updated;
      });

      // Upload the file
      const formData = new FormData();
      formData.append('file', selectedFiles[index].file);

      fetch('/api/documents', {
        method: 'POST',
        body: formData,
      })
        .then(async (response) => {
          let data;
          const contentType = response.headers.get('content-type');
          
          // Check if response is JSON
          if (contentType && contentType.includes('application/json')) {
            data = await response.json();
          } else {
            // Not JSON - get text instead
            const text = await response.text();
            data = { 
              error: 'Server error', 
              message: `Server returned ${response.status}: ${text.substring(0, 100)}` 
            };
          }

          // Simulate progress
          const interval = setInterval(() => {
            setSelectedFiles(prev => {
              const updated = [...prev];
              const current = updated[index];

              if (current.progress >= 100) {
                clearInterval(interval);
                if (data.error) {
                  updated[index] = {
                    ...current,
                    progress: 100,
                    status: 'error',
                    error: data.message || data.error
                  };
                  // Show error toast
                  toast.error(`Failed to upload ${selectedFiles[index].file.name}`, {
                    description: data.message || data.error,
                  });
                } else {
                  updated[index] = {
                    ...current,
                    progress: 100,
                    status: 'success'
                  };
                  // Show success toast
                  toast.success(`Successfully indexed ${selectedFiles[index].file.name}`);
                }
                resolve();
                return updated;
              }

              updated[index] = { ...current, progress: current.progress + 20 };
              return updated;
            });
          }, 200);
        })
        .catch(error => {
          setSelectedFiles(prev => {
            const updated = [...prev];
            updated[index] = {
              ...updated[index],
              status: 'error',
              progress: 100,
              error: error.message || 'Network error'
            };
            return updated;
          });
          toast.error(`Failed to upload ${selectedFiles[index].file.name}`, {
            description: error.message || 'Network error - is the server running?',
          });
          resolve();
        });
    });
  };

  const handleClose = () => {
    if (!uploading) {
      setSelectedFiles([]);
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onClose();
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#111111] border border-gray-300 dark:border-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-300 dark:border-gray-800">
          <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">Upload Documents</h2>
          <button
            onClick={handleClose}
            disabled={uploading}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* File Input (Hidden) */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.doc,.docx,.md"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Browse Button */}
          <div>
            <button
              onClick={handleBrowseClick}
              disabled={uploading}
              className="w-full flex items-center justify-center gap-2 px-4 py-8 bg-gray-100 dark:bg-gray-900 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload className="w-6 h-6" />
              <span className="font-mono">Click to browse files</span>
            </button>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2 font-mono text-center">
              Supported formats: PDF
            </p>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-mono text-gray-600 dark:text-gray-400">
                Selected Files ({selectedFiles.length})
              </h3>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {selectedFiles.map((fileProgress, index) => (
                  <div
                    key={index}
                    className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#0f0f0f] p-4"
                  >
                    <div className="flex items-start gap-3 mb-2">
                      <File className="w-4 h-4 text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-mono text-gray-700 dark:text-gray-300 truncate">
                          {fileProgress.file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 font-mono">
                          {(fileProgress.file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                      {fileProgress.status === 'success' && (
                        <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400 flex-shrink-0" />
                      )}
                      {fileProgress.status === 'error' && (
                        <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-400 flex-shrink-0" />
                      )}
                    </div>

                    {/* Progress Bar */}
                    {(fileProgress.status === 'uploading' || fileProgress.status === 'success' || fileProgress.status === 'error') && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-mono text-gray-600 dark:text-gray-400">
                            {fileProgress.status === 'success' ? 'Indexed' : fileProgress.status === 'error' ? 'Error' : 'Indexing...'}
                          </span>
                          <span className="text-xs font-mono text-gray-600 dark:text-gray-400">
                            {fileProgress.progress}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-900 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full transition-all duration-200 ${
                              fileProgress.status === 'success'
                                ? 'bg-green-500 dark:bg-green-400'
                                : fileProgress.status === 'error'
                                ? 'bg-red-500 dark:bg-red-400'
                                : 'bg-gray-600 dark:bg-gray-600'
                            }`}
                            style={{ width: `${fileProgress.progress}%` }}
                          />
                        </div>
                        {fileProgress.error && (
                          <p className="text-xs text-red-500 dark:text-red-400 mt-1 font-mono">
                            {fileProgress.error}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Button */}
          {selectedFiles.length > 0 && !uploading && selectedFiles.every(f => f.status === 'pending') && (
            <button
              onClick={handleUpload}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors font-mono"
            >
              <Upload className="w-4 h-4" />
              Upload & Index {selectedFiles.length} {selectedFiles.length === 1 ? 'Document' : 'Documents'}
            </button>
          )}

          {/* Uploading Status */}
          {uploading && (
            <div className="flex items-center justify-center gap-2 text-gray-600 dark:text-gray-400 font-mono text-sm">
              <div className="animate-spin w-4 h-4 border-2 border-gray-600 dark:border-gray-400 border-t-transparent rounded-full"></div>
              Processing documents...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}