# Phase 1: Codebase Audit - Plan

**Phase:** 1 - Codebase Audit
**Goal:** Comprehensive documentation of BitRAG codebase
**Estimated Duration:** 2-3 hours

## Context

### What We're Building
This is Phase 1 of 6 in the BitRAG Enhancement Roadmap. The audit will document the entire codebase to inform subsequent phases:
- Phase 2: Graph Module Reimagined
- Phase 3: Model Selection in Settings
- Phase 4: Chat Persistence & Export
- Phase 5: Current Chat TXT Export
- Phase 6: Frontend Polish

### Why This Phase First
Before modifying code, we need to understand what exists. This prevents:
- Reinventing existing functionality
- Breaking working features
- Missing integration points

## Tasks

### Task 1: Create API Contract Documentation
**What:** Document all Flask endpoints with request/response schemas
**Why:** API contract is foundation for frontend changes
**Verification:** Each endpoint has working curl examples

#### Sub-tasks:
- [ ] Document GET endpoints (status, settings, documents, graph, models, system/info)
- [ ] Document POST endpoints (chat, chat/stream, documents, settings, models/download, models/delete)
- [ ] Document DELETE endpoints (documents)
- [ ] Add example requests/responses for each
- [ ] Save to `.planning/docs/API_CONTRACT.md`

**Time estimate:** 30 minutes

---

### Task 2: Create Component Inventory
**What:** Catalog all Python modules and their responsibilities
**Why:** Prevent duplication and identify integration points
**Verification:** Every file > 50 lines has a purpose description

#### Sub-tasks:
- [ ] Document `web_app.py` structure (all endpoints)
- [ ] Document `src/bitrag/core/` modules (config, indexer, query, hybrid_search)
- [ ] Document `src/bitrag/cli/` commands
- [ ] Document `src/bitrag/tui/` components
- [ ] Create component dependency diagram
- [ ] Save to `.planning/docs/COMPONENT_INVENTORY.md`

**Time estimate:** 45 minutes

---

### Task 3: Document Data Flow
**What:** Map how data moves through the system
**Why:** Critical for understanding upload→index→query→response
**Verification:** Can trace a single document from upload to being queryable

#### Sub-tasks:
- [ ] Document PDF upload flow (frontend → API → indexer → ChromaDB)
- [ ] Document query flow (frontend → API → query_engine → LLM → response)
- [ ] Document graph data flow (ChromaDB → keyword extraction → node/link creation)
- [ ] Document session data flow (where data stored, how persisted)
- [ ] Create ASCII flow diagrams
- [ ] Save to `.planning/docs/DATA_FLOW.md`

**Time estimate:** 30 minutes

---

### Task 4: Document Configuration Options
**What:** Catalog all configurable settings
**Why:** Foundation for Phase 3 (model selection) and other settings changes
**Verification:** All settings have descriptions and valid values

#### Sub-tasks:
- [ ] Document Config dataclass fields
- [ ] Document runtime settings (model, port, modes)
- [ ] Document directory structures
- [ ] Document file naming conventions
- [ ] Save to `.planning/docs/CONFIGURATION.md`

**Time estimate:** 15 minutes

---

### Task 5: Investigate Graph Issues
**What:** Diagnose why graph visualization is broken
**Why:** Critical for Phase 2
**Verification:** Can identify root cause

#### Sub-tasks:
- [ ] Check if `/api/graph` endpoint returns valid data
- [ ] Examine force-graph integration in frontend
- [ ] Test graph endpoint with curl
- [ ] Document findings about what's broken
- [ ] Save to `.planning/docs/GRAPH_ISSUES.md`

**Time estimate:** 30 minutes

---

### Task 6: Create CODEBASE_AUDIT.md Summary
**What:** Master document combining all findings
**Why:** Single source of truth for subsequent phases
**Verification:** Planner can use this alone to understand codebase

#### Sub-tasks:
- [ ] Combine all documentation into single file
- [ ] Add quick reference section
- [ ] Add "where to find X" guide
- [ ] Save to `.planning/docs/CODEBASE_AUDIT.md`

**Time estimate:** 15 minutes

---

## Verification

### Phase Goal
All subsequent phase planners can understand the codebase without reading source code.

### Success Criteria
1. [ ] API_CONTRACT.md has all endpoints documented
2. [ ] COMPONENT_INVENTORY.md lists all modules with purposes
3. [ ] DATA_FLOW.md includes ASCII diagrams for key flows
4. [ ] CONFIGURATION.md documents all settings
5. [ ] GRAPH_ISSUES.md identifies what's broken in graph
6. [ ] CODEBASE_AUDIT.md is comprehensive summary

### Verification Commands
```bash
# Test graph endpoint returns valid JSON
curl -s http://localhost:5000/api/graph | python -m json.tool

# Test status endpoint
curl -s http://localhost:5000/api/status | python -m json.tool

# List all documents
curl -s http://localhost:5000/api/documents | python -m json.tool
```

## Dependencies

**This phase has no dependencies** - it's the first phase.

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Frontend source missing | HIGH | MEDIUM | Document what exists, note need for source |
| Graph debugging takes longer | MEDIUM | LOW | Allocate time, document findings regardless |
| Incomplete API documentation | LOW | HIGH | Double-check each endpoint manually |

## Output Files

| File | Location | Purpose |
|------|----------|---------|
| API_CONTRACT.md | .planning/docs/ | All endpoint documentation |
| COMPONENT_INVENTORY.md | .planning/docs/ | Module catalog |
| DATA_FLOW.md | .planning/docs/ | Flow diagrams |
| CONFIGURATION.md | .planning/docs/ | Settings documentation |
| GRAPH_ISSUES.md | .planning/docs/ | Graph diagnosis |
| CODEBASE_AUDIT.md | .planning/docs/ | Master summary |

## Next Phase

Phase 2: Graph Module Reimagined
- Uses API_CONTRACT.md to understand current graph endpoint
- Uses GRAPH_ISSUES.md to fix visualization
- Uses DATA_FLOW.md to plan new summary/tag generation

---

**Plan created:** 2026-04-02
**Ready for execution:** Yes
