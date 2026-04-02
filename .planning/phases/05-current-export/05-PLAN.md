# Phase 5: Current Chat TXT Export - Plan

**Phase:** 5 - Current Chat TXT Export
**Goal:** Add export button for current chat conversation
**Estimated Duration:** 1 hour

## Context

### What We're Building
Simple "Export Chat" button that downloads current conversation as TXT.

### From Phase 4 Learnings
- Session exporter already exists
- Need to expose download endpoint

## Tasks

### Task 1: Create Export Endpoint
**What:** Add `GET /api/chat/export` endpoint
**Why:** Backend support for current chat export
**Verification:** Endpoint returns downloadable TXT file

#### Sub-tasks:
- [ ] Create `GET /api/chat/export` endpoint
- [ ] Load current session
- [ ] Use session exporter
- [ ] Return as file attachment

**Time estimate:** 20 minutes

---

### Task 2: Add Export Button to UI
**What:** Add export button to chat interface
**Why:** User-facing export functionality
**Verification:** Button visible and functional

#### Sub-tasks:
- [ ] Add download icon + "Export" text
- [ ] Position in chat header
- [ ] Disable when no messages
- [ ] Show loading state during export
- [ ] Trigger download on click

**Note:** Frontend source may need rebuild if missing

**Time estimate:** 40 minutes

---

## Verification

### Phase Goal
Users can export current chat with one click.

### Success Criteria
1. [ ] Export button visible in chat UI
2. [ ] Button disabled when no messages
3. [ ] Clicking downloads TXT file
4. [ ] File contains all current messages

### Verification Commands
```bash
# Export current chat
curl -s -o chat_export.txt http://localhost:5000/api/chat/export
cat chat_export.txt
```

## Dependencies

| Dependency | Type | Phase |
|-----------|------|-------|
| Phase 4: Session Exporter | Required | Phase 4 |

## Modified Files

| File | Changes |
|------|---------|
| `web_app.py` | Add export endpoint |
| `frontend/` | Add export button |

## API Specification

### GET /api/chat/export
**Response Headers:**
```
Content-Type: text/plain
Content-Disposition: attachment; filename=chat_2024-01-15_103000.txt
```

**Response Body:** Plain text file content

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Empty export | MEDIUM | LOW | Disable button when no messages |
| Large file download | LOW | LOW | Async download, loading state |

## Next Phase

Phase 6: Frontend Polish
- UI/UX improvements
- Performance optimization
- Testing & QA

---

**Plan created:** 2026-04-02
**Ready for execution:** Yes (pending Phase 4 completion)
