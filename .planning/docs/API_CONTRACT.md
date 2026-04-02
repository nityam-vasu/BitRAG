# BitRAG API Contract Documentation

**Document:** API_CONTRACT.md
**Version:** 1.0
**Date:** 2026-04-02

---

## Overview

The BitRAG API is a REST API served by a Flask backend. It provides endpoints for:
- Chat with documents (query)
- Document management (upload, list, delete)
- Graph visualization data
- Settings management
- Model management
- System information

**Base URL:** `http://localhost:5000`

---

## Authentication

No authentication required (local application).

---

## Common Headers

| Header | Value | Required |
|--------|-------|----------|
| Content-Type | application/json | For POST requests |

---

## Endpoints

### 1. Health & Status

#### GET `/api/status`
Check API/server status.

**Response (200):**
```json
{
  "status": "ready",
  "message": "Server is running and ready",
  "initialized": true,
  "initializing": false
}
```

**Status Values:**
- `ready`: Server fully initialized
- `initializing`: Server starting up

---

#### GET `/debug`
Debug endpoint for troubleshooting.

**Response (200):**
```json
{
  "status": "ok",
  "frontend_dir": "/path/to/frontend",
  "initialized": true,
  "initializing": false
}
```

---

### 2. Chat

#### POST `/api/chat`
Process a chat query (non-streaming).

**Request:**
```json
{
  "query": "What is RAG?"
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "assistant",
  "thinking": "Analyzing your question and searching through indexed documents...",
  "output": "RAG stands for Retrieval-Augmented Generation...",
  "sources": ["document.pdf", "paper.pdf"],
  "model": "llama3.2:1b",
  "is_reasoning_model": false
}
```

**Error Responses:**
- `400`: Empty question or no documents indexed
- `500`: Server error
- `503`: Server still initializing

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'
```

---

#### POST `/api/chat/stream`
Process a chat query with streaming response (SSE).

**Request:**
```json
{
  "query": "Explain machine learning"
}
```

**Response:** Server-Sent Events stream

**Event Types:**
```
data: {"type": "thinking", "thinking": "Starting reasoning..."}

data: {"type": "sources", "sources": ["doc1.pdf"]}

data: {"type": "chunk", "output": "Machine"}

data: {"type": "chunk", "output": " learning"}

data: {"type": "done", "output": "Machine learning is..."}
```

**Error Event:**
```
data: {"type": "error", "message": "No documents found..."}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"query": "What is RAG?"}'
```

---

### 3. Documents

#### GET `/api/documents`
List all indexed documents.

**Response (200):**
```json
[
  {
    "id": "doc_node_id",
    "name": "document.pdf"
  },
  {
    "id": "doc_node_id_2",
    "name": "report.pdf"
  }
]
```

**cURL Example:**
```bash
curl http://localhost:5000/api/documents
```

---

#### POST `/api/documents`
Upload and index a new document.

**Request:** `multipart/form-data`
- `file`: PDF, TXT, MD, DOC, or DOCX file

**Response (200):**
```json
{
  "success": true,
  "id": "document_stem",
  "name": "document.pdf"
}
```

**Error Responses:**
- `400`: No file, invalid type, or empty file
- `404`: File not found after save
- `500`: Indexing failed
- `503`: Server initializing

**Allowed File Types:**
- `.pdf`
- `.txt`
- `.md`
- `.doc`
- `.docx`

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/documents \
  -F "file=@/path/to/document.pdf"
```

---

#### DELETE `/api/documents/<doc_id>`
Delete a document by filename.

**Parameters:**
- `doc_id`: Document filename (URL encoded)

**Response (200):**
```json
{
  "success": true
}
```

**Error Responses:**
- `500`: Deletion failed

**cURL Example:**
```bash
curl -X DELETE http://localhost:5000/api/documents/document.pdf
```

---

### 4. Graph

#### GET `/api/graph`
Get graph data for document visualization.

**Response (200):**
```json
{
  "nodes": [
    {
      "id": "node_id_1",
      "name": "document.pdf",
      "val": 3,
      "group": 1,
      "keywords": ["rag", "retrieval", "generation"],
      "summary": "Document about RAG technology..."
    }
  ],
  "links": [
    {
      "source": "node_id_1",
      "target": "node_id_2",
      "value": 3,
      "label": "rag, retrieval, generation"
    }
  ]
}
```

**Node Properties:**
| Property | Type | Description |
|----------|------|-------------|
| id | string | Unique node identifier |
| name | string | Document filename |
| val | number | Node size (currently fixed at 3) |
| group | number | Category (1-5 based on file type) |
| keywords | string[] | Top 10 keywords |
| summary | string | Document summary |

