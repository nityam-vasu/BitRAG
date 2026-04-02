# BitRAG Enhancement - Phase Plans Summary

**Project:** BitRAG Enhancement Roadmap
**Date:** 2026-04-02
**Total Phases:** 6
**Estimated Time:** 12-17 hours

---

## Quick Reference

| Phase | Name | Hours | Dependencies |
|-------|------|-------|---------------|
| 1 | Codebase Audit | 2-3 | None |
| 2 | Graph Module Reimagined | 4-6 | Phase 1 |
| 3 | Model Selection | 1-2 | Phase 2 |
| 4 | Chat Persistence | 2-3 | Phase 1 |
| 5 | Current Chat Export | 1 | Phase 4 |
| 6 | Frontend Polish | 2-3 | All |

---

## Phase 1: Codebase Audit

### Goal
Comprehensive documentation of BitRAG codebase

### Key Deliverables
- `API_CONTRACT.md` - All endpoint documentation
- `COMPONENT_INVENTORY.md` - Module catalog
- `DATA_FLOW.md` - Flow diagrams
- `GRAPH_ISSUES.md` - Graph diagnosis

### Critical Questions
- Is frontend source available?
- What's broken in graph visualization?
- How does session management work?

---

## Phase 2: Graph Module Reimagined

### Goal
Transform graph from keyword-based to AI-powered visualization

### Key Deliverables
- `summary_generator.py` - LLM-based summaries
- `tag_extractor.py` - 5-10 tags per document
- `graph_builder.py` - Enhanced graph data
- Fixed force-graph visualization

### New Data Structure
```json
{
  "nodes": [{
    "id": "doc_id",
    "name": "file.pdf",
    "val": 5,  // Dynamic
    "summary": "AI summary...",
    "tags": ["topic1", "topic2", ...]
  }],
  "links": [{
    "source": "id1",
    "target": "id2",
    "value": 3,  // Shared tags
    "label": "tag1, tag2"
  }]
}
```

### Files to Create
```
src/bitrag/core/summary_generator.py
src/bitrag/core/tag_extractor.py
src/bitrag/core/graph_builder.py
```

---

## Phase 3: Model Selection

### Goal
Allow users to select which model generates summaries/tags

### New Settings
```python
@dataclass
class Config:
    model: str = "llama3.2:1b"        # Chat
    summary_model: str = "llama3.2:1b" # Summaries
    tag_model: str = "llama3.2:1b"      # Tags
```

### API Changes
- `GET /api/settings` returns `summary_model`, `tag_model`
- `POST /api/settings` accepts `summary_model`, `tag_model`

---

## Phase 4: Chat Persistence & Export

### Goal
Enable viewing and exporting previous chat sessions

### New Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sessions` | GET | List all sessions |
| `/api/sessions/<id>` | GET | Get session details |
| `/api/sessions/<id>` | PATCH | Rename session |
| `/api/sessions/<id>` | DELETE | Delete session |
| `/api/sessions/<id>/export` | GET | Export as TXT |

### Files to Create
```
src/bitrag/core/session_exporter.py
```

---

## Phase 5: Current Chat Export

### Goal
One-click export of current conversation

### New Endpoint
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/export` | GET | Download current chat as TXT |

### UI Addition
- "Export Chat" button in chat header
- Disabled when no messages
- Shows loading state during export

---

## Phase 6: Frontend Polish

### Goal
Polish UI and ensure integration

### Tasks
- Loading states for all async operations
- Error handling UI
- Toast notifications
- Performance optimization
- Cross-browser testing

### Critical
- **Verify frontend source availability first**

---

## Success Criteria

1. ✅ Graph displays documents with AI-generated summaries
2. ✅ Nodes linked by shared tags (5-10 per document)
3. ✅ Node size reflects connection count
4. ✅ Model selection works for summary/tag generation
5. ✅ Previous sessions visible and exportable
6. ✅ Current chat exportable as TXT
7. ✅ All async operations have loading states
8. ✅ Error handling provides user feedback

---

## Files Reference

### Created Documents
```
.planning/
├── CONTEXT.md              # Project decisions & constraints
├── ROADMAP.md              # Master roadmap
└── phases/
    ├── 01-codebase-audit/
    │   ├── 01-RESEARCH.md
    │   └── 01-PLAN.md
    ├── 02-graph-reimagined/
    │   ├── 02-RESEARCH.md
    │   └── 02-PLAN.md
    ├── 03-model-selection/
    │   ├── 03-RESEARCH.md
    │   └── 03-PLAN.md
    ├── 04-chat-persistence/
    │   ├── 04-RESEARCH.md
    │   └── 04-PLAN.md
    ├── 05-current-export/
    │   ├── 05-RESEARCH.md
    │   └── 05-PLAN.md
    └── 06-frontend-polish/
        ├── 06-RESEARCH.md
        └── 06-PLAN.md
```

### New Code Files
```
src/bitrag/core/
├── summary_generator.py    # Phase 2
├── tag_extractor.py       # Phase 2
├── graph_builder.py      # Phase 2
└── session_exporter.py   # Phase 4
```

### Modified Code Files
```
web_app.py                 # All phases - new endpoints
src/bitrag/core/
├── config.py              # Phase 3 - new settings
└── indexer.py             # Phase 2 - store metadata
frontend/src/              # Phase 2, 3, 4, 5, 6 - UI changes
```

---

## Dependencies Graph

```
Phase 1 (Audit)
    │
    ├─────────────────────────────┐
    │                             │
    ▼                             ▼
Phase 2 (Graph)            Phase 4 (Persistence)
    │                             │
    │                             │
    └──────────┬──────────────────┘
               │
               ▼
          Phase 3 (Model Selection)
               │
               ▼
          Phase 5 (Current Export)
               │
               ▼
          Phase 6 (Polish)
```

---

## Next Steps

1. **Start Phase 1** - Codebase Audit
   - Verify frontend source status
   - Diagnose graph issues
   - Document API contracts

2. **Execute Phases 2-6** - Following dependency order

3. **Test** - Full integration testing

4. **Deploy** - User testing and feedback
