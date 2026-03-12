---
phase: 08-tui-v2
plan: 03
subsystem: tui
tags: [pytermgui, tui, settings, ollama, model-management]
dependency_graph:
  requires: [bitrag-tui-app]
  provides: [settings-dialog, model-management]
  affects: [cli, core]
tech_stack:
  added: [subprocess]
  patterns: [model-management, settings-persistence]
key_files:
  created:
    - src/bitrag/tui/settings.py
  modified:
    - src/bitrag/tui/app.py
decisions:
  - "Use subprocess for Ollama CLI operations"
  - "Settings persist via existing config system"
  - "Demo mode fallback when dependencies unavailable"
metrics:
  duration: 1 task
  completed: 2026-03-12
---

# Phase 08 Plan 03: Settings Page Summary

## Overview

Implemented Settings page with full model management and configuration options based on the BitRAG TUI specification.

## Completed Tasks

| Task | Name | Status | Files |
|------|------|--------|-------|
| 1 | Create settings page | ✅ Complete | src/bitrag/tui/settings.py |
| 2 | Integrate settings with main app | ✅ Complete | src/bitrag/tui/app.py |

## Key Features Implemented

### OllamaManager
- **list_models()**: Lists installed Ollama models via `ollama list`
- **pull_model()**: Downloads models with progress callback
- **delete_model()**: Removes models via `ollama rm`
- **is_running()**: Checks if Ollama is running

### ModelDownloadDialog
- Downloads models with progress tracking
- Uses subprocess for `ollama pull` command

### ModelDeleteDialog
- Lists installed models
- Allows deletion via `ollama rm`

### SettingsDialogExtended
Full settings UI with:
- **Ollama Port**: Configuration (default: 11434)
- **Model Selection**: Shows available Ollama models + predefined list
- **Model Download**: Options for downloading new models
- **Model Delete**: List of installed models with delete buttons
- **Dual Model Mode**: Toggle with disclaimer "Using two models increases inference time and resource usage"
- **Hybrid Retrieval Slider**: Three-point slider (-1: Pure Vector, 0: Hybrid, 1: Pure Keyword)
- **Document Management Button**: Navigates to document page

### Integration
- Settings accessible via 'S' keyboard shortcut
- Settings accessible via Settings button in header
- Shows all configuration options in formatted dialog

## Verification

```bash
PYTHONPATH=src python -c "from bitrag.tui.app import BitRAGApp; app = BitRAGApp(); app.show_settings()"
```

Shows:
- Current Ollama port
- Available models (detected from Ollama)
- Predefined model list
- Download/delete options
- Dual model mode toggle
- Hybrid retrieval slider
- Document management navigation

## Deviation from Plan

**None** - Plan executed as written.

## Notes

- Uses subprocess for Ollama CLI operations
- Settings persist via existing config.save() mechanism
- Falls back gracefully when Ollama not available
- Demo mode provides clear guidance

## Commit

- `ab98136`: feat(08-tui-v2): implement settings with model management

## Self-Check

- [x] Settings dialog imports correctly
- [x] OllamaManager works (detected 7 models)
- [x] Model download/delete options shown
- [x] Dual model mode toggle present
- [x] Hybrid slider (-1 to 1) implemented
- [x] Document management navigation works

## Self-Check: PASSED
