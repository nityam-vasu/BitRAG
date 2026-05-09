"""
Tests for BitRAG query engine.
"""

import os
import sys

# Add src to path - this must be FIRST to avoid bitrag.py conflict
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_SRC_PATH = os.path.join(_PROJECT_ROOT, 'src')
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

import pytest
from pathlib import Path


class TestOllamaService:
    """Test cases for OllamaService class."""

    def test_ollama_service_initialization(self):
        """Test OllamaService initialization."""
        from bitrag.core.query import OllamaService

        service = OllamaService()
        assert service.base_url == "http://localhost:11434"
        assert service._available_models is None

    def test_ollama_service_custom_url(self):
        """Test OllamaService with custom URL."""
        from bitrag.core.query import OllamaService

        service = OllamaService(base_url="http://custom:9999")
        assert service.base_url == "http://custom:9999"

    def test_ollama_service_is_available(self):
        """Test Ollama availability check."""
        from bitrag.core.query import OllamaService

        service = OllamaService()
        # This will depend on whether Ollama is running
        result = service.is_available()
        assert isinstance(result, bool)

    def test_ollama_service_list_models(self):
        """Test listing models."""
        from bitrag.core.query import OllamaService

        service = OllamaService()
        models = service.list_models()
        assert isinstance(models, list)

    def test_ollama_service_model_exists(self):
        """Test checking if model exists."""
        from bitrag.core.query import OllamaService

        service = OllamaService()
        # Test with a known model
        exists = service.model_exists("llama3.2:1b")
        assert isinstance(exists, bool)

    def test_ollama_service_invalidate_cache(self):
        """Test cache invalidation."""
        from bitrag.core.query import OllamaService

        service = OllamaService()
        service._available_models = ["cached_model"]
        service.invalidate_cache()
        assert service._available_models is None


class TestQueryEngine:
    """Test cases for QueryEngine class."""

    @pytest.fixture
    def query_engine(self, temp_dir, test_session_id):
        """Create a QueryEngine instance for testing."""
        from bitrag.core.config import Config
        from bitrag.core.query import QueryEngine

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
        )

        # Skip Ollama check for testing
        return QueryEngine(session_id=test_session_id, _skip_ollama_check=True)

    def test_query_engine_initialization(self, query_engine):
        """Test that QueryEngine initializes correctly."""
        assert query_engine is not None
        assert query_engine.session_id == "test_session"

    def test_query_engine_get_current_model(self, query_engine):
        """Test getting current model info."""
        model_info = query_engine.get_current_model()
        assert isinstance(model_info, dict)
        assert "model" in model_info
        assert "llm_type" in model_info

    def test_query_engine_has_documents_empty(self, query_engine):
        """Test has_documents returns False for empty index."""
        assert query_engine.has_documents() is False

    def test_query_engine_get_document_count(self, query_engine):
        """Test getting document count."""
        count = query_engine.get_document_count()
        assert count == 0

    def test_query_engine_get_retrieved_context(self, query_engine):
        """Test retrieving context for a query."""
        context = query_engine.get_retrieved_context("test query")
        assert isinstance(context, list)
        # Empty list for empty index

    def test_query_engine_query_no_documents(self, query_engine):
        """Test query returns message when no documents."""
        result = query_engine.query("test question")
        assert isinstance(result, dict)
        assert "question" in result
        assert "response" in result
        assert "No documents" in result["response"] or "sources" in result


class TestQueryEngineWithModel:
    """Test cases for QueryEngine with specific model settings."""

    def test_query_engine_custom_model(self, temp_dir):
        """Test QueryEngine with custom model."""
        from bitrag.core.config import Config
        from bitrag.core.query import QueryEngine

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            default_model="custom-model:3b",
        )

        engine = QueryEngine(session_id="test", model="custom-model:3b", _skip_ollama_check=True)

        assert engine.model == "custom-model:3b"

    def test_query_engine_llm_type_detection(self, temp_dir):
        """Test LLM type detection from model name."""
        from bitrag.core.query import QueryEngine

        engine = QueryEngine(session_id="test", _skip_ollama_check=True)

        # Test Ollama detection
        engine.model = "llama3.2:1b"
        assert engine._detect_llm_type("llama3.2:1b") == "ollama"

        # Test BitNet detection
        engine.model = "bitnet-b1.58-2B-4T"
        assert engine._detect_llm_type("bitnet-b1.58-2B-4T") == "bitnet"
