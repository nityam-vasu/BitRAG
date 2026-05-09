"""
Tests for BitRAG configuration module.
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


class TestConfig:
    """Test cases for Config class."""

    def test_config_default_values(self):
        """Test that default config values are set correctly."""
        from bitrag.core.config import Config

        config = Config()

        assert config.data_dir is not None
        assert config.chroma_dir is not None
        assert config.sessions_dir is not None
        assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.default_model == "llama3.2:1b"
        assert config.ollama_base_url == "http://localhost:11434"
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.top_k == 3

    def test_config_custom_values(self, temp_dir):
        """Test creating config with custom values."""
        from bitrag.core.config import Config

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            default_model="custom-model:1b",
        )

        assert config.data_dir == os.path.join(temp_dir, "data")
        assert config.chroma_dir == os.path.join(temp_dir, "chroma_db")
        assert config.default_model == "custom-model:1b"

    def test_config_directories_created(self, temp_dir):
        """Test that required directories are created."""
        from bitrag.core.config import Config

        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
        )

        assert os.path.exists(config.data_dir)
        assert os.path.exists(config.chroma_dir)
        assert os.path.exists(config.sessions_dir)

    def test_session_directories(self, temp_dir):
        """Test session directory methods."""
        from bitrag.core.config import Config

        config = Config(
            sessions_dir=os.path.join(temp_dir, "sessions"),
        )

        session_dir = config.get_session_dir("test_session")
        assert str(session_dir) == os.path.join(temp_dir, "sessions", "test_session")

        uploads_dir = config.get_session_uploads_dir("test_session")
        assert str(uploads_dir) == os.path.join(temp_dir, "sessions", "test_session", "uploads")

        chroma_dir = config.get_session_chroma_dir("test_session")
        assert str(chroma_dir) == os.path.join(temp_dir, "sessions", "test_session", "chroma_db")

    def test_config_to_dict(self):
        """Test config serialization to dictionary."""
        from bitrag.core.config import Config

        config = Config()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "data_dir" in config_dict
        assert "chroma_dir" in config_dict
        assert "default_model" in config_dict

    def test_get_config_singleton(self):
        """Test that get_config returns a singleton."""
        from bitrag.core.config import get_config, set_config, Config

        # Create a new config
        new_config = Config()
        set_config(new_config)

        # get_config should return the same instance
        retrieved_config = get_config()
        assert retrieved_config is new_config
