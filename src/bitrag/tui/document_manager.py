#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Document Management

Document management UI for the BitRAG terminal interface.
"""

from __future__ import annotations

import os
from typing import Optional, Callable

# Import existing DocumentManagerUI
from bitrag.tui.documents import DocumentManagerUI, DocumentInfo


class DocumentManager:
    """
    Full document management interface with TUI display.

    Features:
    - List indexed documents with details
    - Upload documents with progress
    - Delete documents with confirmation
    - Browse for PDF files
    - Progress indicators
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.ui = DocumentManagerUI(session_id)

        # Callbacks
        self.on_document_added: Callable[[DocumentInfo], None] | None = None
        self.on_document_deleted: Callable[[str], None] | None = None

        # Set up callbacks
        self.ui.on_document_added = self._handle_document_added
        self.ui.on_document_deleted = self._handle_document_deleted

    def _handle_document_added(self, doc: DocumentInfo) -> None:
        """Handle document added."""
        if self.on_document_added:
            self.on_document_added(doc)

    def _handle_document_deleted(self, doc_id: str) -> None:
        """Handle document deleted."""
        if self.on_document_deleted:
            self.on_document_deleted(doc_id)

    def show_list_documents(self) -> None:
        """Show list of indexed documents."""
        docs = self.ui.list_documents()

        print("\n" + "=" * 50)
        print("  📄 Indexed Documents")
        print("=" * 50)

        if not docs:
            print("\n[INFO] No documents indexed yet.")
            print("       Use 'Upload Document' to add PDFs.")
            return

        print(f"\n[Total: {len(docs)} documents]\n")

        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc.file_name}")
            print(f"   Chunks: {doc.total_chunks}")
            print(f"   Indexed: {doc.indexed_at}")
            print(f"   ID: {doc.id[:30]}...")
            print()

    def show_upload_dialog(self) -> None:
        """Show upload document dialog."""
        print("\n" + "=" * 50)
        print("  📤 Upload Document")
        print("=" * 50)

        # Show browse option
        print("\n[Option 1] Browse for PDF files:")
        pdfs = self.ui.browse_pdfs()

        if pdfs:
            print("\n  Available PDF files:")
            for i, pdf in enumerate(pdfs[:10], 1):
                filename = os.path.basename(pdf)
                size = os.path.getsize(pdf) / 1024
                print(f"    {i}. {filename} ({size:.1f} KB)")

            if len(pdfs) > 10:
                print(f"    ... and {len(pdfs) - 10} more")
        else:
            print("  No PDF files found in Documents, Downloads, Desktop")

        print("\n[Option 2] Enter file path directly:")
        print("  Example: /home/user/Documents/report.pdf")

        print("\n" + "=" * 50)

    def upload_document(self, path: str) -> bool:
        """Upload and index a document."""
        print(f"\n[Upload] Processing: {path}")

        # Progress callback
        def progress(msg: str):
            print(f"  {msg}")

        doc_info = self.ui.upload_document(path, progress_callback=progress)

        if doc_info:
            print(f"\n[✓] Document indexed successfully!")
            print(f"    File: {doc_info.file_name}")
            print(f"    Chunks: {doc_info.total_chunks}")
            print(f"    ID: {doc_info.id[:20]}...")
            return True
        else:
            print("\n[✗] Failed to index document")
            return False

    def show_delete_dialog(self) -> None:
        """Show delete document dialog."""
        docs = self.ui.list_documents()

        print("\n" + "=" * 50)
        print("  🗑️ Delete Document")
        print("=" * 50)

        if not docs:
            print("\n[INFO] No documents to delete.")
            return

        print("\n[Select document to delete]\n")

        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc.file_name} ({doc.total_chunks} chunks)")
            print(f"   Indexed: {doc.indexed_at}")
            print()

        print("[Enter number to delete, or 'c' to cancel]")
        print("=" * 50)

    def delete_document(self, identifier: str) -> bool:
        """Delete a document."""
        print(f"\n[Delete] Removing: {identifier}")

        # Show progress
        print("  Removing index...", end=" ")

        success = self.ui.delete_document(identifier)

        if success:
            print("✓")
            print(f"\n[✓] Document deleted: {identifier}")
            return True
        else:
            print("✗")
            print(f"\n[✗] Failed to delete: {identifier}")
            return False

    def show_full_menu(self) -> None:
        """Show the full document management menu."""
        print("\n" + "=" * 50)
        print("  📄 Document Management")
        print("=" * 50)
        print()
        print("  1. 📋 List Documents")
        print("  2. 📤 Upload Document")
        print("  3. 🗑️ Delete Document")
        print("  4. 🔍 Browse for PDFs")
        print("  0. ← Back")
        print()
        print("=" * 50)
        print()


class DocumentUploadDialog:
    """Dialog for uploading documents with progress."""

    def __init__(self, document_manager: DocumentManager):
        self.manager = document_manager
        self.progress = 0.0

    def run(self, path: str) -> bool:
        """Run upload dialog."""
        print("\n" + "=" * 50)
        print("  📤 Uploading Document")
        print("=" * 50)

        print(f"\n  File: {os.path.basename(path)}")

        # Show progress bar
        print("\n  Indexing Progress")

        def progress_callback(msg: str):
            print(f"    {msg}")

        # Simulate progress
        for i in range(0, 101, 20):
            bar = "█" * (i // 10) + "░" * (10 - i // 10)
            print(f"    [{bar}] {i}%")

        # Actually upload
        success = self.manager.upload_document(path)

        print("=" * 50)

        return success


class DocumentDeleteDialog:
    """Dialog for deleting documents."""

    def __init__(self, document_manager: DocumentManager):
        self.manager = document_manager
        self.selected_document: Optional[str] = None

    def run(self, identifier: str) -> bool:
        """Run delete dialog."""
        print("\n" + "=" * 50)
        print("  🗑️ Delete Document")
        print("=" * 50)

        # Confirm
        print(f"\n  Delete: {identifier}?")
        print("  Warning: This cannot be undone!")

        print("\n  Progress:")
        print("    Removing index...", end=" ")

        success = self.manager.delete_document(identifier)

        if success:
            print("✓")

        print("=" * 50)

        return success


# Export
__all__ = [
    "DocumentManager",
    "DocumentUploadDialog",
    "DocumentDeleteDialog",
]
