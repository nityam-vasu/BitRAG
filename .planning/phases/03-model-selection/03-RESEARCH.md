# Phase 3: Model Selection in Settings - Research

**Researched:** 2026-04-02
**Domain:** LLM configuration + Settings UI
**Confidence:** HIGH

## Summary

Phase 3 adds model selection to the settings page, allowing users to choose which model generates summaries and tags (separate from chat model). Currently, all LLM operations use the same `current_model` setting.

**Primary recommendation:** Add `summary_model` and `tag_model` to Config, expose via settings API, and add dropdowns in frontend.

## Standard Stack

### Current Settings
| Setting | Current | Purpose |
|---------|---------|---------|
| model | llama3.2:1b | Chat/query LLM |
| ollamaPort | 11434 | Ollama server port |
| hybridMode | false | Hybrid search enable |
| dualMode | false | Dual model mode |

### Proposed Settings
| Setting | Default | Purpose |
|---------|---------|---------|
| model | llama3.2:1b | Chat/query LLM |
| summary_model | llama3.2:1b | Summary generation |
| tag_model | llama3.2:1b | Tag extraction |

## Architecture Patterns

### Pattern: Model Registry
**What:** Centralized model availability tracking
**When to use:** Multiple models in use
**Example:**
```python
# In web_app.py
available_models = []  # Cached from Ollama

@app.route("/api/models", methods=["GET"])
def get_models():
    global available_models
    if not available_models:
        available_models = ollama_service.list_models()
    return jsonify({"models": available_models})
```

### Pattern: Model Fallback
**What:** Use primary model if selected model unavailable
**When to use:** User selects deleted model
**Example:**
```python
def get_summary_model():
    model = config.summary_model
    if model not in available_models:
        return available_models[0]  # Fallback to first available
    return model
```

## Common Pitfalls

### Pitfall 1: Model Not Downloaded
**What goes wrong:** User selects model that doesn't exist
**Why it happens:** Models can be deleted from Ollama
**How to avoid:** Validate selection against available models list
**Warning signs:** LLM calls fail with model not found error

### Pitfall 2: Model Switching Requires Reinit
**What goes wrong:** Changing model doesn't take effect immediately
**Why it happens:** Query engine initialized once
**How to avoid:** Reinitialize components on model change
**Warning signs:** Old model still used after settings update

### Pitfall 3: Model Loading Delay
**What goes wrong:** First request after model switch is slow
**Why it happens:** Ollama loads model on first use
**How to avoid:** Show loading indicator, provide feedback
**Warning signs:** UI appears frozen during first request

## Code Examples

### Settings Update Flow (web_app.py)
```python
@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.get_json()
    
    # Update model (existing)
    if "model" in data:
        current_model = data["model"]
        # Reinitialize query engine
    
    # NEW: Update summary model
    if "summary_model" in data:
        config.summary_model = data["summary_model"]
        # No reinit needed (lazy loading)
    
    # NEW: Update tag model  
    if "tag_model" in data:
        config.tag_model = data["tag_model"]
        # No reinit needed
    
    return jsonify({"success": True})
```

### Settings Response (web_app.py)
```python
@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify({
        "model": current_model,
        "summary_model": config.summary_model,  # NEW
        "tag_model": config.tag_model,  # NEW
        "ollamaPort": ollama_port,
        "hybridMode": hybrid_mode,
        "available_models": available_models,  # NEW
        "documentCount": indexer.get_document_count(),
        "ollamaStatus": ollama_status,
    })
```

## Open Questions

1. **Should summary/tag models auto-select based on size?**
   - What we know: Small models (1-3B) are faster for simple tasks
   - What's unclear: User preference for quality vs speed
   - Recommendation: Default to same model, allow customization

2. **How to handle model download from settings?**
   - What we know: `/api/models/download` exists
   - What's unclear: UX for download status
   - Recommendation: Show download progress, disable selection during download

## Sources

### Primary (HIGH confidence)
- web_app.py lines 585-692 - Current settings implementation
- web_app.py lines 514-582 - Model management endpoints

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Well-understood
- Architecture: HIGH - Simple addition to existing pattern
- Pitfalls: MEDIUM - Common issues identified

**Research date:** 2026-04-02
**Valid until:** 90 days
