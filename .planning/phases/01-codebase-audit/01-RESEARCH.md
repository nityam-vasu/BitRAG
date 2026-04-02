# Phase 1: Codebase Audit - Research

**Researched:** 2026-04-02
**Domain:** Python Flask + React RAG Application
**Confidence:** HIGH

## Summary

BitRAG is a local RAG (Retrieval-Augmented Generation) application with a Flask backend and React frontend. The codebase is well-structured with clear separation between core RAG logic (`src/bitrag/core/`), CLI/TUI interfaces, and web application (`web_app.py`).

**Primary recommendation:** Document the codebase systematically, focusing on API contracts, data flow, and component relationships before implementing new features.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | Latest | Web framework | Lightweight, Python-native |
| LlamaIndex | Latest | RAG framework | Industry standard for LLM apps |
| ChromaDB | Latest | Vector storage | Simple, persistent, session-isolated |
| Ollama | Latest | Local LLM inference | Privacy-focused, runs locally |
| sentence-transformers | Latest | Embeddings | Fast, lightweight (384-dim) |

### Frontend
| Library | Version | Purpose |
|---------|---------|---------|
| React | 18 | UI framework |
| React Router | v7 | SPA routing |
| TailwindCSS | v4 | Styling |
| force-graph | Latest | Graph visualization |
| Lucide React | Latest | Icons |

### Supporting
| Library | Purpose |
|---------|---------|
| pypdf | PDF text extraction |
| python-thai-utils | Text processing |
| sentence-splitter | Document chunking |

## Architecture Patterns

### Recommended Project Structure
```
BitRAG/
├── web_app.py                 # Flask backend (1008 lines)
├── src/bitrag/
│   ├── core/                  # Core RAG modules
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration dataclass
│   │   ├── indexer.py        # Document indexing (387 lines)
│   │   ├── query.py          # Query engine (529 lines)
│   │   └── hybrid_search.py  # Hybrid search (301 lines)
│   ├── cli/                   # CLI interface
│   └── tui/                   # Terminal UI
└── frontend/                  # Pre-bundled React (static files)
```

### Pattern 1: Lazy Initialization with Thread Lock
**What:** Components initialized on first request with double-checked locking
**When to use:** Expensive initialization that shouldn't block startup
**Example (web_app.py):**
```python
def ensure_initialized():
    global initialized
    if not initialized:
        with init_lock:
            if not initialized:  # Double-check
                initialize_components()
```

### Pattern 2: Session-Isolated Storage
**What:** Each session has its own ChromaDB collection and directories
**When to use:** Multi-tenant or multi-project data isolation
**Example (config.py):**
```python
collection_name = f"bitrag_documents_{session_id}"
```

