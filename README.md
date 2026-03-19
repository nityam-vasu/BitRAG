# BitRAG - 1-bit LLM RAG System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-2.1-green?style=flat-square" alt="Version">
\
</p>

A lightweight **Retrieval-Augmented Generation (RAG)** system for chatting with PDF documents using 1-bit LLMs. Built with ChromaDB for vector storage, Ollama for local LLM inference, and supports hybrid search combining vector similarity with BM25 keyword search.

## Features

### Core Features
- 📄 **PDF Indexing** - Upload and index PDF documents with automatic text extraction
- 💬 **Chat with PDFs** - Ask questions and get AI-powered answers from your documents
- 🔗 **Session Management** - Organize work into separate sessions with isolated storage
- ⚡ **Lightweight Models** - Works with small models (qwen2, llama3.2, phi3, tinyllama)
- 🎯 **Vector Search** - ChromaDB for semantic similarity search
- 🔀 **Hybrid Search** - Combines vector + BM25 keyword search using Reciprocal Rank Fusion

### User Interfaces
- 🖥️ **Interactive TUI** - Terminal interface with menu system and PyTermGUI
- 🌐 **Web GUI** - Modern web interface with React frontend
- ⌨️ **Command Line Interface** - Full CLI for scripting and automation

### Advanced Features
- 💭 **Reasoning Model Support** - Special handling for thinking/reasoning models
- 📊 **Document Knowledge Graph** - Visualize document relationships in web GUI **(WIP)**
- 🔄 **Streaming Responses** - Real-time streaming output from LLM
- 📁 **Multi-Format Support** - PDF, TXT, MD, DOC, DOCX files **(WIP)**
- ⚙️ **Configurable Parameters** - Chunk size, overlap, top-k, hybrid alpha

## Architecture

