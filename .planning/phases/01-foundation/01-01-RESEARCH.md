# Phase 01: Research & Foundation - RESEARCH.md

## Research Summary

This document captures research findings for building BitRAG - a RAG system using 1-bit LLMs and LlamaIndex.

---

## 1. 1-bit LLM Options

### Primary Option: Microsoft BitNet (DEFAULT - TRUE 1-BIT)

| Model | Type | Size | Bits/Weight | Format | Performance |
|-------|------|------|-------------|--------|-------------|
| Microsoft BitNet b1.58 2B | **Native 1-bit** | 2B | **1.58** | GGUF | ~6x lower RAM, 2-6x faster CPU |

**Why BitNet as Default:**
- True 1.58-bit model from Microsoft Research
- Trained from scratch with 1-bit weights (not post-quantized)
- GGUF format available for Ollama compatibility
- Achieves performance comparable to full-precision models
- 6x lower RAM usage than FP16 models

### Alternative: Ollama Models (For Better Results)

| Model | Type | Size | Bits/Weight | Use Case |
|-------|------|------|-------------|----------|
| llama3.2:1b | Quantized | 1B | ~4-bit | Fast, reliable |
| phi3:3.8b | Quantized | 3.8B | ~4-bit | Better reasoning |
| qwen2:0.5b | Quantized | 0.5B | ~2-3-bit | Lightest |

**Why Alternative Models:**
- More mature, well-tested in production
- Better reasoning capabilities
- Easier setup (works out-of-box with Ollama)
- Better community support

### Running with Ollama

```bash
# For BitNet - Download GGUF manually
# https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf

# For Ollama models (easier setup)
ollama pull llama3.2:1b
ollama pull phi3:3.8b
```

---

## 2. LlamaIndex Setup

### Installation

```bash
# Core package
pip install llama-index

# PDF support
pip install pypdf

# ChromaDB vector store
pip install llama-index-vector-stores-chroma chromadb

# Embeddings (using HuggingFace - local, free)
pip install llama-index-embeddings-huggingface sentence-transformers

# Ollama LLM integration
pip install llama-index-llms-ollama
```

### Key Components

| Component | Purpose | LlamaIndex Module |
|-----------|---------|-------------------|
| Document Loading | Load PDFs, TXT, etc. | `llama_index.readers` |
| Text Splitting | Chunk documents | `llama_index.core.node_parser` |
| Embeddings | Convert text to vectors | `llama_index.embeddings.huggingface` |
| Vector Store | Store embeddings | `llama_index.vector_stores.chroma` |
| Query Engine | RAG query pipeline | `llama_index.core` |

### PDF Processing

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PyPDFReader

# Load PDF
reader = PyPDFReader()
documents = reader.load_data(file_path="document.pdf")

# Or use SimpleDirectoryReader (auto-detects PDF)
documents = SimpleDirectoryReader(input_files=["doc.pdf"]).load_data()
```

### Chunking Strategy

```python
from llama_index.core.node_parser import SentenceSplitter

parser = SentenceSplitter(
    chunk_size=512,        # Characters per chunk
    chunk_overlap=50,      # Overlap for context continuity
    separator="\n"         # Split on newlines
)
```

---

## 3. ChromaDB Integration

### Setup

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

# Persistent ChromaDB (saves to disk)
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("bitrag_docs")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Create storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)
```

### Operations

| Operation | Method |
|-----------|--------|
| Index documents | `VectorStoreIndex.from_documents(documents, storage_context)` |
| Query | `index.as_query_engine().query("question")` |
| Delete by doc_id | `chroma_collection.delete(where={"doc_id": "..."})` |
| Clear all | `chroma_collection.delete(where={})` |

---

## 4. Ollama Integration

### Setup

```python
from llama_index.llms.ollama import Ollama

# Initialize Ollama with 1-bit model
llm = Ollama(
    model="llama3.2:1b",  # Lightweight model
    base_url="http://localhost:11434",
    temperature=0.3,
)

# Use in query engine
query_engine = index.as_query_engine(llm=llm)
```

### Streaming Response

```python
response = query_engine.query("question")
for chunk in response.response_gen:
    print(chunk, end="", flush=True)
```

---

## 5. RAG Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER QUESTION                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   EMBED QUESTION                             │
│              (SentenceTransformers)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 CHROMADB RETRIEVAL                           │
│         (Similarity Search - top_k=3)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              BUILD CONTEXT FROM CHUNKS                      │
│         (Combine top chunks + metadata)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              OLLAMA LLM GENERATION                          │
│              (1-bit model + prompt)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE OUTPUT                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Project Structure

```
bitrag/
├── src/bitrag/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py      # CLI command implementations
│   │   └── main.py          # Entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── indexer.py       # Document indexing
│   │   ├── query.py         # RAG query engine
│   │   └── models.py        # Data models
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
├── data/                    # PDF storage
├── chroma_db/              # Vector database
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 7. CLI Commands Design

### Core Commands

| Command | Description |
|---------|-------------|
| `bitrag upload <path>` | Upload and index a PDF |
| `bitrag list` | List indexed documents |
| `bitrag delete <id>` | Delete a document |
| `bitrag chat` | Interactive chat mode |
| `bitrag query <text>` | Single query |
| `bitrag model list` | List available Ollama models |
| `bitrag model pull <name>` | Pull a model |
| `bitrag status` | Show system status |

---

## 8. Docker Setup

### Services

```yaml
services:
  app:
    build: .
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama_models:
```

---

## 9. Key Decisions

| Decision | Recommendation |
|----------|----------------|
| 1-bit Model | Use Ollama's llama3.2:1b initially (widely tested), then try BitNet GGUF |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality) |
| Chunk Size | 512 chars with 50 char overlap |
| Top-K | 3-5 chunks for context |
| Vector Store | ChromaDB (PersistentClient for disk persistence) |

---

## 10. Common Pitfalls

1. **Memory**: 1-bit models still need 2-4GB RAM for inference
2. **First Run**: Ollama downloads model on first use (slow)
3. **PDF Parsing**: Some PDFs have images/tables - may need LlamaParse for complex docs
4. **Chroma Persistence**: Must use PersistentClient, not EphemeralClient
5. **Embedding Model**: Must be consistent - use same model for indexing and querying

---

## References

- Microsoft BitNet: https://github.com/microsoft/BitNet
- BitNet GGUF: https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf
- LlamaIndex Docs: https://docs.llamaindex.ai
- Ollama: https://ollama.com
- ChromaDB: https://docs.trychroma.com
