import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, Trash2, Loader2 } from 'lucide-react'
import { getDocuments, uploadDocument, deleteDocument, Document } from '../api'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadDocuments = async () => {
    setLoading(true)
    setError(null)
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err) {
      setError('Failed to load documents')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setError(null)

    try {
      for (const file of Array.from(files)) {
        const result = await uploadDocument(file)
        if (!result.success) {
          throw new Error(`Failed to upload ${file.name}`)
        }
      }
      await loadDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Delete "${doc.name}"?`)) return

    try {
      await deleteDocument(doc.name)
      await loadDocuments()
    } catch (err) {
      setError('Failed to delete document')
      console.error(err)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Documents</h2>
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md,.doc,.docx"
              multiple
              onChange={handleUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
            >
              {uploading ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
              Upload Documents
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-600/20 border border-red-600 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-blue-500" size={32} />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <FileText size={48} className="mx-auto mb-4 opacity-50" />
            <p>No documents uploaded yet</p>
            <p className="text-sm mt-2">Click "Upload Documents" to get started</p>
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map(doc => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-gray-800 rounded-lg hover:bg-gray-750"
              >
                <div className="flex items-center gap-3">
                  <FileText className="text-blue-400" size={24} />
                  <span className="font-medium">{doc.name}</span>
                </div>
                <button
                  onClick={() => handleDelete(doc)}
                  className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 bg-gray-800">
        <p className="text-sm text-gray-400">
          {documents.length} document{documents.length !== 1 ? 's' : ''} indexed
        </p>
      </div>
    </div>
  )
}
