# BitRAG Component Inventory

**Document:** COMPONENT_INVENTORY.md
**Version:** 1.0
**Date:** 2026-04-02

---

## Overview

This document catalogs all components in the BitRAG codebase with their purposes, dependencies, and relationships.

---

## Directory Structure

```
BitRAG/
├── web_app.py                    # Flask backend (main entry)
├── src/bitrag/
│   ├── __init__.py
│   ├── core/                     # Core RAG functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── indexer.py           # Document indexing
│   │   ├── query.py              # Query engine
│   │   └── hybrid_search.py      # Hybrid search (optional)
│   ├── cli/                      # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tui/                      # Terminal UI
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── app.py
│   │   ├── chat.py              # Chat session management
│   │   ├── chat_display.py
│   │   ├── document_manager.py
│   │   ├── documents.py
│   │   ├── settings.py
│   │   ├── terminal.py
│   │   ├── tui.py
│   │   └── widgets.py
│   └── utils/
│       └── __init__.py
├── frontend/                     # Pre-built React frontend
│   ├── index.html
│   └── assets/                   # Bundled JS/CSS
│       ├── index-C7WuB4gw.js
│       └── index-GYeDh-gI.css
└── sessions/                     # Session data (runtime)
```

---

## Backend Components

### web_app.py (1008 lines)

**Purpose:** Main Flask application entry point

**Responsibilities:**
- HTTP server setup
- API endpoint routing
- Component initialization
- Session management

**Key Classes/Functions:**
- `initialize_components()` - Lazy initialization of indexer/query engine
- `ensure_initialized()` - Thread-safe initialization check
- `extract_thinking()` - Parse reasoning model output
- `generate_thinking_steps()` - Generate thinking display text

**Endpoints (15 total):**
| Endpoint | Method | Handler |
|----------|--------|---------|
| `/` | GET | `index()` |
| `/debug` | GET | `debug()` |
| `/graph`, `/settings`, `/documents` | GET | `serve_static()` |
| `/api/status` | GET | `api_status()` |
| `/api/chat` | POST | `chat()` |
| `/api/chat/stream` | POST | `chat_stream()` |
| `/api/documents` | GET, POST | `get_documents()`, `upload_document()` |
| `/api/documents/<id>` | DELETE | `delete_document()` |
| `/api/models` | GET | `get_models()` |
| `/api/models/download` | POST | `download_model()` |
| `/api/models/delete` | POST | `delete_model()` |
| `/api/settings` | GET, POST | `get_settings()`, `update_settings()` |
| `/api/system/info` | GET | `get_system_info()` |
| `/api/graph` | GET | `get_graph_data()` |

**Global State:**
```python
init_lock = threading.Lock()
initialized = False
initializing = False
indexer = None
query_engine = None
current_model = "llama3.2:1b"
session_id = "default"
```

**Dependencies:**
- flask
- requests
- psutil
- src.bitrag.core modules

---

## Core Modules

### src/bitrag/core/config.py (124 lines)

**Purpose:** Configuration management

**Key Class:** `Config` (dataclass)

**Configuration Fields:**
```python
data_dir: str = ".../data"
chroma_dir: str = ".../chroma_db"
sessions_dir: str = ".../sessions"
embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
default_model: str = "llama3.2:1b"
llm_type: str = "ollama"
ollama_base_url: str = "http://localhost:11434"
chunk_size: int = 512
chunk_overlap: int = 50
top_k: int = 3
collection_name: str = "bitrag_documents"
```

**Methods:**
- `get_session_dir(session_id)` - Get session directory
- `get_session_uploads_dir(session_id)` - Get uploads directory
- `get_session_chroma_dir(session_id)` - Get ChromaDB directory
- `save()` / `load()` - Persist config to JSON
- `from_env()` - Load from environment variables

**Used By:** All core modules

---

### src/bitrag/core/indexer.py (387 lines)

**Purpose:** Document indexing and storage

**Key Class:** `DocumentIndexer`

**Responsibilities:**
- PDF text extraction (using pypdf)
- Text chunking (using SentenceSplitter)
- Embedding generation (HuggingFace)
- ChromaDB storage
- Document CRUD operations

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `index_document(file_path)` | Index a PDF, return doc_id |
| `list_documents()` | Get all indexed documents |
| `get_document(filename)` | Get document with all chunks |
| `delete_document_by_filename(fn)` | Delete document by filename |
| `search(query, top_k)` | Vector similarity search |
| `update_document_metadata(fn, meta)` | Update document metadata |

**ChromaDB Schema:**
```
Collection: bitrag_documents_{session_id}
├── ids: Document/chunk IDs
├── embeddings: 384-dim vectors
├── documents: Text content
└── metadatas: {file_name, file_path, indexed_at, session_id}
```

**Dependencies:**
- llama_index.core
- llama_index.vector_stores.chroma
- llama_index.embeddings.huggingface
- pypdf
- chromadb

**Used By:** web_app.py

---

### src/bitrag/core/query.py (547 lines)

**Purpose:** RAG query processing