**Link Properties:**
| Property | Type | Description |
|----------|------|-------------|
| source | string | Source node ID |
| target | string | Target node ID |
| value | number | Edge weight (shared keywords count) |
| label | string | Top 3 shared keywords |

**Group Categories:**
| Group | File Types |
|-------|-----------|
| 1 | pdf, doc, docx |
| 2 | md, txt |
| 3 | py, js, java, cpp |
| 4 | jpg, png, gif, svg |
| 5 | Other |

**cURL Example:**
```bash
curl http://localhost:5000/api/graph | python -m json.tool
```

---

### 5. Settings

#### GET `/api/settings`
Get current settings.

**Response (200):**
```json
{
  "model": "llama3.2:1b",
  "ollamaPort": 11434,
  "hybridMode": false,
  "dualMode": false,
  "model1": "llama3.2:1b",
  "model2": "llama3.2:1b",
  "documentCount": 5,
  "ollamaStatus": "running"
}
```

**Ollama Status Values:**
- `running`: Ollama is available
- `not responding`: Cannot connect to Ollama
- `error`: Ollama returned an error

---

#### POST `/api/settings`
Update settings.

**Request:**
```json
{
  "model": "qwen2.5:3b",
  "ollamaPort": 11434,
  "hybridMode": true,
  "dualMode": false,
  "model1": "llama3.2:1b",
  "model2": "qwen2.5:3b"
}
```

**All fields are optional.** Only provided fields are updated.

**Response (200):**
```json
{
  "success": true,
  "model": "qwen2.5:3b",
  "ollamaPort": 11434,
  "hybridMode": true,
  "dualMode": false,
  "model1": "llama3.2:1b",
  "model2": "qwen2.5:3b"
}
```

**cURL Examples:**
```bash
# Change model
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b"}'

# Enable hybrid mode
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"hybridMode": true}'
```

---

### 6. Models

#### GET `/api/models`
List available Ollama models.

**Response (200):**
```json
{
  "models": [
    "llama3.2:1b",
    "qwen2.5:3b",
    "phi3:3.8b"
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/models
```

---

#### POST `/api/models/download`
Download a model from Ollama registry.

**Request:**
```json
{
  "model": "qwen2.5:3b"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Model qwen2.5:3b downloaded"
}
```

**Error Responses:**
- `400`: No model specified
- `500`: Download failed

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/models/download \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b"}'
```

---

#### POST `/api/models/delete`
Delete a model from Ollama.

**Request:**
```json
{
  "model": "qwen2.5:3b"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Model qwen2.5:3b deleted"
}
```

**Error Responses:**
- `400`: No model specified
- `500`: Deletion failed

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/models/delete \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b"}'
```

---

### 7. System

#### GET `/api/system/info`
Get detailed system information.

**Response (200):**
```json
{
  "sessionId": "default",
  "documentCount": 5,
  "embeddingModel": "sentence-transformers/all-MiniLM-L6-v2",
  "chunkSize": 512,
  "topK": 3,
  "cpu": 45.2,
  "memory": {
    "used": 8.5,
    "total": 16.0,
    "percent": 53.1
  },
  "gpu": {
    "utilization": 0,
    "memory_used": 0,
    "memory_total": 0
  },
  "ollamaStatus": "running",
  "ollamaModels": ["llama3.2:1b", "qwen2.5:3b"]
}
```

**Note:** GPU info shows zeros if nvidia-smi is not available.

**cURL Example:**
```bash
curl http://localhost:5000/api/system/info | python -m json.tool
```

---

### 8. Static Files

#### GET `/`, `/graph`, `/settings`, `/documents`
Serve the React frontend.

**Response:** HTML page (index.html)

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

Additional fields may be included depending on the error.

---

## Rate Limits

No rate limits (local application).

---

## Examples

### Full Chat Flow

```bash
# 1. Check status
curl http://localhost:5000/api/status

# 2. Upload a document
curl -X POST http://localhost:5000/api/documents \
  -F "file=@research_paper.pdf"

# 3. List documents
curl http://localhost:5000/api/documents

# 4. Chat with document
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of this paper?"}'

# 5. Get graph visualization
curl http://localhost:5000/api/graph | python -m json.tool

# 6. Check system info
curl http://localhost:5000/api/system/info
```

---

## Notes

1. **Session Management:** Currently uses a single hardcoded "default" session
2. **Graph Generation:** Summaries are generated using LLM if available, otherwise first 200 chars
3. **Keywords:** Extracted using simple word frequency (stopwords filtered)
4. **Model Switching:** Changes model for subsequent queries; existing responses use previous model
5. **Ollama Connection:** Uses `127.0.0.1` instead of `localhost` to avoid IPv6 issues
