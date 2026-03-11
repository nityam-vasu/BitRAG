# Project State

## Project Overview
- **Name**: BitRAG - 1-Bit LLM RAG System
- **Type**: CLI-first RAG application with PyTermGUI terminal UI
- **Goal**: Build a RAG system using 1-bit LLMs for chat with user-uploaded PDFs

## Current Position
- **Phase**: 07 (Phase 01 - PyTermGUI Setup)
- **Plan**: 07-01 (PyTermGUI Setup & Dependencies)
- **Last Updated**: 2026-03-11
- **Branch**: PyTermGUI

## Tech Stack Decisions

### LLM (Locked - Using Ollama)
- **Runtime**: Ollama (for smaller, efficient models)
- **Primary Model**: gemma3:4b (currently available)
- **Smaller Options**:
  - llama3.2:1b (1GB, minimal GPU)
  - qwen2.5:0.5b (very small)
  - phi3:3.8b (Microsoft)
- **Reason**: Smaller models work without high GPU requirements

### Indexing (Locked)
- **Library**: LlamaIndex
- **Reason**: User explicitly requested LlamaIndex for document indexing

### Vector Store
- **Option**: ChromaDB (via LlamaIndex)
- **Alternative**: SQLite-VSS (lighter weight)

### CLI Framework
- **Option**: Click (existing CLI)
- **Reason**: Simple CLI first, then PyTermGUI terminal UI

### Terminal UI Framework (New - Phase 07)
- **Framework**: PyTermGUI
- **Reference**: Existing CLI functionality
- **Hybrid Search**: rank_bm25 + ChromaDB
- **Fusion**: Reciprocal Rank Fusion (RRF)
- **Default Alpha**: 0.5 (balanced vector/keyword)

## User Decisions

### Locked Decisions
1. Use 1-bit LLM as primary model
2. Use LlamaIndex for document indexing
3. CLI first, then PyTermGUI terminal UI
4. No Django frontend (removed)
5. No GTK4 desktop GUI (removed)

### Deferred Ideas
1. Django frontend (removed - using PyTermGUI instead)
2. GTK4 desktop GUI (removed - using PyTermGUI instead)
3. Multiple document formats beyond PDF (TXT, DOCX - deferred)
4. Docker containerization (optional, deferred)

## Pending Tasks
- [x] Phase 01: Research 1-bit LLM options and setup
- [x] Phase 02: Set up project structure and CLI
- [x] Phase 03: Implement document upload and indexing with LlamaIndex
- [x] Phase 04: Implement RAG query pipeline (Ollama)
- [x] Phase 05: Enhance CLI (opencode-style with /commands)
- [x] Phase 06: Hybrid RAG Research (from 07-01)
- [ ] Phase 07: PyTermGUI Terminal Application
  - [ ] 07-01: PyTermGUI Setup & Dependencies
  - [ ] 07-02: Core TUI Components
  - [ ] 07-03: RAG Integration with Hybrid Search
  - [ ] 07-04: Chat Interface & Message Handling
  - [ ] 07-05: Document Management UI
  - [ ] 07-06: Settings & Configuration
  - [ ] 07-07: Polish & Production Ready

## Blockers
- None

## Key Decisions Made
- Used pypdf instead of deprecated PyPDFReader from llama_index
- Session-based ChromaDB isolation for multi-user support
- Progress callback pattern for real-time feedback

## Notes
- Previous RAG project exists but uses different stack (FastAPI + Vue + ChromaDB)
- This is a fresh start with different technology choices per user request
- Phase 03 completed: PDF upload, parsing, and vector indexing with session isolation
- Session management: create/list/delete sessions
- Indexing: PDF → text → chunks → embeddings → ChromaDB
- CLI commands: upload, list, delete (with session ID)
- Phase 04 completed: RAG query pipeline with Ollama
- Phase 05 completed: CLI enhancement + smaller models
- **Working Models**:
  - qwen2.5:0.5b (397MB) ✓ Tested
  - gemma3:4b (3.3GB) ✓ Tested
  - llama3.2:1b requires more GPU memory
- Phase 06: Hybrid RAG Research complete
  - Hybrid search combines vector + BM25 keyword search
  - Expected 20-35% retrieval accuracy improvement
  - Implementation: Manual rank_bm25 + ChromaDB
  - Fusion: Reciprocal Rank Fusion (RRF)
  - Alpha parameter default: 0.5 (balanced)
- **Branch Change**: Switched from GTK4 to PyTermGUI for terminal-based UI
- All GTK4 references removed from planning
- All Django references removed from planning
- All Docker references moved to optional/deferred
