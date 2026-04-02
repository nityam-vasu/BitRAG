# BitRAG Enhancement Roadmap

**Created:** 2026-04-02
**Project:** BitRAG - Local RAG Application
**Version:** 1.0 → Enhanced

---

## Executive Summary

This roadmap covers 6 major phases to enhance BitRAG with improved graph visualization, AI-powered document processing, persistent chat history, and enhanced settings management.

### Quick Overview

| Phase | Name | Duration | Priority |
|-------|------|----------|----------|
| 1 | Codebase Audit & Documentation | 2-3 hours | HIGH |
| 2 | Graph Module Reimagined | 4-6 hours | HIGH |
| 3 | Model Selection in Settings | 1-2 hours | MEDIUM |
| 4 | Chat Persistence & Export | 2-3 hours | HIGH |
| 5 | Current Chat TXT Export | 1 hour | MEDIUM |
| 6 | Frontend Polish & Integration | 2-3 hours | MEDIUM |

**Total Estimated Time:** 12-17 hours

---

## Phase 1: Codebase Audit & Documentation

### Goal
Comprehensive understanding of existing codebase to inform all future phases.

### Deliverables
- `CODEBASE_AUDIT.md` - Detailed component inventory
- `API_CONTRACT.md` - All endpoints documented
- `DATA_FLOW.md` - How data moves through system

### Tasks
1. [ ] Document all Flask endpoints with request/response schemas
2. [ ] Map frontend React components and their responsibilities
3. [ ] Document state management patterns
4. [ ] Identify all configuration options
5. [ ] Create component dependency graph

### Success Criteria
- Every major file has a clear purpose documented
- API endpoints have request/response examples
- Data flow from upload → indexing → query → response is clear

---

## Phase 2: Graph Module Reimagined

### Goal
Transform the graph module from simple keyword-based to AI-powered document relationship visualization.

### Current State
- Simple keyword frequency extraction
- Static node sizes (val: 3)
- Basic force-graph visualization
- Broken visualization (per user report)

### Proposed State
- AI-powered summary generation using small model
- Intelligent tag generation (5-10 tags per document)
- Tag-based node linking with weighted edges
- Dynamic node sizing based on importance/connections
- Fixed and enhanced graph visualization

### Architecture Changes

