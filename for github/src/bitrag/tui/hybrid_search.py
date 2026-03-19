#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Hybrid Search Integration

TUI-specific wrapper for hybrid search and query functionality.
"""

from __future__ import annotations

import os
import threading
from typing import Callable, Optional


# Lazy imports
def _get_hybrid_search():
    """Lazy import of HybridSearch."""
    from bitrag.core.hybrid_search import HybridSearch

    return HybridSearch


def _get_config():
    """Lazy import of get_config."""
    from bitrag.core.config import get_config

    return get_config


class TUIQueryEngine:
    """
    TUI-specific query engine wrapper.

    Provides:
    - Async-friendly interface for UI
    - Streaming response handling
    - Loading state management
    - Source citation extraction
    """

    def __init__(
        self,
        session_id: str = "default",
        model: str | None = None,
        alpha: float = 0.5,
    ):
        self.session_id = session_id
        self.model = model
        self.alpha = alpha

        # Lazy-loaded components
        self._config = None
        self._hybrid_search = None
        self._query_engine = None

        # State
        self._is_loading = False
        self._current_query = ""

    @property
    def config(self):
        """Lazy load config."""
        if self._config is None:
            self._config = _get_config()
        return self._config

    @property
    def model(self) -> str:
        """Get the model name."""
        return self._model or self.config.default_model

    @model.setter
    def model(self, value: str | None):
        """Set the model name."""
        self._model = value

    @property
    def hybrid_search(self):
        """Lazy load hybrid search."""
        if self._hybrid_search is None:
            try:
                HS = _get_hybrid_search()
                self._hybrid_search = HS(
                    session_id=self.session_id,
                    chroma_dir=self.config.chroma_dir,
                    embedding_model=self.config.embedding_model,
                    alpha=self.alpha,
                )
            except Exception as e:
                print(f"Warning: Could not initialize hybrid search: {e}")
                self._hybrid_search = None
        return self._hybrid_search

    @property
    def is_loading(self) -> bool:
        """Check if a query is in progress."""
        return self._is_loading

    def has_documents(self) -> bool:
        """Check if there are indexed documents."""
        try:
            if self.hybrid_search and self.hybrid_search.collection:
                return self.hybrid_search.collection.count() > 0
        except Exception:
            pass
        return False

    def query(
        self,
        question: str,
        callback: Callable[[str], None] | None = None,
        streaming: bool = True,
    ) -> dict:
        """
        Execute a query and return results.

        Args:
            question: The question to ask
            callback: Optional callback for streaming responses
            streaming: Whether to use streaming (if supported)

        Returns:
            dict with response, sources, model
        """
        self._is_loading = True
        self._current_query = question

        try:
            # Get relevant documents using hybrid search
            if self.hybrid_search is None:
                return {
                    "response": "Error: Hybrid search not initialized",
                    "sources": [],
                    "model": self.model,
                }

            # Perform hybrid search
            sources = self.hybrid_search.hybrid_search(question, k=5, alpha=self.alpha)

            # Build context from sources
            context = "\n\n".join(
                [f"Source {i + 1}:\n{source['text']}" for i, source in enumerate(sources)]
            )

            # Generate response using Ollama
            response = self._generate_response(question, context, callback)

            return {
                "response": response,
                "sources": sources,
                "model": self.model,
            }

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "sources": [],
                "model": self.model,
            }
        finally:
            self._is_loading = False

    def query_async(
        self,
        question: str,
        on_chunk: Callable[[str], None] | None = None,
        on_complete: Callable[[dict], None] | None = None,
    ) -> None:
        """
        Execute query in background thread.

        Args:
            question: The question to ask
            on_chunk: Callback for streaming chunks
            on_complete: Callback when complete with full result
        """

        def run_query():
            result = self.query(question, callback=on_chunk)
            if on_complete:
                on_complete(result)

        thread = threading.Thread(target=run_query, daemon=True)
        thread.start()

    def _generate_response(
        self,
        question: str,
        context: str,
        callback: Callable[[str], None] | None = None,
    ) -> str:
        """Generate response using Ollama."""
        import subprocess
        import json

        # Build prompt
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""

        try:
            # Call Ollama
            result = subprocess.run(
                [
                    "ollama",
                    "run",
                    self.model,
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return f"Error: {result.stderr}"

            response = result.stdout.strip()

            # If callback provided, simulate streaming
            if callback:
                # Stream word by word
                words = response.split()
                for i, word in enumerate(words):
                    callback(word + (" " if i < len(words) - 1 else ""))

            return response

        except subprocess.TimeoutExpired:
            return "Error: Request timed out"
        except FileNotFoundError:
            return "Error: Ollama not found. Is it installed?"
        except Exception as e:
            return f"Error: {str(e)}"

    def set_alpha(self, alpha: float) -> None:
        """Set the hybrid search alpha parameter."""
        self.alpha = max(0.0, min(1.0, alpha))
        # Reset hybrid search to apply new alpha
        self._hybrid_search = None

    def get_sources_text(self, sources: list) -> list:
        """Extract just the text from sources for display."""
        return [
            {
                "text": s.get("text", "")[:200] + "..."
                if len(s.get("text", "")) > 200
                else s.get("text", ""),
                "score": s.get("score", 0),
                "rank": s.get("rank", 0),
            }
            for s in sources
        ]


class DocumentManager:
    """
    TUI-specific document management wrapper.

    Provides:
    - Document upload with progress
    - Document listing
    - Document deletion
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self._indexer = None

    @property
    def indexer(self):
        """Lazy load indexer."""
        if self._indexer is None:
            from bitrag.core.indexer import DocumentIndexer

            self._indexer = DocumentIndexer(self.session_id)
        return self._indexer

    def upload_document(
        self,
        path: str,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict:
        """
        Upload and index a document.

        Args:
            path: Path to the document
            progress_callback: Optional callback for progress updates

        Returns:
            dict with success status and message
        """
        try:
            if progress_callback:
                progress_callback("Loading document...")

            if not os.path.exists(path):
                return {"success": False, "error": f"File not found: {path}"}

            if progress_callback:
                progress_callback("Indexing document...")

            # Index the document
            doc_id = self.indexer.index_document(path, metadata={"source": "tui"})

            if progress_callback:
                progress_callback("Done!")

            return {
                "success": True,
                "doc_id": doc_id,
                "message": f"Indexed: {os.path.basename(path)}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_documents(self) -> list:
        """List all indexed documents."""
        try:
            return self.indexer.list_documents()
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

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
                return True
            except ValueError:
                # Fall back to ID
                self.indexer.delete_document(identifier)
                return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False


# Export
__all__ = [
    "TUIQueryEngine",
    "DocumentManager",
]
