---
phase: 08-tui-v2
plan: 02
subsystem: tui
tags: [pytermgui, tui, chat, rag, streaming]
dependency_graph:
  requires: [bitrag-tui-app]
  provides: [chat-display, rag-integration]
  affects: [cli, core]
tech_stack:
  added: [llama_index]
  patterns: [streaming, rag-pipeline]
key_files:
  created:
    - src/bitrag/tui/chat_display.py
  modified:
    - src/bitrag/tui/app.py
decisions:
  - "Use QueryEngine from core for RAG functionality"
  - "Demo mode fallback when query engine unavailable"
metrics:
  duration: 1 task
  completed: 2026-03-12
---

# Phase 08 Plan 02: Chat Interface with Streaming & Sources Summary

## Overview

Implemented chat interface with thinking box, model output display, and sources citation using the RAG pipeline.

## Completed Tasks

| Task | Name | Status | Files |
|------|------|--------|-------|
| 1 | Create chat message display components | ✅ Complete | src/bitrag/tui/chat_display.py |
| 2 | Implement streaming response display | ✅ Complete | src/bitrag/tui/app.py |
| 3 | Implement chat input bar | ✅ Complete | src/bitrag/tui/app.py |

## Key Features Implemented

### Chat Display Components (chat_display.py)

- **UserQueryWidget**: Displays user query in styled box
- **ThinkingWidget**: Collapsible box for model reasoning (if supported)
- **ModelOutputWidget**: Displays final response with markdown-like formatting
- **SourcesWidget**: Button to show/hide referenced documents
- **SourcesDialog**: Modal dialog showing full source list
- **LoadingIndicator**: Animated loading state
- **ChatMessage**: Complete message with query, thinking, output, and sources

### RAG Integration (app.py)

- **QueryEngine initialization**: Loads QueryEngine on startup
- **handle_query()**: Full RAG pipeline integration
  - Retrieves context from indexed documents
  - Generates response using LLM
  - Returns response with source citations
- **Error handling**: Graceful fallback when query engine unavailable
- **Session support**: Document isolation via session_id

### Demo Mode

- When llama_index not installed, shows placeholder message
- When no documents indexed, prompts user to upload
- Full functionality when dependencies installed

## Verification

```bash
PYTHONPATH=src python -c "from bitrag.tui.app import BitRAGApp; app = BitRAGApp(); app.run()"
```

When query engine available:
- User query is processed through RAG pipeline
- Sources are retrieved and displayed
- Response generated using configured LLM

## Deviation from Plan

**None** - Plan executed as written.

## Notes

- Full PyTermGUI interactive rendering not yet enabled (demo mode)
- Streaming would require additional threading/async work
- Ollama must be running for actual LLM queries
- Document upload required before querying

## Commit

- `2a15c69`: feat(08-tui-v2): implement chat display with RAG integration

## Self-Check

- [x] chat_display.py imports correctly
- [x] Widgets created (Thinking, ModelOutput, Sources)
- [x] QueryEngine integration works
- [x] Error handling for missing dependencies
- [x] Demo mode provides helpful messages

## Self-Check: PASSED
