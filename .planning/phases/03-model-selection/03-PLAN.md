# Phase 3: Model Selection in Settings - Plan

**Phase:** 3 - Model Selection in Settings
**Goal:** Add model selection for summary and tag generation
**Estimated Duration:** 1-2 hours

## Context

### What We're Building
This phase adds model selection to the settings page:
1. Summary model selection (for document summaries)
2. Tag model selection (for tag extraction)
3. Model availability display
4. Model download from settings

### From Phase 2 Learnings
- SummaryGenerator and TagExtractor accept model parameter
- Models can be configured independently
- Need to persist selections in Config

## Tasks

### Task 1: Update Config Class
**What:** Add `summary_model` and `tag_model` to Config
**Why:** Persist model selections
**Verification:** Config has new fields with defaults

#### Sub-tasks:
- [ ] Add `summary_model: str = "llama3.2:1b"` to Config
- [ ] Add `tag_model: str = "llama3.2:1b"` to Config
- [ ] Add validation in `__post_init__` (optional)

**Time estimate:** 15 minutes

---

### Task 2: Update Settings API
**What:** Modify `/api/settings` endpoint
**Why:** Expose new model settings
**Verification:** Settings endpoint returns new fields

#### Sub-tasks:
- [ ] Update GET to return `summary_model`, `tag_model`
- [ ] Update POST to accept `summary_model`, `tag_model`
- [ ] Validate selected models against available models
- [ ] Add error response if model not available

**Time estimate:** 30 minutes

---

### Task 3: Update Graph Modules
**What:** Wire new config values to generators
**Why:** Use configured models
**Verification:** Summary/tag use selected models

#### Sub-tasks:
- [ ] Update SummaryGenerator instantiation to use config.summary_model
- [ ] Update TagExtractor instantiation to use config.tag_model
- [ ] Add lazy initialization (don't create on import)

**Time estimate:** 15 minutes

---

### Task 4: Update Settings Frontend
**What:** Add model selection dropdowns
**Why:** UI for model selection
**Verification:** Dropdowns show and work

#### Sub-tasks:
- [ ] Add "Summary Model" dropdown with available models
- [ ] Add "Tag Model" dropdown with available models
- [ ] Show model status (downloaded/not downloaded)
- [ ] Persist selections on change

**Note:** Frontend source may need rebuild if missing

**Time estimate:** 30 minutes

---

## Verification

### Phase Goal
Users can select different models for chat, summary, and tag generation.

### Success Criteria
1. [ ] Settings page shows summary model dropdown
2. [ ] Settings page shows tag model dropdown
3. [ ] Model selections persist across sessions
4. [ ] Selected models are actually used

### Verification Commands
```bash
# Get current settings
curl -s http://localhost:5000/api/settings | python -m json.tool

# Update summary model
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"summary_model": "qwen2.5:3b"}'
```

## Dependencies

| Dependency | Type | Phase |
|-----------|------|-------|
| Phase 2: Graph Reimagined | Required | Phase 2 |

## Modified Files

| File | Changes |
|------|---------|
| `src/bitrag/core/config.py` | Add summary_model, tag_model |
| `web_app.py` | Update settings endpoint |
| `src/bitrag/core/summary_generator.py` | Use config model |
| `src/bitrag/core/tag_extractor.py` | Use config model |
| `frontend/` | Update settings UI |

## New API Fields

### GET /api/settings Response
```json
{
  "model": "llama3.2:1b",
  "summary_model": "llama3.2:1b",
  "tag_model": "qwen2.5:3b",
  "available_models": ["llama3.2:1b", "qwen2.5:3b", ...],
  ...
}
```

### POST /api/settings Request
```json
{
  "summary_model": "qwen2.5:3b",
  "tag_model": "llama3.2:1b"
}
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model not available | MEDIUM | LOW | Validate before save, show error |
| Model loading delay | MEDIUM | LOW | Show loading indicator |
| Settings save fails | LOW | MEDIUM | Show error toast, keep previous |

## Next Phase

Phase 4: Chat Persistence & Export
- Session management for chat history
- Export functionality

---

**Plan created:** 2026-04-02
**Ready for execution:** Yes (pending Phase 2 completion)
