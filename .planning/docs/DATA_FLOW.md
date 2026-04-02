# BitRAG Data Flow Documentation

**Document:** DATA_FLOW.md
**Version:** 1.0
**Date:** 2026-04-02

---

## Overview

This document maps how data moves through the BitRAG system, from document upload to query response.

---

## 1. Document Upload Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     DOCUMENT UPLOAD & INDEXING FLOW                      │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐         ┌──────────────┐         ┌──────────────────┐
  │ Frontend │         │  web_app.py  │         │  DocumentIndexer │
  │   Form   │────────▶│ upload_doc() │────────▶│ index_document() │
  └──────────┘         └──────┬───────┘         └────────┬─────────┘
                               │                           │
                               │ File (multipart)          │
                               ▼                           │
                        ┌──────────────┐                    │
                        │  temp_path   │                    │
                        │  (saved)     │                    │
                        └──────┬───────┘                    │
                               │                           │
                               ▼                           ▼
                        ┌──────────────────────────────────────────┐
                        │              PDF Processing              │
                        │  ┌────────────────────────────────────┐ │
                        │  │ 1. Read PDF (pypdf.PdfReader)      │ │
                        │  │ 2. Extract text from each page      │ │
                        │  │ 3. Concatenate all text            │ │
                        │  │ 4. Create Document object          │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Chunking                     │
                        │  ┌────────────────────────────────────┐ │
                        │  │ SentenceSplitter                   │ │
                        │  │ - chunk_size: 512                 │ │
                        │  │ - chunk_overlap: 50               │ │
                        │  │ → Creates list of Node objects    │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │           Embedding Generation             │
                        │  ┌────────────────────────────────────┐ │
                        │  │ HuggingFaceEmbedding               │ │
                        │  │ Model: all-MiniLM-L6-v2           │ │
                        │  │ → 384-dimensional vectors         │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │             ChromaDB Storage               │
                        │  ┌────────────────────────────────────┐ │
                        │  │ collection.upsert()                │ │
                        │  │ - ids: [node.node_id]             │ │
                        │  │ - embeddings: [vector]            │ │
                        │  │ - documents: [text]                │ │
                        │  │ - metadatas: [{file_name, ...}]   │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Cleanup & Response            │
                        │  ┌────────────────────────────────────┐ │
                        │  │ 1. Remove temp file                │ │
                        │  │ 2. Return {success, id, name}     │ │
                        │  └────────────────────────────────────┘ │
                        └──────────────────────────────────────────┘
```

**API Call:**
```bash
curl -X POST http://localhost:5000/api/documents -F "file=@doc.pdf"
```

**Success Response:**
```json
{"success": true, "id": "doc_stem", "name": "doc.pdf"}
```

---

## 2. Query Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          QUERY PROCESSING FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐         ┌──────────────┐         ┌──────────────────┐
  │ Frontend │         │  web_app.py  │         │   QueryEngine    │
  │   Input  │────────▶│ chat()       │────────▶│ query_streaming()│
  └──────────┘         └──────┬───────┘         └────────┬─────────┘
                               │                           │
                               │ {query: "..."}           │
                               ▼                           │
                        ┌──────────────┐                    │
                        │ Validate:    │                    │
                        │ - Query not empty              │
                        │ - Documents exist              │
                        └──────┬───────┘                    │
                               │                           │
                               ▼                           ▼
                        ┌──────────────────────────────────────────┐
                        │            Context Retrieval              │
                        │  ┌────────────────────────────────────┐ │
                        │  │ VectorIndexRetriever                │ │
                        │  │ - similarity_top_k: 3 (config)     │ │
                        │  │ - Uses ChromaDB                    │ │
                        │  │ - Returns ranked chunks            │ │
                        │  └────────────────────────────────────┘ │
                        │                    │                      │
                        │                    ▼                      │
                        │  ┌────────────────────────────────────┐ │
                        │  │ Yield: {"type": "sources", ...}    │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │            Prompt Construction            │
                        │  ┌────────────────────────────────────┐ │
                        │  │ DEFAULT_RAG_PROMPT template         │ │
                        │  │ {context} + {question}              │ │
                        │  └────────────────────────────────────┘ │
                        │                    │                      │
                        │                    ▼                      │
                        │  ┌────────────────────────────────────┐ │
                        │  │ Prompt sent to Ollama LLM          │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │           LLM Streaming Response         │
                        │  ┌────────────────────────────────────┐ │
                        │  │ Ollama LLM (llama3.2:1b, etc.)     │ │
                        │  │ Temperature: 0.1                   │ │
                        │  │ Timeout: 120s                       │ │
                        │  │                                    │ │
                        │  │ stream_complete() → chunks         │ │
                        │  └────────────────────────────────────┘ │
                        │                    │                      │
                        │                    ▼                      │
                        │  ┌────────────────────────────────────┐ │
                        │  │ Yield: {"type": "chunk", ...}      │ │
                        │  │ Yield: {"type": "done", ...}      │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │            Response Formatting            │
                        │  ┌────────────────────────────────────┐ │
                        │  │ 1. Extract thinking (reasoning mdl) │ │
                        │  │ 2. Format final response           │ │
                        │  │ 3. Add source filenames             │ │
                        │  └────────────────────────────────────┘ │
                        └──────────────────────────────────────────┘
```