**Key Classes:**
- `OllamaService` - Ollama connection management
- `QueryEngine` - RAG query engine

**QueryEngine Methods:**
| Method | Purpose |
|--------|---------|
| `query(question)` | Single-shot query |
| `query_streaming(question)` | Streaming query (Generator) |
| `get_retrieved_context(question)` | Get context without response |
| `set_model(model_name)` | Switch LLM model |
| `get_ollama_status()` | Check Ollama connection |

**Streaming Response Format:**
```python
{"type": "sources", "sources": [...]}  # First yield
{"type": "chunk", "text": "..."}      # Token chunks
{"type": "done", "response": "..."}  # Final response
{"type": "error", "message": "..."}   # Error
```

**Dependencies:**
- llama_index.llms.ollama
- llama_index.core
- llama_index.embeddings.huggingface

**Used By:** web_app.py

---

### src/bitrag/core/hybrid_search.py (301 lines)

**Purpose:** Hybrid search combining vector + BM25

**Key Class:** `HybridSearch`

**Methods:**
| Method | Purpose |
|--------|---------|
| `vector_search(query, k)` | ChromaDB similarity search |
| `keyword_search(query, k)` | BM25 keyword search |
| `hybrid_search(query, k, alpha)` | Combined with RRF |
| `_reciprocal_rank_fusion()` | Score fusion algorithm |

**RRF Formula:**
```
score(doc) = α × (1/(k+rank_vector)) + (1-α) × (1/(k+rank_bm25))
k = 60 (constant)
α = 0.5 (default, configurable)
```

**Dependencies:**
- rank_bm25
- llama_index.core

**Used By:** TUI (optional feature)

---

## TUI Components

### src/bitrag/tui/chat.py (330 lines)

**Purpose:** Chat session management (TUI)

**Key Classes:**
- `ChatMessageData` - Serializable message
- `ChatSessionData` - Serializable session
- `ChatSession` - Single session manager
- `SessionManager` - Multiple sessions manager

**Session Storage:**
```
sessions/{session_id}/
└── session.json
```

**Session JSON Schema:**
```json
{
  "session_id": "default",
  "title": "Chat Title",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:22:00Z",
  "messages": [
    {
      "content": "Message text",
      "role": "user|assistant|system",
      "timestamp": "ISO timestamp",
      "sources": ["file.pdf"]
    }
  ]
}
```

**Dependencies:** None (uses standard library)

---

## Frontend Components

### frontend/index.html (14 lines)

**Purpose:** Single-page application entry

**Structure:**
- Loads bundled React app
- Uses force-graph for visualization
- Single `div#root` container

**Note:** Frontend source code NOT in repository (pre-built only)

---

## Component Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        web_app.py                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐    │
│  │ /api/chat   │  │ /api/documents│  │ /api/graph          │    │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘    │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│  QueryEngine    │ │ DocumentIndexer│ │  GraphBuilder   │
│  (query.py)     │ │ (indexer.py)   │ │  (inline)      │
└────────┬────────┘ └───────┬───────┘ └─────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────┐ ┌───────────────┐
│ OllamaService   │ │ ChromaDB      │
│ (query.py)      │ │ VectorStore   │
└─────────────────┘ └───────────────┘
         │
         ▼
┌─────────────────┐
│ Ollama Server   │
│ (localhost:11434)│
└─────────────────┘
```

---

## File Summary Table

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| web_app.py | 1008 | Backend | Flask API server |
| config.py | 124 | Core | Configuration |
| indexer.py | 387 | Core | Document indexing |
| query.py | 547 | Core | Query engine |
| hybrid_search.py | 301 | Core | Optional search |
| chat.py (TUI) | 330 | TUI | Session management |
| frontend/* | - | Frontend | Pre-built, bundled |

---

## Integration Points

### Where to Modify for Phase 2 (Graph)

1. **web_app.py** - `get_graph_data()` endpoint (lines 784-988)
   - Add summary generation
   - Add tag extraction
   - Update node structure
   - Enhance link calculation

2. **src/bitrag/core/indexer.py** - `DocumentIndexer`
   - Add `update_document_metadata()` for storing summaries/tags

### Where to Modify for Phase 3 (Model Selection)

1. **src/bitrag/core/config.py** - Add `summary_model`, `tag_model`
2. **web_app.py** - Update settings endpoint (lines 585-692)
3. **src/bitrag/core/query.py** - Pass model to generators

### Where to Modify for Phase 4 (Sessions)

1. **src/bitrag/tui/chat.py** - SessionManager already exists
2. **web_app.py** - Add session endpoints
3. **Add:** `src/bitrag/core/session_exporter.py`

---

## Quick Reference

**Need to change X? Find it here:**

| What to Change | Where |
|----------------|-------|
| API endpoints | web_app.py |
| Document storage | indexer.py |
| Query processing | query.py |
| Configuration | config.py |
| Chat sessions | chat.py (TUI) |
| Frontend UI | Need to rebuild frontend |
| Graph visualization | frontend/assets/index-*.js |
