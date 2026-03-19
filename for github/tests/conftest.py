"""
Test configuration and fixtures for BitRAG tests.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def test_session_id():
    """Provide a test session ID."""
    return "test_session"


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    from bitrag.core.config import Config

    config = Config(
        data_dir=os.path.join(temp_dir, "data"),
        chroma_dir=os.path.join(temp_dir, "chroma_db"),
        sessions_dir=os.path.join(temp_dir, "sessions"),
    )
    return config


@pytest.fixture
def sample_pdf_path():
    """Provide path to a sample test PDF."""
    # Use the sample PDFs included in the repo
    pdf_path = Path(__file__).parent.parent / "pdfs" / "Test_Story.pdf"
    if pdf_path.exists():
        return str(pdf_path)
    return None


@pytest.fixture
def mock_ollama():
    """Mock Ollama service for testing without actual Ollama."""

    class MockOllamaService:
        def __init__(self):
            self.base_url = "http://localhost:11434"
            self._available_models = ["llama3.2:1b", "qwen2.5:0.5b"]

        def is_available(self):
            return True

        def list_models(self):
            return self._available_models

        def model_exists(self, model_name):
            return model_name in self._available_models

    return MockOllamaService()
