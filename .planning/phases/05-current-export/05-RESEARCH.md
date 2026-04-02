# Phase 5: Current Chat TXT Export - Research

**Researched:** 2026-04-02
**Domain:** UI button + file download
**Confidence:** HIGH

## Summary

Phase 5 adds a simple "Export Chat" button to the chat page for exporting the current conversation. This is simpler than Phase 4's session management.

**Primary recommendation:** Reuse the session exporter from Phase 4, add download endpoint.

## Architecture Patterns

### Pattern: File Download Endpoint
**What:** Return file as attachment
**When to use:** User wants to download content
**Example:**
```python
from flask import make_response
import io

@app.route("/api/chat/export", methods=["GET"])
def export_current_chat():
    session = load_current_session()
    content = export_session_as_text(session)
    
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = f"attachment; filename=chat_export_{session['id']}.txt"
    
    return response
```

### Pattern: Frontend Download Trigger
**What:** Trigger file download from API response
**When to use:** Download button in UI
**Example:**
```javascript
async function exportChat() {
  const response = await fetch("/api/chat/export");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement("a");
  a.href = url;
  a.download = `chat_${Date.now()}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

## Common Pitfalls

### Pitfall 1: Empty Chat Export
**What goes wrong:** Export button exports empty file
**Why it happens:** No messages in current session
**How to avoid:** Disable button when no messages, show toast
**Warning signs:** User complaints about empty exports

### Pitfall 2: Large Download Blocking UI
**What goes wrong:** Download takes time, UI appears frozen
**Why it happens:** Synchronous fetch
**How to avoid:** Show loading state, use async download
**Warning signs:** UI unresponsive during download

## Open Questions

1. **Should filename include timestamp?**
   - Recommendation: Yes, `chat_2024-01-15_103000.txt`

2. **Where to place export button?**
   - Recommendation: Top-right of chat area, icon + text

## Sources

### Primary (HIGH confidence)
- session_exporter.py (Phase 4 output)
- web_app.py - Existing chat endpoints

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Simple feature
- Architecture: HIGH - Standard download pattern
- Pitfalls: LOW - Well-understood

**Research date:** 2026-04-02
**Valid until:** 90 days
