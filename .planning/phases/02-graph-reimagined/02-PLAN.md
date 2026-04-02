# Phase 2: Graph Module Reimagined - Plan

**Phase:** 2 - Graph Module Reimagined
**Goal:** Transform graph from keyword-based to AI-powered visualization
**Estimated Duration:** 4-6 hours

## Context

### What We're Building
This phase reimagines the graph module with:
1. LLM-powered summary generation (small model parsing PDFs → summaries)
2. Tag extraction (5-10 tags per document from summaries)
3. Tag-based node linking (shared tags → weighted edges)
4. Dynamic node sizing (based on connections)
5. Fixed and enhanced graph visualization

### From Phase 1 Learnings
- Current graph uses simple word frequency for keywords
- Summary generation is LLM-based but truncated fallback exists
- Node size is fixed at `val: 3`
- Graph endpoint at `/api/graph` (Lines 784-988 in web_app.py)
- Frontend uses force-graph library

## Tasks

### Task 1: Create Summary Generator Module
**What:** Create `src/bitrag/core/summary_generator.py`
**Why:** Modular, reusable summary generation
**Verification:** Can generate summary for any text, handles long documents

#### Sub-tasks:
- [ ] Create `SummaryGenerator` class
- [ ] Implement LLM-based summary with Ollama
- [ ] Add text truncation for long documents (first 3000 chars)
- [ ] Add configurable max length
- [ ] Add timeout handling (30 seconds)
- [ ] Add fallback to extractive summary if LLM fails
- [ ] Write unit tests

**Time estimate:** 45 minutes

---

### Task 2: Create Tag Extractor Module
**What:** Create `src/bitrag/core/tag_extractor.py`
**Why:** Intelligent tag extraction using LLM
**Verification:** Returns 5-10 valid tags per document

#### Sub-tasks:
- [ ] Create `TagExtractor` class
- [ ] Implement LLM-based tag extraction with JSON output
- [ ] Add JSON parsing with error handling
- [ ] Add fallback to keyword extraction if JSON parsing fails
- [ ] Ensure 5-10 diverse tags returned
- [ ] Write unit tests

**Time estimate:** 45 minutes

---

### Task 3: Create Graph Builder Module
**What:** Create `src/bitrag/core/graph_builder.py`
**Why:** Centralized graph data construction
**Verification:** Builds valid nodes/links structure

#### Sub-tasks:
- [ ] Create `GraphBuilder` class
- [ ] Integrate SummaryGenerator and TagExtractor
- [ ] Implement metadata caching (avoid regeneration)
- [ ] Implement dynamic node sizing (connection count)
- [ ] Implement weighted edge calculation (shared tags)
- [ ] Add method to regenerate specific document metadata
- [ ] Add method to clear cache

**Time estimate:** 45 minutes

---

### Task 4: Update Document Indexer
**What:** Modify `src/bitrag/core/indexer.py`
**Why:** Store summaries and tags in ChromaDB metadata
**Verification:** Documents have summary/tag metadata after indexing

#### Sub-tasks:
- [ ] Add `generate_metadata` parameter to `index_document()`
- [ ] Call GraphBuilder during indexing (optional)
- [ ] Store summary in document metadata
- [ ] Store tags in document metadata
- [ ] Add `update_document_metadata()` method
- [ ] Add `regenerate_metadata(doc_id)` method

**Time estimate:** 30 minutes

---

### Task 5: Refactor Graph Endpoint
**What:** Update `/api/graph` endpoint in `web_app.py`
**Why:** Use new modules, fix broken functionality
**Verification:** Endpoint returns enhanced graph data

#### Sub-tasks:
- [ ] Import new modules (SummaryGenerator, TagExtractor, GraphBuilder)
- [ ] Use GraphBuilder instead of inline keyword extraction
- [ ] Return new fields: `tags`, dynamic `val`
- [ ] Add caching to avoid regeneration
- [ ] Add `?refresh=true` query param for forced regeneration
- [ ] Add `GET /api/graph/regenerate` endpoint
- [ ] Add `POST /api/documents/<id>/regenerate-tags` endpoint

**Time estimate:** 45 minutes

---

### Task 6: Fix Force-Graph Visualization
**What:** Debug and fix frontend graph display
**Why:** Current visualization is broken
**Verification:** Graph renders correctly with nodes and edges

