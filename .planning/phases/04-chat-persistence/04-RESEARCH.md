# Phase 4: Chat Persistence & Export - Research

**Researched:** 2026-04-02
**Domain:** Session management + File export
**Confidence:** HIGH

## Summary

Phase 4 adds persistent chat history with export functionality. Currently, sessions are stored as JSON in `sessions/<session_id>/session.json` but there's no UI to view or export previous sessions.

**Primary recommendation:** Create session management endpoints and UI for viewing, loading, and exporting chat sessions.

## Current State

### Session Storage (from Phase 1)
```
sessions/
└── default/
    └── session.json  # Contains: messages, title, timestamps
```

### Current Chat Message Structure
```python
@dataclass
class ChatMessageData:
    content: str       # Message text
    role: str         # "user" or "assistant"
    timestamp: str     # ISO format
    sources: list      # Retrieved documents
```

## Architecture Patterns

### Pattern: Session List Endpoint
**What:** Return list of sessions with metadata
**When to use:** Display session history
**Example:**
```python
@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    sessions = []
    for session_dir in Path(sessions_dir).iterdir():
        if session_dir.is_dir():
            meta = load_session_metadata(session_dir)
            sessions.append({
                "id": session_dir.name,
                "title": meta.get("title", "Untitled"),
                "message_count": meta.get("message_count", 0),
                "created_at": meta.get("created_at"),
                "updated_at": meta.get("updated_at"),
            })
    return jsonify({"sessions": sessions})
```

### Pattern: Session Export
**What:** Generate TXT file from session
**When to use:** User wants to save conversation
**Example:**
```python
def export_session_as_text(session_id: str) -> str:
    session = load_session(session_id)
    
    lines = [
        "=== BitRAG Chat Export ===",
        f"Session: {session_id}",
        f"Date: {session['created_at']}",
        f"Model: {session.get('model', 'unknown')}",
        "",
        "--- Chat History ---",
        "",
    ]
    
    for msg in session["messages"]:
        role = msg["role"].upper()
        timestamp = msg.get("timestamp", "")
        content = msg["content"]
        
        lines.append(f"[{role}] {timestamp}")
        lines.append(content)
        if msg.get("sources"):
            lines.append(f"Sources: {', '.join(msg['sources'])}")
        lines.append("")
    
    return "\n".join(lines)
```

### Pattern: Session Management Actions
**What:** CRUD operations for sessions
**When to use:** Full session management
**Example:**
```python
# Rename
@app.route("/api/sessions/<id>", methods=["PATCH"])
def update_session(id):
    data = request.get_json()
    if "title" in data:
        rename_session(id, data["title"])
    
# Delete
@app.route("/api/sessions/<id>", methods=["DELETE"])
def delete_session(id):
    delete_session_files(id)
    return jsonify({"success": True})
```

## Common Pitfalls

### Pitfall 1: Large Session Files
**What goes wrong:** Session JSON grows large with many messages
**Why it happens:** Every message stored indefinitely
**How to avoid:** Pagination, lazy loading, or truncation
**Warning signs:** Slow load times, large file sizes

### Pitfall 2: Session ID in URL
**What goes wrong:** Session IDs exposed in URLs could be guessed
**Why it happens:** Simple session_id naming
**How to avoid:** Use UUIDs, add access control
**Warning signs:** Security audit flags

### Pitfall 3: Concurrent Session Access
**What goes wrong:** Multiple tabs modifying same session
**Why it happens:** No locking mechanism
**How to avoid:** Add last_modified timestamp, warn on conflicts
**Warning signs:** Lost messages, race conditions

## Code Examples

### Session File Structure
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
    },
    {
      "content": "RAG stands for...",
      "role": "assistant", 
      "timestamp": "2024-01-15T10:30:05Z",
      "sources": ["doc1.pdf", "doc2.pdf"]
    }
  ]
}
```

### Export TXT Format
```
=== BitRAG Chat Export ===
Session: default
Date: 2024-01-15
Model: llama3.2:1b

--- Chat History ---

[USER] 2024-01-15T10:30:00Z
What is RAG?

[ASSISTANT] 2024-01-15T10:30:05Z
RAG stands for Retrieval-Augmented Generation, a technique...

Sources: doc1.pdf, doc2.pdf

---
```

## Open Questions

1. **Should sessions auto-title based on first message?**
   - What we know: Current system has "title" field
   - What's unclear: How to generate meaningful titles
   - Recommendation: Use first user message as default title

2. **How many sessions to keep?**
   - What we know: No limit currently
   - What's unclear: Storage concerns
   - Recommendation: No limit, let user manage

## Sources

### Primary (HIGH confidence)
- src/bitrag/tui/chat.py - ChatSession class (existing persistence)
- web_app.py - Current session handling

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Well-understood
- Architecture: HIGH - Standard CRUD patterns
- Pitfalls: MEDIUM - Common web app issues

**Research date:** 2026-04-02
**Valid until:** 90 days