**API Call:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'
```

**Response:**
```json
{
  "id": "uuid",
  "type": "assistant",
  "thinking": "...",
  "output": "RAG stands for...",
  "sources": ["doc1.pdf", "doc2.pdf"],
  "model": "llama3.2:1b"
}
```

---

## 3. Graph Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GRAPH DATA FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐         ┌──────────────┐         ┌──────────────────┐
  │ Frontend │         │  web_app.py  │         │   DocumentIndexer │
  │  /graph  │────────▶│ get_graph_() │────────▶│ list_documents()  │
  └──────────┘         └──────┬───────┘         └────────┬─────────┘
                              │                           │
                              │                           │ List of docs
                              ▼                           ▼
                        ┌──────────────────────────────────────────┐
                        │         Per-Document Processing           │
                        │  ┌────────────────────────────────────┐ │
                        │  │ For each document:                 │ │
                        │  │ 1. get_document(filename)          │ │
                        │  │ 2. Extract all text                │ │
                        │  │ 3. Generate summary (LLM or 200ch) │ │
                        │  │ 4. Extract keywords (frequency)    │ │
                        │  │ 5. Determine category (file type)   │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Keyword Extraction           │
                        │  ┌────────────────────────────────────┐ │
                        │  │ 1. Split text into words           │ │
                        │  │ 2. Filter: stopwords, <3 chars     │ │
                        │  │ 3. Count frequencies               │ │
                        │  │ 4. Take top 10                     │ │
                        │  └────────────────────────────────────┘ │
                        │                                          │
                        │  Result: {"keyword": count, ...}        │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Node Creation                 │
                        │  ┌────────────────────────────────────┐ │
                        │  │ For each document:                  │ │
                        │  │ {                                  │ │
                        │  │   id: doc_id,                      │ │
                        │  │   name: filename,                  │ │
                        │  │   val: 3,  // Fixed size!          │ │
                        │  │   group: 1-5,  // Category         │ │
                        │  │   keywords: [kw1, kw2, ...],     │ │
                        │  │   summary: "..."                  │ │
                        │  │ }                                  │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Edge Creation                │
                        │  ┌────────────────────────────────────┐ │
                        │  │ For each document pair:            │ │
                        │  │ 1. Find shared keywords            │ │
                        │  │ 2. If shared >= 1:                │ │
                        │  │    Create link with:               │ │
                        │  │    - source, target                │ │
                        │  │    - value: shared count           │ │
                        │  │    - label: top 3 shared          │ │
                        │  └────────────────────────────────────┘ │
                        └────────────────────┬───────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────────────────┐
                        │              Return JSON                  │
                        │  ┌────────────────────────────────────┐ │
                        │  │ {                                  │ │
                        │  │   nodes: [...],                    │ │
                        │  │   links: [...]                     │ │
                        │  │ }                                  │ │
                        │  └────────────────────────────────────┘ │
                        └──────────────────────────────────────────┘
```

**API Call:**
```bash
curl http://localhost:5000/api/graph
```

**Response Structure:**
```json
{
  "nodes": [
    {
      "id": "abc123",
      "name": "document.pdf",
      "val": 3,
      "group": 1,
      "keywords": ["rag", "retrieval", "generation", ...],
      "summary": "This paper discusses..."
    }
  ],
  "links": [
    {
      "source": "abc123",
      "target": "def456",
      "value": 3,
      "label": "rag, retrieval, generation"
    }
  ]
}
```