```
┌─────────────────────────────────────────────────────────────────┐
│                        PDF Upload Flow                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PDF Upload → Parse → Generate Summary → Generate Tags → Index   │
│                              ↓                    ↓              │
│                        [SUMMARY_DB]              [CHROMA DB]     │
│                              ↓                    ↓              │
│                        Graph Nodes ◄───────────────┘              │
│                              ↓                                    │
│                   Tag-based Edge Creation                        │
│                              ↓                                    │
│                   Enhanced Force-Graph ◄── Dynamic Sizing        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `summary_generator.py` | `src/bitrag/core/` | AI summary generation |
| `tag_generator.py` | `src/bitrag/core/` | Intelligent tag extraction |
| `graph_builder.py` | `src/bitrag/core/` | Graph data structure builder |
| Enhanced `/api/graph` | `web_app.py` | Improved graph endpoint |

### Tasks

#### 2.1: Summary Generator Module
- [ ] Create `src/bitrag/core/summary_generator.py`
- [ ] Implement LLM-based summary generation
- [ ] Add configurable summary length (short/medium/long)
- [ ] Cache summaries to avoid regeneration
- [ ] Fallback to extractive summary if LLM fails

#### 2.2: Tag Generator Module  
- [ ] Create `src/bitrag/core/tag_generator.py`
- [ ] Implement tag extraction using LLM
- [ ] Ensure 5-10 diverse tags per document
- [ ] Include topic, entities, and concept tags
- [ ] Store tags alongside document metadata

#### 2.3: Graph Builder Enhancement
- [ ] Create `src/bitrag/core/graph_builder.py`
- [ ] Implement weighted edge calculation based on tag overlap
- [ ] Add node importance scoring (connections + content density)
- [ ] Dynamic node sizing algorithm
- [ ] Graph clustering for visual grouping

#### 2.4: Backend API Updates
- [ ] Update `/api/graph` endpoint to use new modules
- [ ] Add `/api/graph/regenerate` endpoint for manual refresh
- [ ] Add `/api/documents/<id>/regenerate-tags` endpoint
- [ ] Implement graph data caching

#### 2.5: Frontend Graph Fix & Enhancement
- [ ] Debug and fix broken force-graph visualization
- [ ] Implement dynamic node sizing based on API data
- [ ] Add zoom/pan controls
- [ ] Add node click → document preview
- [ ] Add tag filter panel
- [ ] Add search/highlight functionality

### Success Criteria
- [ ] Graph displays all indexed documents as nodes
- [ ] Edges represent shared tags between documents
- [ ] Node size reflects importance/connections
- [ ] Clicking node shows document preview
- [ ] Tags can be used to filter/highlight nodes
- [ ] Graph auto-refreshes on new document upload

---

## Phase 3: Model Selection in Settings

### Goal
Allow users to select which model generates summaries and tags (separate from chat model).

### Current State
- Single model configuration for chat
- No distinction between chat, summary, and tag models

### Proposed State
- Settings page with model dropdown
- Separate model selection for:
  - Chat/LLM queries
  - Summary generation
  - Tag generation
- Visual indicator of currently selected models

### Tasks

#### 3.1: Backend Model Configuration
- [ ] Add `summary_model` and `tag_model` to Config class
- [ ] Update `/api/settings` to expose model options
- [ ] Add model validation (check if model exists in Ollama)
- [ ] Implement model availability checking

#### 3.2: Frontend Settings Page
- [ ] Add model selection dropdowns
- [ ] Show model status (downloaded/not downloaded)
- [ ] Add "Download Model" button if missing
- [ ] Persist selections to backend

#### 3.3: Integration
- [ ] Wire summary generator to use `summary_model`
- [ ] Wire tag generator to use `tag_model`
- [ ] Add model loading indicators
- [ ] Handle model switching gracefully

### Success Criteria
- [ ] User can select different models for chat, summary, and tags
- [ ] Model selection persists across sessions
- [ ] Clear feedback when model is loading/changed
- [ ] Fallback behavior when selected model unavailable

---

## Phase 4: Chat Persistence & Export

### Goal
Enable persistent chat history with TXT export functionality.

### Current State
- Sessions stored as JSON in `sessions/` directory
- No export functionality
- Previous chats not easily accessible in UI

### Proposed State
- List of previous chat sessions visible in sidebar
- Click to load previous session
- Export any session as TXT file
- Session management (rename, delete, export)

### Tasks

#### 4.1: Backend Session Management
- [ ] Add `/api/sessions` endpoint to list all sessions
- [ ] Add `/api/sessions/<id>` endpoint to get session details
- [ ] Add `/api/sessions/<id>/export` endpoint (TXT format)
- [ ] Add `/api/sessions/<id>/rename` endpoint
- [ ] Add `/api/sessions/<id>/delete` endpoint

#### 4.2: Session Export Format
```
=== BitRAG Chat Export ===
Session: <session_id>
Date: <creation_date>
Model: <model_used>

--- Chat History ---

[USER] <timestamp>
<message_content>