#### Sub-tasks:
- [ ] Check if frontend source exists (may need to set up frontend dev)
- [ ] If source exists: Fix force-graph integration
- [ ] Implement dynamic node sizing based on `val` field
- [ ] Implement edge rendering based on `value` field
- [ ] Add zoom/pan controls
- [ ] Add node click handler for preview
- [ ] If source missing: Document need for frontend rebuild

**Time estimate:** 60 minutes

---

### Task 7: Add Graph Enhancements
**What:** Enhance graph with filtering and interaction
**Why:** Better user experience
**Verification:** User can filter by tags, click nodes for preview

#### Sub-tasks:
- [ ] Add tag filter panel (show/hide nodes by tag)
- [ ] Add node search functionality
- [ ] Add highlight on hover
- [ ] Add document preview panel on node click
- [ ] Add zoom controls
- [ ] Add "fit to screen" button

**Time estimate:** 45 minutes

---

## Verification

### Phase Goal
Transform graph from simple keyword visualization to AI-powered document relationship map.

### Success Criteria
1. [ ] `SummaryGenerator` class works with Ollama
2. [ ] `TagExtractor` class returns 5-10 tags
3. [ ] `GraphBuilder` produces nodes with dynamic sizing
4. [ ] `/api/graph` returns enhanced data structure
5. [ ] Graph visualization renders correctly
6. [ ] Nodes are clickable with preview
7. [ ] Tag filtering works

### Verification Commands
```bash
# Test graph endpoint
curl -s http://localhost:5000/api/graph | python -m json.tool

# Should return nodes with:
# - id, name, val (dynamic), group, summary, tags (new field)

# Test with refresh
curl -s "http://localhost:5000/api/graph?refresh=true" | python -m json.tool

# Test regenerate endpoint (after uploading doc)
curl -X POST http://localhost:5000/api/documents/<id>/regenerate-tags
```

## Dependencies

| Dependency | Type | Phase |
|-----------|------|-------|
| Phase 1: Codebase Audit | Required | Phase 1 |
| Understanding current graph endpoint | Required | From Phase 1 |
| Phase 3: Model Selection | Recommended | Phase 3 |

## New Files Created

| File | Purpose |
|------|---------|
| `src/bitrag/core/summary_generator.py` | LLM-based summary generation |
| `src/bitrag/core/tag_extractor.py` | LLM-based tag extraction |
| `src/bitrag/core/graph_builder.py` | Graph data construction |

## Modified Files

| File | Changes |
|------|---------|
| `src/bitrag/core/indexer.py` | Store metadata, add regenerate method |
| `web_app.py` | Refactor graph endpoint, add endpoints |
| `frontend/src/` (if exists) | Fix and enhance graph visualization |

## API Changes

### Modified Endpoints
| Endpoint | Change |
|----------|--------|
| `GET /api/graph` | Returns enhanced data with `tags`, dynamic `val` |

### New Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/graph` | GET | Add `?refresh=true` param |
| `POST /api/documents/<id>/regenerate-tags` | POST | Regenerate metadata |
| `GET /api/graph/regenerate` | GET | Refresh entire graph |

## Data Structure Changes

### New Node Structure
```json
{
  "id": "doc_id",
  "name": "filename.pdf",
  "val": 5,  // Dynamic based on connections
  "group": 1,  // Category
  "summary": "AI-generated summary...",  // NEW
  "tags": ["topic1", "topic2", ...],  // NEW: 5-10 tags
  "keywords": ["legacy", "keywords"]  // Keep for compatibility
}
```

### Enhanced Link Structure
```json
{
  "source": "doc_id_1",
  "target": "doc_id_2",
  "value": 3,  // Number of shared tags
  "label": "tag1, tag2, tag3"  // Top 3 shared tags
}
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM timeout on large docs | MEDIUM | MEDIUM | Truncate to 3000 chars, 30s timeout |
| Tag parsing fails | MEDIUM | LOW | Fallback to keyword extraction |
| Frontend source missing | HIGH | HIGH | Document need for frontend rebuild |
| Performance with many nodes | LOW | MEDIUM | Limit initial render, add clustering |

## Next Phase

Phase 3: Model Selection in Settings
- Uses Phase 2 infrastructure to plug in different models
- Model selection in settings for summary/tag generation

---

**Plan created:** 2026-04-02
**Ready for execution:** Yes (pending Phase 1 completion)
