---
phase: 07-pytermgui
plan: 03
type: execute
subsystem: tui-query
tags: [pytermgui, hybrid-search, rag]
dependency_graph:
  requires: [07-02]
  provides: [bitrag.tui.hybrid_search.TUIQueryEngine, bitrag.tui.hybrid_search.DocumentManager]
  affects: [src/bitrag/tui/main.py]
tech-stack:
  added: []
  patterns: [lazy-loading, async-pattern, callback-pattern]
key-files:
  created:
    - src/bitrag/tui/hybrid_search.py
decisions:
  - Used lazy imports for HybridSearch and config
  - Implemented async query with background thread
  - Used callback pattern for streaming responses
  - DocumentManager wraps DocumentIndexer with progress support
---

# Plan 07-03: RAG Integration with Hybrid Search - Summary

## Objective

Integrate Hybrid RAG (Vector + BM25) with the PyTermGUI application.

## What Was Done

### 1. TUIQueryEngine Class

TUI-specific query engine wrapper providing:

- **Hybrid Search Integration**: Uses existing `HybridSearch` from core
- **Query Method**: `query(question, callback, streaming)` returns dict with:
  - `response`: LLM response text
  - `sources`: List of retrieved documents
  - `model`: Model used
- **Streaming Support**: Callback for word-by-word streaming
- **Async Execution**: `query_async()` runs in background thread
- **State Management**: `is_loading` property for loading indicators
- **Alpha Control**: `set_alpha()` for hybrid search weight

### 2. DocumentManager Class

Document management wrapper for TUI:

- **Upload**: `upload_document(path, progress_callback)` with progress
- **List**: `list_documents()` returns indexed docs
- **Delete**: `delete_document(identifier)` by ID or filename

### 3. Architecture

- **Lazy Loading**: Components loaded on first access
- **Thread Safety**: Async queries run in daemon threads
- **Error Handling**: Graceful degradation if Ollama unavailable
- **Progress Callbacks**: UI can show upload/index progress

## Verification

- [x] TUIQueryEngine imports successfully
- [x] DocumentManager imports successfully
- [ ] Full integration - deferred to app runtime

## Notes

- The widgets from Plan 07-02 + TUIQueryEngine + DocumentManager
  can now be composed in main.py
- Streaming response is simulated word-by-word (true streaming 
  would require async generator from Ollama)
- Ready for chat interface implementation in Plan 07-04

## Commit

`9c09996` - feat(07-03): Add TUI hybrid search integration
