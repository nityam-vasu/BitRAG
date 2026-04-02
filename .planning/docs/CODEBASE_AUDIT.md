# BitRAG Codebase Audit - Master Summary

**Document:** CODEBASE_AUDIT.md
**Version:** 1.0
**Date:** 2026-04-02
**Phase:** 1 of 6

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Backend framework | Flask |
| Frontend framework | React (bundled, source missing) |
| Vector DB | ChromaDB |
| LLM | Ollama |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| Graph library | force-graph |

---

## Where to Find X

| Need | File | Lines |
|------|------|-------|
| API endpoints | web_app.py | 259-988 |
| Document indexing | src/bitrag/core/indexer.py | 108-187 |
| Query processing | src/bitrag/core/query.py | 471-520 |
| Graph endpoint | web_app.py | 784-988 |
| Session management | src/bitrag/tui/chat.py | 198-322 |
| Configuration | src/bitrag/core/config.py | 23-68 |

---

## API Summary

### Endpoints (15 total)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Non-streaming chat |
| `/api/chat/stream` | POST | Streaming chat (SSE) |
| `/api/documents` | GET, POST | List/upload documents |
| `/api/documents/<id>` | DELETE | Delete document |
| `/api/graph` | GET | Graph visualization data |
| `/api/settings` | GET, POST | Get/update settings |
| `/api/models` | GET | List Ollama models |
| `/api/models/download` | POST | Download model |
| `/api/models/delete` | POST | Delete model |
| `/api/system/info` | GET | System metrics |
| `/api/status` | GET | Server status |

---

## Critical Findings

### 🔴 Frontend Source Missing

**Impact:** HIGH - Cannot modify UI directly

**Status:** Only bundled assets exist in `frontend/assets/`

**Solution Required:**
- Option A: Recover from git history
- Option B: Create new React project
- Option C: Modify bundled JS (not recommended)

---

### 🟡 Graph Visualization Broken

**Impact:** MEDIUM - Visual feature affected

**Root Cause:** Unknown (source code missing)

**Backend Status:** ✅ API returns valid data

**Solution Required:**
- Recover frontend source
- Fix force-graph integration
- Add dynamic node sizing
- Add LLM-based tag extraction

---

### 🟢 Backend Fully Functional

**Status:** All core features work

- Document upload ✅
- Chat queries ✅
- Settings management ✅
- Model management ✅
- System info ✅

---

## Data Structures

### Document Storage (ChromaDB)

```
Collection: bitrag_documents_{session_id}
├── ids: [node_id, ...]
├── embeddings: [384-dim vector, ...]
├── documents: [text chunk, ...]
└── metadatas: [{file_name, file_path, indexed_at}, ...]
```

### Session Storage

```
sessions/{session_id}/
├── uploads/
├── chroma_db/
└── session.json  (TUI only)
```

### Graph Data

```json
{
  "nodes": [{"id", "name", "val", "group", "keywords", "summary"}],
  "links": [{"source", "target", "value", "label"}]
}
```

---

## Configuration

### Config Fields (config.py)

| Field | Default | Purpose |
|-------|---------|---------|
| embedding_model | all-MiniLM-L6-v2 | Embedding model |
| default_model | llama3.2:1b | Default LLM |
| chunk_size | 512 | Text chunk size |
| top_k | 3 | Retrieval count |
| ollama_base_url | localhost:11434 | Ollama URL |

### Runtime Settings (web_app.py)

| Variable | Default | Purpose |
|----------|---------|---------|
| current_model | llama3.2:1b | Active model |
| session_id | "default" | Current session |

---

## File Inventory

### Core Files

| File | Lines | Purpose |
|------|-------|---------|
| web_app.py | 1008 | Flask API server |
| src/bitrag/core/indexer.py | 387 | Document indexing |
| src/bitrag/core/query.py | 547 | Query engine |
| src/bitrag/core/config.py | 124 | Configuration |
| src/bitrag/core/hybrid_search.py | 301 | Hybrid search |
| src/bitrag/tui/chat.py | 330 | Session management |

### Frontend Files

| File | Status |
|------|--------|
| frontend/src/ | ❌ MISSING |
| frontend/assets/index-*.js | ✅ Bundled |
| frontend/assets/index-*.css | ✅ Bundled |

---

## Key Flows

### Document Upload → Index → Query

```
PDF → web_app.py:upload_document() → indexer.index_document()
  → ChromaDB (embeddings stored)
  → query_engine.query_streaming()
  → Ollama LLM → Response
```

### Graph Generation

```
/api/graph → indexer.list_documents()
  → For each doc: extract keywords, generate summary
  → Create nodes array
  → Create links (shared keywords)
  → Return JSON
```

---

## Dependencies

### Python Packages

```
flask
llama-index
chromadb
sentence-transformers
pypdf
requests
psutil
```

### Frontend Packages (in bundled JS)

```
react
react-dom
react-router-dom
force-graph
lucide-react
```

---

## Recommendations for Subsequent Phases

### Phase 2: Graph Module

1. **Priority 1:** Recover/create frontend source
2. **Priority 2:** Fix graph endpoint (consistent IDs, dynamic sizing)
3. **Priority 3:** Add LLM-based summary generation
4. **Priority 4:** Add LLM-based tag extraction
5. **Priority 5:** Enhance visualization (zoom, pan, click, filter)

### Phase 3: Model Selection

1. Add `summary_model` to Config
2. Add `tag_model` to Config
3. Update settings API
4. Wire to summary/tag generators

### Phase 4: Chat Persistence

1. Expose session endpoints in web_app.py
2. Use existing SessionManager from TUI
3. Add export functionality
4. Create session_exporter.py

---

## Verification Commands

```bash
# Check server status
curl http://localhost:5000/api/status

# List documents
curl http://localhost:5000/api/documents

# Get graph data
curl http://localhost:5000/api/graph

# Test chat (requires documents)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

---

## Next Steps

1. **Phase 2:** Reimagine graph module
   - Create summary_generator.py
   - Create tag_extractor.py
   - Create graph_builder.py
   - Fix/enhance frontend visualization

2. **Continue** through phases 3-6 as planned

---

## Audit Completed

- [x] API Contract documented
- [x] Component Inventory created
- [x] Data Flow mapped
- [x] Configuration documented
- [x] Graph Issues investigated
- [x] This summary created

**Audit Date:** 2026-04-02
**Auditor:** Phase 1 Execution
**Confidence:** HIGH
