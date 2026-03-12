# BitRAG Project Roadmap

## Project Overview
- **Name**: BitRAG - 1-Bit LLM RAG System
- **Description**: RAG software using 1-bit LLMs for chatting with user-uploaded PDFs with Hybrid Search
- **Tech Stack**: LlamaIndex (indexing), 1-bit LLM via Ollama, Python CLI, PyTermGUI Terminal UI, Hybrid RAG (Vector + BM25)
- **Current Phase**: Phase 08 - PyTermGUI TUI v2 Implementation

---

## Phase 01: Research & Foundation
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Research 1-bit LLM options, set up development environment, and establish project structure.

### Plans
- [x] 01-01-PLAN.md — Research 1-bit LLM options and setup

---

## Phase 02: Project Setup & Docker Foundation
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Create Python project structure with CLI skeleton, dependencies, and Docker setup.

### Plans
- [x] 02-01-PLAN.md — Project structure, requirements, CLI skeleton, Dockerfile, Docker Compose

---

## Phase 03: Document Indexing with LlamaIndex
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Implement PDF upload, parsing, and vector indexing using LlamaIndex.

### Plans
- [x] 03-01-PLAN.md — PDF indexing with LlamaIndex and ChromaDB

---

## Phase 04: RAG Query Pipeline
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Implement the complete RAG pipeline: retrieve relevant chunks, generate response with 1-bit LLM.

### Plans
- [x] 04-01-PLAN.md — RAG query with Ollama 1-bit LLM

---

## Phase 05: CLI Refinement
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Polish CLI with better UX, error handling, and documentation.

### Plans
- [x] 05-01-PLAN.md — CLI polish, error handling, configuration

---

## Phase 06: Hybrid RAG Research
**Status**: Completed | **Plans**: 1 plan(s)

### Goal
Research Hybrid RAG (Vector + Keyword search) integration.

### Plans
- [x] 06-01-PLAN.md — Hybrid RAG Research

---

## Phase 07: PyTermGUI Terminal Application
**Status**: Planning complete | **Plans**: 7 plan(s)

### Goal
Build PyTermGUI terminal application with Hybrid RAG (Vector + Keyword search).

### Plans
- [x] 07-01-PLAN.md — PyTermGUI Setup & Dependencies
- [x] 07-02-PLAN.md — Core TUI Components
- [x] 07-03-PLAN.md — RAG Integration with Hybrid Search
- [x] 07-04-PLAN.md — Chat Interface & Message Handling
- [x] 07-05-PLAN.md — Document Management UI
- [x] 07-06-PLAN.md — Settings & Configuration
- [x] 07-07-PLAN.md — Polish & Production Ready

---

## Phase 08: PyTermGUI TUI v2 Implementation
**Status**: Planning complete | **Plans**: 5 plan(s)

### Goal
Implement full-featured PyTermGUI TUI based on the detailed specification (splash screen, main window, settings, document management, chat with streaming).

### Plans
- [x] 08-01-PLAN.md — Splash Screen & Main Window Layout
- [x] 08-02-PLAN.md — Chat Interface with Streaming & Sources
- [x] 08-03-PLAN.md — Settings Page with Model Management
- [x] 08-04-PLAN.md — Document Management Page
- [x] 08-05-PLAN.md — Navigation, Polish & Entry Point

---

## Phase 09: Optional Docker Containerization
**Status**: Deferred | **Plans**: 0 plan(s)

### Goal
Containerize the application with Docker (optional, for advanced users).

### Plans
- [ ] (Deferred) Docker setup for advanced deployment

---

## Dependencies

### Phase Dependencies
- Phase 01 → Phase 02 (research feeds setup)
- Phase 02 → Phase 03 (project ready)
- Phase 03 → Phase 04 (indexing needed before queries)
- Phase 04 → Phase 05 (refine working system)
- Phase 05 → Phase 06 (CLI verified, proceed to Hybrid RAG)
- Phase 06 → Phase 07 (Research complete, proceed to PyTermGUI)
- Phase 07 → Phase 08 (PyTermGUI v1 complete, proceed to v2 spec)
- Phase 08 → Phase 09 (TUI v2 ready, optional Docker)

### External Dependencies
- Ollama for LLM runtime
- 1-bit quantized models (GGUF format)
- LlamaIndex for RAG
- ChromaDB for vector storage
- rank_bm25 for keyword search
- PyTermGUI for terminal UI
- PyYAML for configuration

---

## Success Criteria

### Phase 01 (Research)
- [x] Research document created
- [x] Technology choices validated

### Phase 02 (Setup)
- [x] CLI skeleton runs
- [x] Dependencies install correctly
- [x] Docker builds successfully
- [x] Docker Compose starts
- [x] Data persists in volumes

### Phase 03 (Indexing)
- [x] PDF files can be uploaded
- [x] Documents are indexed and searchable
- [x] Can list and delete documents

### Phase 04 (RAG Pipeline)
- [x] Can query indexed documents
- [x] 1-bit LLM generates responses
- [x] Streaming responses work

### Phase 05 (CLI Refinement)
- [x] CLI is user-friendly
- [x] Error handling is robust
- [x] Documentation is complete

### Phase 06 (Hybrid RAG Research)
- [x] Hybrid RAG research complete

### Phase 07 (PyTermGUI Terminal Application)
- [x] PyTermGUI app launches
- [x] Core TUI widgets implemented
- [x] Hybrid search combines vector + keyword search
- [x] Chat interface works with streaming responses
- [x] Document management UI functional
- [x] Settings dialog works
- [x] Application packaged and production-ready

### Phase 08 (PyTermGUI TUI v2)
- [ ] Splash screen with ASCII art on startup
- [ ] Main window layout (header, chat, chat bar, footer)
- [ ] Chat interface with thinking box, model output, sources
- [ ] Streaming responses display progressively
- [ ] Settings page with model management (download/delete)
- [ ] Dual model mode with disclaimer
- [ ] Hybrid retrieval slider (vector/keyword balance)
- [ ] Document management (list, upload, delete)
- [ ] Keyboard shortcuts (C, S, U, Q)
- [ ] System resource display in header
- [ ] Production-ready entry point
