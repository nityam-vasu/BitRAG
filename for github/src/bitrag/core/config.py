"""
BitRAG Configuration Module

Manages configuration for BitRAG including:
- Directory paths
- Model settings
- Indexing parameters
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


# Get project root (go up from src/bitrag/core to project root)
# File: Test_Project/src/bitrag/core/config.py
# Going up 4 levels: core -> bitrag -> src -> Test_Project
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class Config:
    """BitRAG Configuration"""

    # Directory paths
    data_dir: str = str(PROJECT_ROOT / "data")
    chroma_dir: str = str(PROJECT_ROOT / "chroma_db")
    sessions_dir: str = str(PROJECT_ROOT / "sessions")

    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM settings
    default_model: str = "llama3.2:1b"  # Available in Ollama
    llm_type: str = "ollama"  # "bitnet" or "ollama"
    ollama_base_url: str = "http://localhost:11434"

    # Indexing settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 3

    # Collection name for ChromaDB
    collection_name: str = "bitrag_documents"

    def __post_init__(self):
        """Ensure directories exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.chroma_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)

    def get_session_dir(self, session_id: str) -> Path:
        """Get session directory path"""
        return Path(self.sessions_dir) / session_id

    def get_session_uploads_dir(self, session_id: str) -> Path:
        """Get session uploads directory"""
        return self.get_session_dir(session_id) / "uploads"

    def get_session_chroma_dir(self, session_id: str) -> Path:
        """Get session ChromaDB directory"""
        return self.get_session_dir(session_id) / "chroma_db"

    def get_session_index_dir(self, session_id: str) -> Path:
        """Get session index directory"""
        return self.get_session_dir(session_id) / "index"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    def save(self, path: str = None):
        """Save config to JSON file"""
        if path is None:
            path = PROJECT_ROOT / ".bitrag_config.json"

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str = None) -> "Config":
        """Load config from JSON file"""
        if path is None:
            path = PROJECT_ROOT / ".bitrag_config.json"

        if not os.path.exists(path):
            return cls()

        with open(path, "r") as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""
        return cls(
            data_dir=os.getenv("DATA_DIR", str(PROJECT_ROOT / "data")),
            chroma_dir=os.getenv("CHROMA_DIR", str(PROJECT_ROOT / "chroma_db")),
            sessions_dir=os.getenv("SESSIONS_DIR", str(PROJECT_ROOT / "sessions")),
            default_model=os.getenv("DEFAULT_LLM_MODEL", "llama3.2:1b"),
            llm_type=os.getenv("LLM_TYPE", "ollama"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config):
    """Set global config instance"""
    global _config
    _config = config
