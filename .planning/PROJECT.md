# BitRAG Project Details

## 1. Project Overview

**Project Name**: BitRAG
**Project Type**: RAG (Retrieval-Augmented Generation) Application
**Core Functionality**: Chat with PDF documents using 1-bit LLM models
**Target Users**: Users who want to query their own PDF documents locally using efficient 1-bit quantized LLMs

## 2. Technology Stack

### Core Technologies (Locked)
| Component | Technology | Reason |
|-----------|------------|--------|
| Indexing | LlamaIndex | User requirement |
| **LLM (DEFAULT)** | **BitNet 1.58 (True 1-bit)** | User requirement - pure 1-bit LLM |
| **LLM (Alternative)** | Ollama GGUF models | Better results, easier setup |
| Vector Store | ChromaDB (via LlamaIndex) | Default LlamaIndex integration |
| CLI Framework | Python argparse/Click | CLI-first approach |
| Deployment | Docker | User requirement |
| Frontend | Django | Deferred until CLI works |

### Technology Options

#### 1-bit LLM Options (DEFAULT - True 1-bit)
- **Microsoft BitNet b1.58**: True 1.58-bit model, GGUF format available
  - Native 1-bit (trained from scratch, not post-quantized)
  - 6x lower RAM, 2-6x faster CPU inference
  - Best for: Resource-constrained environments

#### Alternative: Ollama Models (For Better Results)
- **llama3.2:1b**: 4-bit quantized, fast, reliable
- **Phi-3 Mini 4K**: 4-bit, better reasoning
- **Qwen2-0.5B**: 2-3-bit, lightest option

**User Choice:** Default is BitNet (true 1-bit), but users can switch to regular Ollama models for better quality.

#### LlamaIndex Components
- **Document Loaders**: PyPDFLoader for PDFs
- **Text Splitters**: SentenceSplitter for chunking
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaVectorStore

## 3. Architecture

### CLI-First Architecture
```
┌─────────────────┐
│   Python CLI    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG Engine    │  (LlamaIndex + ChromaDB)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ollama LLM    │  (1-bit model)
└─────────────────┘
```

### Future Django Architecture
```
┌─────────────────┐
│   Django UI     │  (Web Interface)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI/REST  │  (API Layer)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG Engine    │
└─────────────────┘
```

## 4. CLI Commands Design

### Core Commands
```bash
# Document Management
bitrag upload <pdf_path>           # Upload and index a PDF
bitrag list                          # List indexed documents
bitrag delete <doc_id>              # Delete a document
bitrag clear                        # Clear all documents

# Querying
bitrag chat "your question"         # Interactive chat with documents
bitrag query "question"             # Single query
bitrag stream "question"            # Streaming response

# Model Management (BitNet vs Ollama)
bitrag model list                   # List available models
bitrag model pull <model>          # Pull a model from Ollama
bitrag model use <model>           # Switch model (bitnet or ollama model)
bitrag model status                # Show current model

# Configuration
bitrag config show                   # Show current config
bitrag config set <key> <value>     # Set configuration

# System
bitrag status                       # Show system status
bitrag stats                        # Show indexing statistics
```

### Model Selection
```
DEFAULT: BitNet 1.58 (true 1-bit)
  - microsoft/bitnet-b1.58-2B-4T-gguf
  - For: Low resource, true 1-bit experience

ALTERNATIVE: Ollama Models (better quality)
  - llama3.2:1b - Fast, reliable
  - phi3:3.8b - Better reasoning
  - For: Better accuracy, more features
```

## 5. Data Flow

### Indexing Flow
```
PDF File → PyPDFLoader → Text → SentenceSplitter → 
→ Embedding (SentenceTransformers) → ChromaDB Vector Store
```

### Query Flow
```
User Question → Embedding → ChromaDB (similarity search) →
→ Retrieved Chunks → Prompt Template → Ollama (1-bit LLM) →
→ Response → User
```

## 6. File Structure

```
bitrag/
├── src/
│   └── bitrag/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── commands.py
│       │   └── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── indexer.py
│       │   ├── query.py
│       │   └── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── document.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── scripts/
│   ├── download_model.py      # Model downloader (Ollama + BitNet)
│   ├── create_session.py      # Session creator
│   ├── activate_session.py    # Upload + Index with progress bar
│   ├── start_web.py           # Web GUI starter
│   └── chat_session.py        # Chat with session auth + streaming
├── sessions/                   # User sessions (created at runtime)
│   └── <session_id>/
│       ├── uploads/
│       ├── index/
│       └── chroma_db/
├── tests/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── web/                        # Django web interface
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 7. Scripts Overview

### 1. download_model.py
```bash
# Download Ollama model
python scripts/download_model.py --type ollama --model llama3.2:1b

# Download BitNet GGUF
python scripts/download_model.py --type bitnet

# List available models
python scripts/download_model.py --list
```

### 2. create_session.py
```bash
# Create new session
python scripts/create_session.py

# Create with custom name
python scripts/create_session.py --name my_project

# List sessions
python scripts/create_session.py --list
```

### 3. activate_session.py
```bash
# Activate session
python scripts/activate_session.py --session 20250213_143022

# Upload and index PDF with progress bar
python scripts/activate_session.py --session 20250213_143022 --upload document.pdf --index
```

### 4. start_web.py
```bash
# Start Django web server
python scripts/start_web.py

# With custom port
python scripts/start_web.py --port 3000 --migrate
```

### 5. chat_session.py
```bash
# Chat with session authentication + streaming
python scripts/chat_session.py --session 20250213_143022

# With specific model
python scripts/chat_session.py --session 20250213_143022 --model phi3:3.8b
```

## 7. Docker Setup

### Services
- **app**: Python CLI application
- **ollama**: LLM runtime (port 11434)

### Volumes
- `./data`: Persistent storage for indexed documents
- `./uploads`: User uploaded PDFs
- `ollama_models`: Ollama model cache

## 8. Development Environment

### Virtual Environment Setup (LOCAL - Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate
# OR on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Verify
bitrag --help
```

### Docker Setup (Production/Deployment)
```bash
# Build and run
docker-compose up --build
```

## 9. Deferred Features

The following will be implemented after CLI success:
- Django web interface
- Support for DOCX, TXT, Markdown files
- Cloud LLM fallback (OpenRouter)
- Multi-document chat
- History management
- Streaming in web UI

## 9. Success Metrics

### Phase Completion Criteria
1. **Virtual Environment**: Python venv with all dependencies
2. **Indexing**: Can upload PDF and see it indexed
3. **Query**: Can ask questions and get relevant answers
4. **1-bit LLM**: Response uses BitNet (true 1-bit) or Ollama model
5. **Docker**: Application runs in containers
6. **CLI**: All commands work smoothly
