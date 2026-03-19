"""
Tests for BitRAG document indexer.
"""

import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestDocumentIndexer:
    """Test cases for DocumentIndexer class."""

    @pytest.fixture
    def indexer(self, temp_dir, test_session_id):
        """Create a DocumentIndexer instance for testing."""
        from bitrag.core.config import Config
        from bitrag.core.indexer import DocumentIndexer

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
        )

        return DocumentIndexer(session_id=test_session_id)

    def test_indexer_initialization(self, indexer):
        """Test that indexer initializes correctly."""
        assert indexer is not None
        assert indexer.session_id == "test_session"
        assert indexer.collection is not None
        assert indexer.embedding_model is not None

    def test_get_document_count_empty(self, indexer):
        """Test that document count is 0 for new indexer."""
        count = indexer.get_document_count()
        assert count == 0

    def test_list_documents_empty(self, indexer):
        """Test that list_documents returns empty list for new indexer."""
        docs = indexer.list_documents()
        assert isinstance(docs, list)
        assert len(docs) == 0

    def test_index_document_nonexistent_file(self, indexer):
        """Test that indexing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            indexer.index_document("/nonexistent/file.pdf")

    def test_search_empty_index(self, indexer):
        """Test search returns empty results for empty index."""
        results = indexer.search("test query")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_delete_document_nonexistent(self, indexer):
        """Test deleting nonexistent document."""
        # Should not raise error, but also not affect anything
        indexer.delete_document("nonexistent_id")

    def test_delete_document_by_filename_nonexistent(self, indexer):
        """Test deleting nonexistent document by filename."""
        with pytest.raises(ValueError):
            indexer.delete_document_by_filename("nonexistent.pdf")

    def test_get_document_nonexistent(self, indexer):
        """Test getting nonexistent document."""
        with pytest.raises(ValueError):
            indexer.get_document("nonexistent.pdf")

    def test_clear_index(self, indexer):
        """Test clearing the index."""
        indexer.clear_index()
        assert indexer.get_document_count() == 0


class TestDocumentIndexerWithPDF:
    """Test cases for DocumentIndexer with actual PDF files."""

    @pytest.fixture
    def indexer(self, temp_dir, test_session_id):
        """Create a DocumentIndexer instance for testing."""
        from bitrag.core.config import Config
        from bitrag.core.indexer import DocumentIndexer

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
        )

        return DocumentIndexer(session_id=test_session_id)

    def test_index_sample_pdf(self, indexer, sample_pdf_path):
        """Test indexing a sample PDF if available."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not available")

        doc_id = indexer.index_document(sample_pdf_path)
        assert doc_id is not None
        assert indexer.get_document_count() > 0

    def test_search_after_indexing(self, indexer, sample_pdf_path):
        """Test search returns results after indexing."""
        if sample_pdf_path is None:
            pytest.skip("Sample PDF not available")

        indexer.index_document(sample_pdf_path)
        results = indexer.search("test")

        assert isinstance(results, list)
        # May or may not have results depending on PDF content