```
BitRAG/
├── src/bitrag/              # Source code
│   ├── core/                # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── indexer.py      # PDF indexing with ChromaDB
│   │   ├── query.py        # Query engine with Ollama integration
│   │   └── hybrid_search.py # Vector + BM25 hybrid search
│   ├── cli/                 # CLI interface (Click-based)
│   │   └── main.py
├── frontend/               # React frontend for web GUI
├── web/                     # Flask web server
├── scripts/                 # Utility scripts
│   ├── download_model.py   # Model downloader
│   ├── create_session.py   # Session creator
│   └── activate_session.py # Session activator
├── tests/                   # Test suite
├── pdfs/                    # Sample PDFs for testing
├── web_app.py              # Flask web application
├── bitrag.py               # Main launcher (CLI)
├── run_web.sh              # Web GUI launcher
├── setup.sh                # Setup script
├── install.sh              # Installation script
├── requirements.txt       # Python dependencies
├── web_requirements.txt    # Web-specific dependencies
├── pyproject.toml          # Package configuration
└── README.md
```

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | |
| Ollama | Latest | [Install](https://ollama.com) |
| RAM | 2GB+ | Works with CPU |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nityam-vasu/BitRAG.git
cd BitRAG

# Install dependencies
pip install -e .

# Start Ollama (in another terminal)
ollama serve

# Run the application
./run.sh
```

## Installation

### Using the setup script

```bash
chmod +x setup.sh
./setup.sh
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Usage

### Web User Interface (GUI)

The easiest way to use BitRAG:

```bash
# Start the web server
./run_web.sh

# Open in browser
# http://localhost:5000
```

Features:
- Modern React-based chat interface
- Document upload and management
- Model selection and settings
- Document knowledge graph visualization
- Real-time streaming responses
- Reasoning model support with thinking display

### Command Line Interface (CLI)

```bash
# Upload a document
bitrag upload document.pdf

# List documents
bitrag documents

# Query documents
bitrag query "What is this document about?"

# Start chat mode
bitrag chat

# Model management
bitrag model list
bitrag model use llama3.2:1b

# Session management
bitrag session list
bitrag session create my_project
```

### Interactive Commands

When in interactive mode:

| Command | Description |
|---------|-------------|
| `/upload <file>` | Upload and index a PDF |
| `/documents` | List indexed documents |
| `/delete <name>` | Delete a document |
| `/query <text>` | Query indexed documents |
| `/chat` | Start interactive chat |
| `/model <cmd>` | Model management |
| `/session <cmd>` | Session management |
| `/status` | Show system status |
| `/help` | Show help |
| `/exit` | Exit |

## Configuration

### Environment Variables

```bash
export DATA_DIR="./data"
export CHROMA_DIR="./chroma_db"
export SESSIONS_DIR="./sessions"
export DEFAULT_LLM_MODEL="llama3.2:1b"
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Config File

Create `.bitrag_config.json`:

```json
{
  "data_dir": "./data",
  "chroma_dir": "./chroma_db",
  "sessions_dir": "./sessions",
  "default_model": "llama3.2:1b",
  "ollama_base_url": "http://localhost:11434",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k": 3
}
```

## Hybrid Search

BitRAG supports hybrid search combining vector similarity with BM25 keyword search:

- **Vector Search** - Semantic similarity using embeddings
- **BM25 Search** - Traditional keyword-based retrieval
- **RRF Fusion** - Reciprocal Rank Fusion for combining results

The `alpha` parameter controls the balance:
- `alpha=0.0` - Pure keyword search
- `alpha=0.5` - Balanced (default)
- `alpha=1.0` - Pure vector search


### Using the scripts

```bash
# Download a model
python scripts/download_model.py --type ollama --model llama3.2:1b
```

## Supported Models

### Ollama Models (Recommended)

| Model | Size | Description |
|-------|------|-------------|
| llama3.2:1b | ~1.3GB | Fast, reliable - recommended for beginners |
| llama3.2:3b | ~1.8GB | Better quality, larger model |
| qwen2.5:0.5b | ~350MB | Lightest option - ultra fast |
| qwen2.5:3b | ~900MB | Small but capable |
| gemma3:1b  | ~810MB | Googles Open Weight Model, 
| tinyllama:1.1b | ~630MB | Very small, fast |
| gemma3:1b | ~815MB | Lightweight Google model, efficient and balanced |
| deepseek-r1:1.5b | ~1.1GB | Strong reasoning-focused model, good for logic tasks |
| qwen3:1.7b | ~1.4GB | Improved Qwen model, solid performance and versatility |
| granite3.1-moe:1b | ~1.4GB | Mixture-of-experts model, optimized for efficiency and scaling |
| llama3.2:1b | ~1.3GB | Fast, reliable - great general-purpose model |
| qwen3:0.6b | ~522MB | Very lightweight, ultra-fast with basic capabilities |

### BitNet Models (1-bit) **{WIP}*

| Model | Size | Description |
|-------|------|-------------|
| microsoft/bitnet-b1.58-2B-4T | ~700MB | True 1.58-bit model |

## Troubleshooting

### Ollama not found

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### No documents found

```bash
# Upload a PDF first
bitrag upload /path/to/document.pdf
```

### Model not available

```bash
# Pull a model
ollama pull llama3.2:1b
```


## Dependencies

### Core
- `llama-index>=0.10.0` - RAG framework
- `chromadb>=0.4.0` - Vector database
- `sentence-transformers>=2.2.0` - Embeddings
- `pypdf>=3.0.0` - PDF processing
- `rank-bm25>=0.2.0` - BM25 keyword search

### LLM Integration
- `llama-index-llms-ollama>=0.1.0` - Ollama LLM integration
- `llama-index-embeddings-huggingface>=0.1.0` - HuggingFace embeddings
- `llama-index-vector-stores-chroma>=0.1.0` - ChromaDB vector store

### Web GUI
- `flask>=3.0.0` - Web framework
- `flask-cors>=4.0.0` - CORS support
- `psutil>=5.9.0` - System information

### CLI & Utilities
- `click>=8.1.0` - CLI framework
- `python-dotenv>=1.0.0` - Environment variables
- `pyyaml>=6.0.0` - YAML support
- `requests>=2.31.0` - HTTP requests
- `tqdm>=4.65.0` - Progress bars
- `colorama>=0.4.0` - Terminal colors

### Optional: Development
- `pytest>=7.0.0` - Testing
- `ruff>=0.1.0` - Linting
- `black>=23.0.0` - Code formatting



---

<p align="center">
  BTech Final Year Project
</p>
