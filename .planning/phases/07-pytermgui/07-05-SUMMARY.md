---
phase: 07-pytermgui
plan: 05
type: execute
subsystem: tui-documents
tags: [pytermgui, documents, upload]
dependency_graph:
  requires: [07-04]
  provides: [bitrag.tui.documents.DocumentManagerUI]
  affects: [src/bitrag/tui/main.py]
tech-stack:
  added: []
  patterns: [callback-pattern, file-browser]
key-files:
  created:
    - src/bitrag/tui/documents.py
decisions:
  - Searches common directories: Documents, Downloads, Desktop, PDFs
  - Supports PDF, TXT, DOCX file types
  - Uses callbacks for UI integration
---

# Plan 07-05: Document Management UI - Summary

## Objective

Implement document management UI for uploading, listing, and deleting documents.

## What Was Done

### DocumentManagerUI Class

Comprehensive document management for TUI:

- **Browse PDFs**: `browse_pdfs(search_dirs)` finds PDFs in:
  - ~/Documents
  - ~/Downloads
  - ~/Desktop
  - ~/Documents/PDFs

- **Upload**: `upload_document(path, progress_callback)`
  - Validates file exists and type
  - Indexes with DocumentIndexer
  - Returns DocumentInfo on success

- **List**: `list_documents()` 
  - Returns list of DocumentInfo objects
  - Cached internally

- **Get Details**: `get_document(identifier)`
  - Full document info including chunks

- **Delete**: `delete_document(identifier)`
  - By filename or ID

- **Format**: `format_document_list()`
  - Pretty-printed list for display

### DocumentInfo Dataclass

```python
@dataclass
class DocumentInfo:
    id: str
    file_name: str
    indexed_at: str
    total_chunks: int
    source: str = ""
```

## Verification

- [x] DocumentManagerUI imports
- [x] browse_pdfs() finds files
- [x] Works with callbacks

## Notes

- Combined with hybrid_search.py DocumentManager
- Ready for UI integration

## Commit

`fc30b13` - feat(07-05): Add document management UI
