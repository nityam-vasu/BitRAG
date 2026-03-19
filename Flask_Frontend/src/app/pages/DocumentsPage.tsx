import { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { Upload, Trash2 } from 'lucide-react';
import { UploadDocumentModal } from '../components/UploadDocumentModal';

interface Document {
  id: string;
  name: string;
}

export function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await fetch('/api/documents');
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    setDeleting(id);
    
    try {
      const response = await fetch(`/api/documents/${encodeURIComponent(id)}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setDocuments(documents.filter((doc) => doc.id !== id));
      } else {
        const error = await response.json();
        alert(`Error deleting document: ${error.error}`);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Failed to delete document');
    } finally {
      setDeleting(null);
    }
  };

  const handleUploadComplete = (fileName: string) => {
    loadDocuments(); // Reload the document list
  };

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-mono text-gray-900 dark:text-gray-100">Document Management</h1>
            <button
              onClick={() => setUploadModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg transition-colors"
            >
              <Upload className="w-4 h-4" />
              Upload Document
            </button>
          </div>

          {/* Indexed Documents */}
          <div className="border border-gray-300 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-[#111111] p-6">
            <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100 mb-4">Indexed Documents</h2>
            
            {loading ? (
              <p className="text-sm text-gray-500 dark:text-gray-500 text-center py-8 font-mono">
                Loading documents...
              </p>
            ) : documents.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-500 text-center py-8 font-mono">
                No documents indexed yet. Upload PDF documents to get started.
              </p>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-3"
                  >
                    <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{doc.name}</span>
                    <button
                      onClick={() => handleDeleteDocument(doc.id)}
                      disabled={deleting === doc.id}
                      className="text-red-500 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300 transition-colors disabled:opacity-50 flex items-center gap-2"
                    >
                      {deleting === doc.id ? (
                        <span className="text-xs font-mono">Deleting...</span>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4" />
                          <span className="text-xs font-mono">Delete</span>
                        </>
                      )}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <UploadDocumentModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />
    </Layout>
  );
}