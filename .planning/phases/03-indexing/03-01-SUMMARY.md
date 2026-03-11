---
phase: 03-indexing
plan: 01
subsystem: indexing
tags: [pdf-upload, chromadb, llama-index, session-management]
dependency_graph:
  requires:
    - phase-02-setup (CLI structure)
  provides:
    - DocumentIndexer class
    - Session-based indexing
    - CLI upload/list/delete commands
  affects:
    - Phase 04 (RAG query pipeline)
tech_stack:
  added:
    - llama-index (document indexing)
    - chromadb (vector storage)
    - pypdf (PDF parsing)
    - reportlab (test PDF generation)
  patterns:
    - Session-based document isolation
    - Progress bar for indexing stages
    - Persistent ChromaDB storage per session
key_files:
  created:
    - src/bitrag/core/indexer.py (Document indexer with ChromaDB)
    - src/bitrag/core/config.py (Configuration with session paths)
    - scripts/create_session.py (Session management CLI)
    - scripts/activate_session.py (Upload + index with progress)
    - tests/test_indexing.py (End-to-end indexing tests)
  modified:
    - src/bitrag/cli/main.py (Added upload/list/delete commands)
decisions:
  - "Used pypdf instead of deprecated PyPDFReader from llama_index"
  - "Session-based ChromaDB isolation for multi-user support"
  - "Progress callback pattern for real-time feedback"
metrics:
  duration: "~2 minutes (tests)"
  completed: "2026-02-14"
  test_count: 5
  test_passed: 5
---

# Phase 03 Plan 01: PDF Upload and Indexing Summary

## One-liner

PDF upload and vector indexing pipeline with session isolation using LlamaIndex and ChromaDB.

## Objective

Implemented PDF upload, parsing, and vector indexing using LlamaIndex with ChromaDB, enabling document storage per session with real-time progress feedback.

## Key Achievements

1. **Session-based document management** - Each session has isolated uploads/, index/, and chroma_db/ directories
2. **PDF indexing pipeline** - Complete flow from PDF upload to ChromaDB vector storage
3. **Real-time progress bar** - 5-stage progress tracking (Loading → Extracting → Chunking → Embedding → Storing)
4. **CLI integration** - `bitrag upload`, `bitrag list`, `bitrag delete` commands fully functional
5. **Test coverage** - 5/5 tests passing for indexing functionality

## Verification

- [x] Configuration loads correctly (`Config` dataclass)
- [x] PDF files can be indexed (via `DocumentIndexer.index_document()`)
- [x] Documents persist in ChromaDB (PersistentClient per session)
- [x] List command shows indexed documents (with metadata)
- [x] Delete removes documents from index

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed deprecated PyPDFReader import**
- **Found during:** Task 4 verification
- **Issue:** `from llama_index.readers.file import PyPDFReader` failed - the class was moved/removed in newer llama_index versions
- **Fix:** Replaced with direct pypdf usage: `from pypdf import PdfReader`
- **Files modified:** `src/bitrag/core/indexer.py`
- **Commit:** See git log

**2. [Rule 2 - Feature] Added session index directory**
- **Found during:** Review of config
- **Issue:** Config didn't have get_session_index_dir() method, create_session.py didn't create index/ directory
- **Fix:** Added `get_session_index_dir()` to config.py and updated create_session.py to create the directory
- **Files modified:** `src/bitrag/core/config.py`, `scripts/create_session.py`

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/bitrag/core/indexer.py` | Document indexer with PDF loading, chunking, embedding, ChromaDB storage |
| `src/bitrag/core/config.py` | Configuration dataclass with session path methods |
| `scripts/create_session.py` | Create/list/delete sessions |
| `scripts/activate_session.py` | Upload PDF and index with progress bar |
| `src/bitrag/cli/main.py` | CLI commands: upload, list, delete |
| `tests/test_indexing.py` | E2E tests for indexing |

## Usage Examples

```bash
# Create a session
python scripts/create_session.py --name my_project

# Upload and index a PDF
python scripts/activate_session.py --session my_project_20260214 --upload document.pdf --index

# Or use CLI
bitrag upload document.pdf --session my_project_20260214
bitrag list --session my_project_20260214
bitrag delete <doc_id> --session my_project_20260214
```

## Self-Check

- [x] Created files exist
- [x] All tests pass (5/5)
- [x] CLI commands work (`bitrag upload --help`, etc.)
- [x] Scripts work (`python scripts/create_session.py --help`)
