# Phase 4: Chat Persistence & Export - Plan

**Phase:** 4 - Chat Persistence & Export
**Goal:** Enable viewing and exporting previous chat sessions
**Estimated Duration:** 2-3 hours

## Context

### What We're Building
This phase adds:
1. Session list endpoint to view all sessions
2. Session loading endpoint
3. Session export endpoint (TXT format)
4. Session management (rename, delete)
5. Frontend UI for session management

### From Phase 1 Learnings
- Sessions stored as JSON in `sessions/<id>/session.json`
- `ChatSession` class handles persistence
- No current UI for session management

## Tasks

### Task 1: Create Session API Endpoints
**What:** Add CRUD endpoints for sessions
**Why:** Backend support for session management
**Verification:** All endpoints return correct data

#### Sub-tasks:
- [ ] Create `GET /api/sessions` - List all sessions
- [ ] Create `GET /api/sessions/<id>` - Get session details
- [ ] Create `PATCH /api/sessions/<id>` - Update session (rename)
- [ ] Create `DELETE /api/sessions/<id>` - Delete session
- [ ] Create `GET /api/sessions/<id>/export` - Export as TXT
- [ ] Create `POST /api/sessions` - Create new session

**Time estimate:** 45 minutes

---

### Task 2: Implement Session Exporter
**What:** Create session export logic
**Why:** Generate readable TXT files
**Verification:** Exported files are valid and readable

#### Sub-tasks:
- [ ] Create `src/bitrag/core/session_exporter.py`
- [ ] Implement `export_session_as_text()` function
- [ ] Format with headers, timestamps, sources
- [ ] Handle messages with/without sources
- [ ] Add error handling for missing sessions

**Time estimate:** 30 minutes

---

### Task 3: Add Session Management to TUI
**What:** Integrate session management into TUI chat
**Why:** Allow switching between sessions
**Verification:** Can switch, rename, delete sessions from TUI

#### Sub-tasks:
- [ ] Add session list command
- [ ] Add session switch command
- [ ] Add session rename command
- [ ] Add session delete command
- [ ] Add session export command

**Time estimate:** 30 minutes

---

### Task 4: Update Web Chat Session Handling
**What:** Improve session persistence in web chat
**Why:** Better session management
**Verification:** Sessions persist correctly

#### Sub-tasks:
- [ ] Update session save logic in chat endpoint
- [ ] Add session title auto-generation
- [ ] Add session metadata (message count, last activity)
- [ ] Handle concurrent access gracefully

**Time estimate:** 30 minutes

---

## Verification

### Phase Goal
Users can view, load, rename, delete, and export previous chat sessions.

### Success Criteria
1. [ ] `GET /api/sessions` returns list of all sessions
2. [ ] `GET /api/sessions/<id>` returns session with messages
3. [ ] `PATCH /api/sessions/<id>` renames session
4. [ ] `DELETE /api/sessions/<id>` removes session
5. [ ] `GET /api/sessions/<id>/export` returns TXT file
6. [ ] Sessions visible in UI (if frontend available)

### Verification Commands
```bash
# List all sessions
curl -s http://localhost:5000/api/sessions | python -m json.tool

# Get specific session
curl -s http://localhost:5000/api/sessions/default | python -m json.tool

# Export session
curl -s http://localhost:5000/api/sessions/default/export

# Rename session
curl -X PATCH http://localhost:5000/api/sessions/default \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title"}'

# Delete session
curl -X DELETE http://localhost:5000/api/sessions/session123
```

## Dependencies

| Dependency | Type | Phase |
|-----------|------|-------|
| Phase 1: Codebase Audit | Required | Phase 1 |

## New Files

| File | Purpose |
|------|---------|
| `src/bitrag/core/session_exporter.py` | Session export logic |

## Modified Files

| File | Changes |
|------|---------|
| `web_app.py` | Add session endpoints |
| `src/bitrag/tui/chat.py` | Add session management |
| `src/bitrag/core/chat_session.py` | Enhance session handling |

## API Specification

### GET /api/sessions
**Response:**
```json
{
  "sessions": [
    {
      "id": "default",
      "title": "Research Session",
      "message_count": 12,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:22:00Z"
    }
  ]
}
```

### GET /api/sessions/<id>
**Response:**
```json
{
  "id": "default",
  "title": "Research Session",
  "model": "llama3.2:1b",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:22:00Z",
  "messages": [
    {
      "content": "What is RAG?",
      "role": "user",
      "timestamp": "2024-01-15T10:30:00Z",
      "sources": []
    }
  ]
}
```

### GET /api/sessions/<id>/export
**Response:** Plain text file download

## Export Format
```
=== BitRAG Chat Export ===
Session: default
Date: 2024-01-15
Model: llama3.2:1b

--- Chat History ---

[USER] 2024-01-15T10:30:00Z
What is RAG?

[ASSISTANT] 2024-01-15T10:30:05Z
RAG stands for Retrieval-Augmented Generation...

Sources: doc1.pdf, doc2.pdf

---
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Large session files | MEDIUM | LOW | Lazy load messages, pagination |
| Concurrent access | LOW | MEDIUM | Timestamp-based conflict detection |
| Missing session | LOW | LOW | Return 404 with clear message |

## Next Phase

Phase 5: Current Chat TXT Export
- Adds export button to current chat view
- Simpler than full session management

---

**Plan created:** 2026-04-02
**Ready for execution:** Yes
