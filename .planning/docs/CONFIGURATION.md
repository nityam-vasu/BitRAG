# BitRAG Configuration Documentation

**Document:** CONFIGURATION.md
**Version:** 1.0
**Date:** 2026-04-02

---

## Overview

BitRAG uses a `Config` dataclass to manage all configuration settings. This document catalogs all configurable options.

---

## Configuration Sources

Configuration can be loaded from:

1. **Defaults** - Hardcoded values in `Config` class
2. **Environment Variables** - Using `Config.from_env()`
3. **JSON File** - Using `Config.save()` / `Config.load()`
4. **Runtime** - Modified via API endpoints

---

## Config Dataclass Fields

### Directory Paths

| Field | Default | Env Var | Description |
|-------|---------|---------|-------------|
| `data_dir` | `{PROJECT_ROOT}/data` | `DATA_DIR` | General data storage |
| `chroma_dir` | `{PROJECT_ROOT}/chroma_db` | `CHROMA_DIR` | ChromaDB storage |
| `sessions_dir` | `{PROJECT_ROOT}/sessions` | `SESSIONS_DIR` | Session storage |

### Embedding Settings

| Field | Default | Env Var | Description |
|-------|---------|---------|-------------|
| `embedding_model` | `sentence-transformers/all-MiniLM-L6-v2` | `EMBEDDING_MODEL` | HuggingFace model for embeddings |

**Model Info:**
- Dimensions: 384
- Size: ~90MB
- Speed: Fast
- Quality: Good balance of speed/quality

### LLM Settings

| Field | Default | Env Var | Description |
|-------|---------|---------|-------------|
| `default_model` | `llama3.2:1b` | `DEFAULT_LLM_MODEL` | Default Ollama model |
| `llm_type` | `ollama` | `LLM_TYPE` | LLM type (`ollama` or `bitnet`) |
| `ollama_base_url` | `http://localhost:11434` | `OLLAMA_BASE_URL` | Ollama server URL |

### Indexing Settings

| Field | Default | Env Var | Description |
|-------|---------|---------|-------------|
| `chunk_size` | `512` | `CHUNK_SIZE` | Text chunk size (tokens) |
| `chunk_overlap` | `50` | `CHUNK_OVERLAP` | Overlap between chunks |
| `top_k` | `3` | `TOP_K` | Number of results to retrieve |

### Storage Settings

| Field | Default | Description |
|-------|---------|-------------|
| `collection_name` | `bitrag_documents` | ChromaDB collection name prefix |

---

## Runtime Settings (web_app.py)

These settings are managed at runtime and NOT persisted in Config:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `current_model` | str | `"llama3.2:1b"` | Active LLM model |
| `ollama_port` | int | `11434` | Ollama port (hardcoded in URL) |
| `hybrid_mode` | bool | `False` | Enable hybrid search |
| `dual_mode` | bool | `False` | Enable dual model mode |
| `dual_model1` | str | `"llama3.2:1b"` | First model for dual mode |
| `dual_model2` | str | `"llama3.2:1b"` | Second model for dual mode |
| `session_id` | str | `"default"` | Current session ID |

---

## API Settings

### GET /api/settings Response

```json
{
  "model": "llama3.2:1b",
  "ollamaPort": 11434,
  "hybridMode": false,
  "dualMode": false,
  "model1": "llama3.2:1b",
  "model2": "llama3.2:1b",
  "documentCount": 5,
  "ollamaStatus": "running"
}
```

### POST /api/settings Request

```json
{
  "model": "qwen2.5:3b",
  "ollamaPort": 11434,
  "hybridMode": true,
  "dualMode": false,
  "model1": "llama3.2:1b",
  "model2": "qwen2.5:3b"
}
```

---

## Environment Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `DATA_DIR` | `/custom/data` | Override data directory |
| `CHROMA_DIR` | `/custom/chroma` | Override ChromaDB directory |
| `SESSIONS_DIR` | `/custom/sessions` | Override sessions directory |
| `DEFAULT_LLM_MODEL` | `qwen2.5:3b` | Override default model |
| `LLM_TYPE` | `ollama` | LLM type (ollama/bitnet) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL |
| `EMBEDDING_MODEL` | `BAAI/bge-small` | Override embedding model |

---

## Session Directory Structure

Each session has its own isolated storage:

```
sessions/{session_id}/
├── uploads/              # Uploaded files
│   ├── doc1.pdf
│   └── doc2.txt
├── chroma_db/           # Session-specific ChromaDB
│   ├── ...
├── index/               # LlamaIndex storage (if used)
│   └── ...
└── session.json          # Chat history (TUI)
```

---

## ChromaDB Collection Naming

Collections are named using the pattern:

```
{collection_name}_{session_id}
```

Example: `bitrag_documents_default`

This ensures session isolation in shared ChromaDB directories.

---

## Configuration Validation

### Ollama Model Validation

When setting `current_model`:
1. Check if Ollama is reachable
2. Verify model exists (via `ollama list`)
3. If invalid, keep previous model and return error

### Directory Creation

On `Config` initialization:
```python
def __post_init__(self):
    os.makedirs(self.data_dir, exist_ok=True)
    os.makedirs(self.chroma_dir, exist_ok=True)
    os.makedirs(self.sessions_dir, exist_ok=True)
```

---

## Recommended Settings

### Fast/Testing
```python
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
default_model = "llama3.2:1b"
chunk_size = 256
top_k = 2
```

### Balanced
```python
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
default_model = "qwen2.5:3b"
chunk_size = 512
top_k = 3
```

### High Quality
```python
embedding_model = "BAAI/bge-base-en-v1.5"
default_model = "llama3.2:3b"
chunk_size = 1024
top_k = 5
```

---

## Configuration File (.bitrag_config.json)

Save/load configuration to JSON:

```bash
# In Python
config = get_config()
config.model = "qwen2.5:3b"
config.save()  # Saves to .bitrag_config.json

# Load on restart
config = Config.load()  # Loads from .bitrag_config.json
```

---

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Storage | 1GB | 10GB+ |
| CPU | 2 cores | 4+ cores |
| GPU | Optional | 4GB+ VRAM |

---

## Key Configuration Notes

1. **Session Isolation**: Each session has its own ChromaDB collection
2. **Model Switching**: Changes take effect on next query
3. **Ollama Connection**: Uses `127.0.0.1` (not `localhost`) to avoid IPv6
4. **Chunking**: SentenceSplitter handles sentence boundaries
5. **Embeddings**: Loaded once, cached in memory
