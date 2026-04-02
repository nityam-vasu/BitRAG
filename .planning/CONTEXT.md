# BitRAG Enhancement Project - Context

**Project:** BitRAG - Local RAG Application Enhancement
**Created:** 2026-04-02

---

## Decisions (Locked - Research These)

### 1. Technology Stack
- **Backend:** Python Flask (existing)
- **Frontend:** React (existing, source may need recovery)
- **LLM:** Ollama (existing)
- **Vector DB:** ChromaDB (existing)
- **Graph Visualization:** force-graph (existing)

### 2. Graph Module Approach
- Use LLM for summary generation (small model like llama3.2:1b)
- Use LLM for tag extraction (5-10 tags per document)
- Tags drive node linking and edge weights
- Dynamic node sizing based on connections
- Fix broken force-graph visualization

### 3. Model Selection
- Add summary_model and tag_model to settings
- Keep existing model for chat queries
- Default to llama3.2:1b for all (fast, local-friendly)

### 4. Chat Persistence
- Use existing session structure (JSON in sessions/)
- Add session list endpoint
- Add session export as TXT
- Keep message structure: content, role, timestamp, sources

### 5. Export Format
```
=== BitRAG Chat Export ===
Session: <id>
Date: <date>
Model: <model>

--- Chat History ---

[USER] <timestamp>
<message>

[ASSISTANT] <timestamp>
<response>
Sources: doc1.pdf, doc2.pdf

---
```

---

## Claude's Discretion (Research Options, Recommend)

### 1. Summary Generation Approach
- **Option A:** Extractive (first N chars) - Fast, no LLM needed
- **Option B:** Abstractive (LLM) - Better quality, slower
- **Recommendation:** Abstractive with extractive fallback

### 2. Tag Extraction Approach
- **Option A:** Simple keyword frequency - Fast, low quality
- **Option B:** LLM-based - Better semantic tags
- **Recommendation:** LLM-based with keyword fallback

### 3. Frontend Development
- **Option A:** Recover source from git history
- **Option B:** Set up new frontend project
- **Option C:** Modify bundled assets directly
- **Recommendation:** Check git history first, then decide

### 4. Graph Enhancements
- **Option A:** 2D force-graph (existing)
- **Option B:** 3D force-graph for more nodes
- **Recommendation:** Start with 2D, add 3D if needed

---

## Deferred Ideas (Out of Scope)

### Not in This Enhancement Cycle
- Multi-user support / authentication
- Cloud deployment
- Mobile app
- Plugin system
- Document version history
- Collaborative annotation
- Advanced search filters
- Custom chunking strategies
- Multiple vector stores
- Graph database integration
- Semantic caching
- Query expansion
- Re-ranking

### Rejected Ideas
- Use OpenAI API (user wants local-only)
- Real-time collaboration (out of scope)
- Mobile-first design (desktop focus)

---

## Phase Order

1. **Phase 1:** Codebase Audit (2-3 hours)
2. **Phase 2:** Graph Module Reimagined (4-6 hours)
3. **Phase 3:** Model Selection in Settings (1-2 hours)
4. **Phase 4:** Chat Persistence & Export (2-3 hours)
5. **Phase 5:** Current Chat TXT Export (1 hour)
6. **Phase 6:** Frontend Polish & Integration (2-3 hours)

**Total Estimated:** 12-17 hours

---

## Key Files to Modify

### Backend (web_app.py)
- `/api/graph` - Enhanced graph endpoint
- `/api/settings` - Model selection
- `/api/sessions/*` - Session management
- `/api/chat/export` - Current chat export

### Core Modules (src/bitrag/core/)
- `summary_generator.py` - NEW
- `tag_extractor.py` - NEW
- `graph_builder.py` - NEW
- `session_exporter.py` - NEW
- `indexer.py` - Store metadata
- `config.py` - New settings

### Frontend (if source available)
- Graph visualization component
- Settings page
- Session management UI
- Export buttons

---

## Critical Success Criteria

1. Graph displays documents as nodes with AI-generated summaries
2. Nodes linked by shared tags (5-10 per document)
3. Node size reflects connection count
4. Model selection works for summary/tag generation
5. Previous sessions visible and exportable
6. Current chat exportable as TXT
7. All async operations have loading states
8. Error handling provides user feedback

---

## Out of Scope Constraints

- No authentication/multi-user (single user local app)
- No cloud features (all local)
- No mobile app (desktop focus)
- No third-party APIs (Ollama only)