---

## 4. Session Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SESSION FLOW (TUI)                              │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │  Session    │
  │  Manager    │
  └──────┬──────┘
         │
         ├──▶ list_sessions() ──────▶ Scan sessions/ directory
         │
         ├──▶ get_session(id) ──────▶ Load or create session
         │
         ├──▶ create_session() ─────▶ Generate ID, create directory
         │
         └──▶ delete_session(id) ───▶ Remove directory

  ┌─────────────┐
  │ ChatSession │
  └──────┬──────┘
         │
         ├──▶ add_message() ────────▶ Create ChatMessageData
         │                               │
         │                               ▼
         │                          _save() ────▶ sessions/{id}/session.json
         │
         └──▶ _load() ◀──────────────── Load on init

  ┌──────────────────────────────────────────┐
  │           session.json Format             │
  │  ┌────────────────────────────────────┐  │
  │  │ {                                  │  │
  │  │   "session_id": "default",        │  │
  │  │   "title": "Chat Title",           │  │
  │  │   "created_at": "ISO",             │  │
  │  │   "updated_at": "ISO",             │  │
  │  │   "messages": [                     │  │
  │  │     {                               │  │
  │  │       "content": "...",            │  │
  │  │       "role": "user|assistant",   │  │
  │  │       "timestamp": "ISO",          │  │
  │  │       "sources": [...]             │  │
  │  │     }                               │  │
  │  │   ]                                 │  │
  │  │ }                                   │  │
  │  └────────────────────────────────────┘  │
  └──────────────────────────────────────────┘
```

**Note:** Web backend currently has hardcoded `session_id = "default"` - session management not exposed via web API.

---

## 5. Directory Structure (Runtime)

```
BitRAG/
├── data/                           # General data (configurable)
├── chroma_db/                      # ChromaDB storage (configurable)
├── sessions/                       # Session storage (configurable)
│   └── default/
│       ├── uploads/                 # Uploaded files
│       │   └── document.pdf
│       ├── chroma_db/             # Session-specific ChromaDB
│       │   └── ...
│       ├── index/                  # LlamaIndex storage (unused currently)
│       │   └── ...
│       └── session.json            # Chat history
└── .bitrag_config.json            # Saved config (optional)
```

---

## 6. ChromaDB Data Structure

```
Collection: bitrag_documents_{session_id}

┌─────────────────────────────────────────────────────────┐
│                    Collection Schema                     │
├─────────────┬─────────────┬────────────────┬──────────┤
│     ids     │ embeddings  │   documents    │ metadatas │
├─────────────┼─────────────┼────────────────┼──────────┤
│ node_abc123 │ [0.1, ...]  │ "Chunk text..."│ {...}    │
│ node_def456 │ [0.2, ...]  │ "More text..." │ {...}    │
│ ...         │ ...         │ ...            │ ...      │
└─────────────┴─────────────┴────────────────┴──────────┘

Metadata Schema:
{
  "file_name": "document.pdf",
  "file_path": "/path/to/sessions/default/uploads/doc.pdf",
  "indexed_at": "2024-01-15T10:30:00Z",
  "session_id": "default"
}
```

---

## 7. Key Processing Pipelines

### Document → Indexed Chunk Pipeline

```
PDF File
    │
    ▼
┌─────────────────┐
│ pypdf Reader   │  Extract text from all pages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Concat     │  Combine all page text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SentenceSplitter│  Split into chunks (512 tokens, 50 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Object │  LlamaIndex Document with metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Node Parser     │  Get nodes from document
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding Model │  Generate 384-dim vectors
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ChromaDB upsert │  Store (id, embedding, text, metadata)
└─────────────────┘
```

### Query → Response Pipeline

```
User Query
    │
    ▼
┌─────────────────┐
│ Query Embedding │  Generate embedding for query
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ChromaDB Search │  Find top-k similar chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Build   │  Concatenate chunks with separators
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt Template │  Insert context + query into RAG prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ollama LLM      │  Generate response (streaming)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response Parse  │  Extract thinking, format output
└────────┬────────┘
         │
         ▼
User Response
```
