"""
BitRAG Document Indexer

Handles PDF loading, text chunking, embedding, and storage in ChromaDB.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pypdf import PdfReader
import chromadb

from .config import get_config


class DocumentIndexer:
    """Handles document indexing for BitRAG"""

    def __init__(
        self, session_id: str, progress_callback: Optional[Callable[[str, int], None]] = None
    ):
        """
        Initialize the document indexer.

        Args:
            session_id: Session ID for isolation
            progress_callback: Optional callback for progress updates
        """
        self.config = get_config()
        self.session_id = session_id
        self.progress_callback = progress_callback

        # Set up paths
        self.session_dir = self.config.get_session_dir(session_id)
        self.uploads_dir = self.config.get_session_uploads_dir(session_id)
        self.chroma_dir = self.config.get_session_chroma_dir(session_id)

        # Create directories
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.chroma_dir, exist_ok=True)

        # Initialize ChromaDB
        self._init_chroma()

        # Initialize embedding model
        self._init_embedding()

        # Initialize index
        self._init_index()

    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))

        # Get or create collection
        collection_name = f"{self.config.collection_name}_{self.session_id}"
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"session_id": self.session_id}
        )

        # Create vector store
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

    def _init_embedding(self):
        """Initialize embedding model"""
        self._report_progress("Loading embedding model...", 0)
        self.embedding_model = HuggingFaceEmbedding(model_name=self.config.embedding_model)
        self._report_progress("Embedding model loaded", 10)

    def _init_index(self):
        """Initialize or load existing index"""
        self._report_progress("Initializing index...", 15)

        # Create storage context
        from llama_index.core import StorageContext

        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Try to load existing index
        index_path = self.session_dir / "index"
        if index_path.exists():
            self._report_progress("Loading existing index...", 20)
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embedding_model
            )
        else:
            self._report_progress("Creating new index...", 20)
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embedding_model
            )

        # Create node parser
        self.node_parser = SentenceSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )

    def _report_progress(self, message: str, percentage: int):
        """Report progress to callback"""
        if self.progress_callback:
            self.progress_callback(message, percentage)

    def index_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Index a document (PDF).

        Args:
            file_path: Path to PDF file
            metadata: Optional metadata for the document

        Returns:
            Document ID
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Copy file to uploads directory
        dest_path = self.uploads_dir / file_path.name
        import shutil

        shutil.copy2(file_path, dest_path)

        self._report_progress(f"Loading PDF: {file_path.name}...", 25)

        # Load PDF using pypdf
        try:
            reader = PdfReader(str(dest_path))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Handle None return value
                    text += page_text + "\n"

            # Check if any text was extracted
            if not text.strip():
                raise ValueError(f"No text could be extracted from PDF: {file_path.name}")
        except Exception as e:
            # Clean up the temp file
            if dest_path.exists():
                dest_path.unlink()
            raise ValueError(f"Failed to read PDF file: {str(e)}") from e

        # Create LlamaIndex Document
        doc = Document(text=text, metadata=metadata or {})
        doc.metadata["file_name"] = file_path.name
        doc.metadata["file_path"] = str(dest_path)
        doc.metadata["indexed_at"] = datetime.now().isoformat()
        doc.metadata["session_id"] = self.session_id

        self._report_progress("Extracting text...", 40)

        # Parse nodes
        self._report_progress("Chunking text...", 50)
        nodes = self.node_parser.get_nodes_from_documents([doc])

        # Create embeddings
        self._report_progress("Creating embeddings...", 65)
        # Embeddings are created automatically during indexing

        # Index documents
        self._report_progress("Storing in vector database...", 80)

        # Use insert approach for ChromaDB
        for node in nodes:
            # Get embedding
            embedding = self.embedding_model.get_text_embedding(node.get_content())

            # Add to collection
            self.collection.upsert(
                ids=[node.node_id],
                embeddings=[embedding],
                documents=[node.get_content()],
                metadatas=[node.metadata],
            )

        self._report_progress("Indexing complete!", 100)

        # Return document ID (use filename as ID)
        doc_id = file_path.stem
        return doc_id

    def index_documents(
        self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Index multiple documents.

        Args:
            file_paths: List of paths to PDF files
            metadata: Optional metadata for documents

        Returns:
            List of document IDs
        """
        doc_ids = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths):
            # Calculate progress for this document
            base_progress = int((i / total) * 100)

            doc_id = self.index_document(file_path, metadata)
            doc_ids.append(doc_id)

        return doc_ids

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all indexed documents.

        Returns:
            List of document metadata
        """
        results = self.collection.get()

        documents = []
        seen_files = set()

        for i, doc_id in enumerate(results.get("ids", [])):
            metadata = results.get("metadatas", [{}])[i]
            file_name = metadata.get("file_name", "unknown")

            # Avoid duplicates
            if file_name not in seen_files:
                seen_files.add(file_name)
                documents.append(
                    {
                        "id": doc_id,
                        "file_name": file_name,
                        "indexed_at": metadata.get("indexed_at", "unknown"),
                        "session_id": metadata.get("session_id", "unknown"),
                    }
                )

        return documents

    def get_document_count(self) -> int:
        """Get total number of indexed documents"""
        return self.collection.count()

    def delete_document(self, doc_id: str):
        """
        Delete a document from the index by chunk/node ID.

        Args:
            doc_id: Document ID (chunk ID) to delete
        """
        self.collection.delete(ids=[doc_id])

    def delete_document_by_filename(self, filename: str):
        """
        Delete all chunks associated with a document by filename.

        Args:
            filename: Name of the file to delete
        """
        # Find all chunks with matching filename
        results = self.collection.get(where={"file_name": filename})

        if not results.get("ids"):
            raise ValueError(f"Document not found: {filename}")

        # Delete all matching chunks
        ids_to_delete = results["ids"]
        self.collection.delete(ids=ids_to_delete)

        # Also delete the uploaded file if it exists
        uploaded_file = self.uploads_dir / filename
        if uploaded_file.exists():
            uploaded_file.unlink()

        return len(ids_to_delete)

    def get_document(self, filename: str) -> Dict[str, Any]:
        """
        Get document details by filename.

        Args:
            filename: Name of the file

        Returns:
            Document details including all chunks
        """
        results = self.collection.get(where={"file_name": filename})

        if not results.get("ids"):
            raise ValueError(f"Document not found: {filename}")

        chunks = []
        for i, doc_id in enumerate(results.get("ids", [])):
            chunks.append(
                {
                    "id": doc_id,
                    "text": results.get("documents", [""])[i],
                    "metadata": results.get("metadatas", [{}])[i],
                }
            )

        return {
            "filename": filename,
            "total_chunks": len(chunks),
            "chunks": chunks,
        }

    def update_document_metadata(self, filename: str, metadata: Dict[str, Any]):
        """
        Update metadata for all chunks of a document.

        Args:
            filename: Name of the file
            metadata: New metadata to apply
        """
        results = self.collection.get(where={"file_name": filename})

        if not results.get("ids"):
            raise ValueError(f"Document not found: {filename}")

        ids_to_update = results["ids"]
        current_metadatas = results.get("metadatas", [{}])

        # Update each chunk's metadata
        for i, doc_id in enumerate(ids_to_update):
            updated_metadata = {**current_metadatas[i], **metadata}
            self.collection.update(
                ids=[doc_id],
                metadatas=[updated_metadata],
            )

    def clear_index(self):
        """Clear all documents from the index"""
        self.collection.delete(where={})

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results (default: config.top_k)

        Returns:
            List of similar documents
        """
        if top_k is None:
            top_k = self.config.top_k

        # Get query embedding
        query_embedding = self.embedding_model.get_text_embedding(query)

        # Search
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

        documents = []
        for i in range(len(results.get("ids", [[]])[0])):
            documents.append(
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                }
            )

        return documents


def create_session_indexer(
    session_id: str, progress_callback: Optional[Callable[[str, int], None]] = None
) -> DocumentIndexer:
    """
    Create a DocumentIndexer for a specific session.

    Args:
        session_id: Session ID
        progress_callback: Optional callback for progress updates

    Returns:
        DocumentIndexer instance
    """
    return DocumentIndexer(session_id, progress_callback)