[ASSISTANT] <timestamp>
<message_content>
<sources>
---
```

#### 4.3: Frontend Session UI
- [ ] Add sessions list panel (sidebar or modal)
- [ ] Display session titles and timestamps
- [ ] Add export button per session
- [ ] Add delete/rename options
- [ ] Show confirmation dialogs for destructive actions

### Success Criteria
- [ ] All previous sessions visible in UI
- [ ] Can load any previous session
- [ ] Export generates valid, readable TXT file
- [ ] Delete removes session with confirmation
- [ ] Export includes all message metadata

---

## Phase 5: Current Chat TXT Export

### Goal
Add one-click export of current chat conversation.

### Tasks

#### 5.1: Backend Export API
- [ ] Reuse `/api/sessions/<id>/export` for current session
- [ ] Or create `/api/chat/export` for unsaved current chat

#### 5.2: Frontend Export Button
- [ ] Add "Export Chat" button to chat header
- [ ] Button location: Top-right of chat area
- [ ] Click triggers download of current conversation
- [ ] Visual feedback during export

### Success Criteria
- [ ] Single click exports current chat as TXT
- [ ] Downloaded file has proper formatting
- [ ] Button accessible but not intrusive

---

## Phase 6: Frontend Polish & Integration

### Goal
Ensure all components work together seamlessly with polished UX.

### Tasks

#### 6.1: UI/UX Improvements
- [ ] Loading states for all async operations
- [ ] Error handling with user-friendly messages
- [ ] Toast notifications for actions
- [ ] Responsive design for various screen sizes

#### 6.2: Performance Optimization
- [ ] Lazy load graph component
- [ ] Debounce graph updates
- [ ] Cache model lists
- [ ] Optimize re-renders

#### 6.3: Testing & QA
- [ ] Test all new endpoints
- [ ] Test graph visualization with various data sizes
- [ ] Test export functionality
- [ ] Cross-browser testing

### Success Criteria
- [ ] All features work without errors
- [ ] UI is responsive and polished
- [ ] No console errors
- [ ] All buttons/links functional

---

## Technical Notes

### Recommended Small Models for Summary/Tag

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.2:1b | ~1.3GB | Very Fast | Good | Quick summaries |
| llama3.2:3b | ~2GB | Fast | Better | Balanced |
| qwen2.5:3b | ~2GB | Fast | Good | Multilingual |
| phi3:3.8b | ~2.2GB | Medium | Good | General use |

### Graph Visualization Settings

```javascript
// Recommended force-graph configuration
{
  nodeId: 'id',
  nodeVal: 'val',  // Dynamic sizing
  nodeLabel: 'name',
  nodeColor: 'group',  // Cluster-based coloring
  linkSource: 'source',
  linkTarget: 'target',
  linkValue: 'value',  // Edge weight
  linkLabel: 'label',  // Shared tags
  nodeCanvasObject: (node, ctx) => { /* Custom rendering */ },
  nodeCanvasObjectMode: () => 'replace',
  controls: true,
  cooldownTime: 3000,
  d3AlphaDecay: 0.02,
  d3VelocityDecay: 0.3,
}
```

---

## Dependencies Between Phases

```
Phase 1 (Audit)
    ↓
    ├──────────────────────┐
    ↓                      ↓
Phase 2 (Graph)    Phase 3 (Model Select)
    ↓                      ↓
    └──────────┬───────────┘
               ↓
         Phase 4 (Chat Persistence)
               ↓
         Phase 5 (Current Export)
               ↓
         Phase 6 (Polish)
```

**Important:** Phase 1 (Codebase Audit) should be completed first as it informs all other phases.

---

## Next Steps

1. **Review this roadmap** and adjust priorities/timeline as needed
2. **Start Phase 1** - Codebase Audit
3. **Begin implementation** following the dependency order
4. **Test each phase** before moving to next

---

## Files to Create/Modify

### New Files
```
src/bitrag/core/summary_generator.py
src/bitrag/core/tag_generator.py
src/bitrag/core/graph_builder.py
src/bitrag/core/session_exporter.py
```

### Modified Files
```
web_app.py                    # New endpoints, updated graph logic
src/bitrag/core/config.py     # New model configurations
src/bitrag/core/indexer.py    # Integrate summary/tag generation
src/bitrag/core/query_engine.py
frontend/src/App.tsx          # Route changes, new components
frontend/src/components/*     # New UI components
```

---

*End of Roadmap*
