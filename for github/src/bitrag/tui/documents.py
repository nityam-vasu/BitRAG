#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Document Management UI

TUI-specific document management interface.
"""

from __future__ import annotations

import os
import glob
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass


# Lazy imports
def _get_config():
    """Lazy import of get_config."""
    from bitrag.core.config import get_config

    return get_config


@dataclass
class DocumentInfo:
    """Document information for display."""

    id: str
    file_name: str
    indexed_at: str
    total_chunks: int
    source: str = ""


class DocumentManagerUI:
    """
    TUI document management interface.

    Features:
    - Browse for PDF files
    - Upload with progress
    - List indexed documents
    - Delete documents
    - Show document details
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self._indexer = None
        self._documents: list[DocumentInfo] = []

        # Callbacks
        self.on_document_added: Callable[[DocumentInfo], None] | None = None
        self.on_document_deleted: Callable[[str], None] | None = None
        self.on_error: Callable[[str], None] | None = None

    @property
    def indexer(self):
        """Lazy load indexer."""
        if self._indexer is None:
            from bitrag.core.indexer import DocumentIndexer

            self._indexer = DocumentIndexer(self.session_id)
        return self._indexer

    def browse_pdfs(
        self,
        search_dirs: list[str] | None = None,
    ) -> list[str]:
        """
        Browse for PDF files in common locations.

        Args:
            search_dirs: Directories to search (defaults to common locations)

        Returns:
            List of PDF file paths
        """
        if search_dirs is None:
            home = os.path.expanduser("~")
            search_dirs = [
                os.path.join(home, "Documents"),
                os.path.join(home, "Downloads"),
                os.path.join(home, "Desktop"),
                os.path.join(home, "Documents/PDFs"),
            ]

        pdf_files = []
        for directory in search_dirs:
            if os.path.exists(directory):
                pattern = os.path.join(directory, "*.pdf")
                pdf_files.extend(glob.glob(pattern))

        # Remove duplicates and sort by modification time
        pdf_files = list(set(pdf_files))
        pdf_files.sort(key=os.path.getmtime, reverse=True)

        return pdf_files

    def upload_document(
        self,
        path: str,
        progress_callback: Callable[[str], None] | None = None,
    ) -> DocumentInfo | None:
        """
        Upload and index a document.

        Args:
            path: Path to the document
            progress_callback: Optional callback for progress

        Returns:
            DocumentInfo if successful, None otherwise
        """
        try:
            if progress_callback:
                progress_callback(f"Loading: {os.path.basename(path)}")

            if not os.path.exists(path):
                if self.on_error:
                    self.on_error(f"File not found: {path}")
                return None

            # Check file extension
            ext = os.path.splitext(path)[1].lower()
            if ext not in [".pdf", ".txt", ".docx"]:
                if self.on_error:
                    self.on_error(f"Unsupported file type: {ext}")
                return None

            if progress_callback:
                progress_callback("Indexing document...")

            # Index the document
            metadata = {
                "source": "tui",
                "file_name": os.path.basename(path),
            }
            doc_id = self.indexer.index_document(path, metadata=metadata)

            if progress_callback:
                progress_callback("Complete!")

            # Get document info
            doc_info = self._get_document_info(doc_id)

            if self.on_document_added:
                self.on_document_added(doc_info)

            return doc_info

        except Exception as e:
            if self.on_error:
                self.on_error(f"Error: {str(e)}")
            return None

    def list_documents(self) -> list[DocumentInfo]:
        """
        List all indexed documents.

        Returns:
            List of DocumentInfo objects
        """
        try:
            docs = self.indexer.list_documents()
            self._documents = [self._create_doc_info(d) for d in docs]
            return self._documents
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error listing documents: {e}")
            return []

    def get_document(self, identifier: str) -> dict | None:
        """
        Get detailed document information.

        Args:
            identifier: Document ID or filename

        Returns:
            Document details dict
        """
        try:
            return self.indexer.get_document(identifier)
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error: {e}")
            return None

    def delete_document(self, identifier: str) -> bool:
        """
        Delete a document.

        Args:
            identifier: Document ID or filename

        Returns:
            True if successful
        """
        try:
            # Try by filename first
            try:
                count = self.indexer.delete_document_by_filename(identifier)
            except ValueError:
                # Fall back to ID
                self.indexer.delete_document(identifier)

            if self.on_document_deleted:
                self.on_document_deleted(identifier)

            return True
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error deleting: {e}")
            return False

    def _get_document_info(self, doc_id: str) -> DocumentInfo | None:
        """Get document info from ID."""
        try:
            doc = self.indexer.get_document(doc_id)
            return self._create_doc_info(doc)
        except Exception:
            return None

    def _create_doc_info(self, doc: dict) -> DocumentInfo:
        """Create DocumentInfo from document dict."""
        return DocumentInfo(
            id=doc.get("id", ""),
            file_name=doc.get("filename", "Unknown"),
            indexed_at=doc.get("indexed_at", ""),
            total_chunks=doc.get("total_chunks", 0),
            source=doc.get("metadata", {}).get("source", ""),
        )

    def format_document_list(self) -> str:
        """
        Format document list for display.

        Returns:
            Formatted string
        """
        docs = self.list_documents()

        if not docs:
            return "No documents indexed yet."

        lines = []
        for i, doc in enumerate(docs, 1):
            lines.append(f"{i}. {doc.file_name} ({doc.total_chunks} chunks)")
            lines.append(f"   ID: {doc.id[:20]}...")
            lines.append(f"   Indexed: {doc.indexed_at}")
            lines.append("")

        return "\n".join(lines)


# Export
__all__ = [
    "DocumentInfo",
    "DocumentManagerUI",
]