### Pattern 3: Streaming Response with SSE
**What:** Long responses streamed as Server-Sent Events
**When to use:** LLM responses that may take time
**Example (web_app.py):**
```python
@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    def generate():
        for chunk in query_engine.query_streaming(question):
            yield f"data: {json.dumps(chunk)}\n\n"
    return Response(generate(), mimetype='text/event-stream')
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Document chunking | Custom splitting | SentenceSplitter | Handles edge cases, preserves semantics |
| Vector search | Raw cosine similarity | ChromaDB built-ins | Optimized, persistent |
| LLM streaming | Manual chunking | LlamaIndex stream_complete | Handles tokenization properly |
| Embeddings | Custom models | sentence-transformers | Pre-trained, optimized |

**Key insight:** The LlamaIndex framework handles most complex RAG operations. Custom code should focus on application-specific logic.

## Common Pitfalls

### Pitfall 1: Frontend Source Code Missing
**What goes wrong:** Frontend is pre-bundled, source not in repo
**Why it happens:** Build step outputs to `frontend/assets/`, source elsewhere
**How to avoid:** If modifying frontend, need to set up separate frontend repo
**Warning signs:** No `frontend/src/` directory, only `frontend/assets/`

### Pitfall 2: Session Hardcoding
**What goes wrong:** `session_id = "default"` hardcoded in web_app.py
**Why it happens:** Quick implementation for MVP
**How to avoid:** Implement proper session management before multi-session features
**Warning signs:** All data goes to `sessions/default/`

### Pitfall 3: Global State in Flask
**What goes wrong:** indexer, query_engine are global module variables
**Why it happens:** Simple architecture for single-user app
**How to avoid:** Consider Flask application context or request-scoped objects for multi-user
**Warning signs:** Thread safety concerns with concurrent requests

### Pitfall 4: Graph Keyword Extraction Quality
**What goes wrong:** Simple word frequency misses semantic relationships
**Why it happens:** No LLM for keyword extraction (only for summary)
**How to avoid:** Use LLM-based tag extraction (Phase 2)
**Warning signs:** "keywords" are common words despite stopword filtering

## Code Examples

### Document Indexing Flow (web_app.py → indexer.py)
```python
# web_app.py:upload_document() [Lines 427-492]
@app.route("/api/documents", methods=["POST"])
def upload_document():
    file = request.files["file"]
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(temp_path)
    
    doc_id = indexer.index_document(temp_path)
    os.remove(temp_path)
    
    return jsonify({"success": True, "id": doc_id, "name": file.filename})
```

### Query Engine Streaming (query.py)
```python
# query.py:query_streaming() [Lines 471-520]
def query_streaming(self, question: str) -> Generator:
    retrieved_context = self.get_retrieved_context(question)
    yield {"type": "sources", "sources": retrieved_context}
    
    context = "\n\n---\n\n".join(context_parts)
    prompt = DEFAULT_RAG_PROMPT.format(context=context, question=question)
    
    for chunk in self.llm.stream_complete(prompt):
        yield {"type": "chunk", "text": chunk.delta}
    
    yield {"type": "done", "response": response_text}
```

### Graph Node Structure (web_app.py)
```python
# web_app.py:get_graph_data() [Lines 935-950]
nodes.append({
    "id": doc_id,
    "name": file_name,
    "val": 3,  # Fixed - needs to be dynamic
    "group": category,  # 1-5 based on file type
    "keywords": top_10_keywords,
    "summary": llm_summary_or_truncated,
})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| In-memory vectors | ChromaDB persistent | Current | Data survives restarts |
| Single model | Dual model mode | Current | Different models for different tasks |
| Vector-only search | Optional hybrid (BM25+RRF) | Current | Better keyword matching |
| Basic keyword extraction | LLM summary + word freq keywords | Current | Better context |

**Deprecated/outdated:**
- None identified - codebase is current

## Open Questions

1. **Where is the frontend source code?**
   - What we know: Only bundled assets exist in `frontend/assets/`
   - What's unclear: Original source location or if it was discarded
   - Recommendation: Set up frontend development environment if UI changes needed

2. **How to handle multi-user sessions?**
   - What we know: Currently single "default" session
   - What's unclear: Session management UX design
   - Recommendation: Define session concept clearly before implementation

3. **Graph visualization broken - root cause?**
   - What we know: force-graph library used, API returns data
   - What's unclear: Frontend JS error or data format issue
   - Recommendation: Inspect browser console when visiting /graph

## Sources

### Primary (HIGH confidence)
- web_app.py - Complete endpoint documentation
- src/bitrag/core/indexer.py - Complete indexing logic
- src/bitrag/core/query.py - Complete query logic
- src/bitrag/core/config.py - Configuration structure

### Secondary (MEDIUM confidence)
- frontend/assets/index-*.js - Bundled frontend (reverse-engineered)
- frontend/assets/index-*.css - Styling

### Tertiary (LOW confidence)
- N/A - All primary sources available

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Well-documented libraries
- Architecture: HIGH - Clear patterns identified
- Pitfalls: MEDIUM - Based on code analysis, some untested

**Research date:** 2026-04-02
**Valid until:** 90 days (stable codebase)
