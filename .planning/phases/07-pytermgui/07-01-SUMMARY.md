---
phase: 07-pytermgui
plan: 01
type: execute
subsystem: tui
tags: [pytermgui, tui, ui]
dependency_graph:
  requires: []
  provides: [bitrag.tui.BitRAGApplication]
  affects: [src/bitrag/cli/main.py]
tech-stack:
  added: [pytermgui>=5.0.0, rank-bm25>=0.2.0]
  patterns: [lazy-imports, mvc-pattern]
key-files:
  created:
    - src/bitrag/tui/__init__.py
    - src/bitrag/tui/main.py
  modified:
    - pyproject.toml
decisions:
  - Used lazy imports for core modules to avoid import errors during setup
  - Used PyTermGUI v7 API (not ptg alias, direct pytermgui import)
  - Implemented lazy property pattern for config and indexer
---

# Plan 07-01: PyTermGUI Setup & Dependencies - Summary

## Objective

Set up PyTermGUI dependencies and create initial TUI application structure.

## What Was Done

### 1. Dependencies Added

Added to `pyproject.toml`:
- `pytermgui>=5.0.0` - Terminal UI library
- `rank-bm25>=0.2.0` - BM25 keyword search for hybrid RAG

### 2. TUI Package Structure

Created `src/bitrag/tui/` package:
- `__init__.py` - Package initialization, exports BitRAGApplication
- `main.py` - Main application class

### 3. BitRAGApplication Class

Created basic PyTermGUI application with:
- **Header**: Logo and system title
- **Sidebar**: Navigation buttons (Chat, Documents, Settings, New Session, Exit)
- **Main Content**: Three views (Chat, Documents, Settings)
- **Footer**: Keyboard shortcuts

### 4. Architecture

- **Lazy Imports**: Core modules (DocumentIndexer, get_config) are imported lazily
- **Lazy Properties**: config and indexer are created on-demand
- **Event Handlers**: Button click handlers for navigation
- **View Switching**: Simple state machine for view management

## Verification

- [x] PyTermGUI imports successfully
- [x] Basic widgets (Button, Label, Window) create without errors
- [x] main.py syntax is valid Python
- [ ] Full app run - deferred (requires full dependency install)

## Notes

- This is a **skeleton only** - actual functionality will be added in subsequent plans:
  - Plan 07-02: Core TUI Components (ChatDisplay, InputWidget, Sidebar)
  - Plan 07-03: RAG Integration with Hybrid Search
  - Plan 07-04: Chat Interface & Message Handling
  - Plan 07-05: Document Management UI
  - Plan 07-06: Settings & Configuration
  - Plan 07-07: Polish & Production Ready
- The application uses PyTermGUI v7 API
- Some LSP errors shown are false positives (dynamic module loading)

## Commit

`fae2ba2` - feat(07-01): Add PyTermGUI setup and basic TUI skeleton
