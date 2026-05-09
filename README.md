# BitRAG - Local RAG System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-2.2-green?style=flat-square" alt="Version">
</p>

> **Why "BitRAG"?** The name comes from "Bit" (lightweight, minimal footprint) + "RAG" (Retrieval-Augmented Generation). It's designed to run efficiently on minimal CPU resources with low operational costs - perfect for laptops and resource-constrained environments.

A lightweight **Retrieval-Augmented Generation (RAG)** system for chatting with PDF documents. Built with ChromaDB for vector storage, Ollama for local LLM inference, and supports hybrid search combining vector similarity with BM25 keyword search.

## Project Members

| Name | GitHub |
|------|--------|
| [Harsk Kumar Sinha](https://github.com/yourusername) | [GitHub](https://github.com/yourusername) |
| [Vaishnavi Majumdar](https://github.com/yourusername) | [GitHub](https://github.com/yourusername) |
| [Ankita Sahu](https://github.com/yourusername) | [GitHub](https://github.com/yourusername) |
| [Poonam Kalihari](https://github.com/yourusername) | [GitHub](https://github.com/yourusername) |

## ✨ New Features

### 🚀 Custom Embedding Models
- **Model Selection** - Choose from popular embedding models (BGE, MiniLM, E5)
- **Automatic Download** - Downloads on first use

### 🧠 Thinking Mode Support
- **Reasoning Models** - Support for qwen3, deepseek-r1 with thinking
- **Enable/Disable** - `--thinking` / `--no-thinking` flags
- **Thinking Display** - View reasoning process in results

### 🚀 AI-Powered Knowledge Graph
- **Automatic Summarization** - LLM generates summaries for each document
- **Smart Tagging** - Extracts 5-10 semantic tags per document
- **Dynamic Visualization** - Interactive force-graph with zoom, pan, and node details
- **Connection-Based Sizing** - Node size reflects document relationships

### 💬 Enhanced Chat Experience
- **Persistent Sessions** - Save and load chat history
- **TXT Export** - Export conversations as text files
- **Model Selection** - Choose different models for chat, summaries, and tags

### 📊 System Information
- **Real-time Metrics** - CPU, RAM, GPU usage
- **Software Versions** - Flask, Ollama, ChromaDB, LlamaIndex status
- **Model Availability** - See all available Ollama models

### ⚡ Custom Ollama Parameters
- **Pre-made Presets** - Office Laptop and Home Server
- **CPU Optimization** - Thread count, batch size, context window tuning
- **Memory Management** - Memory mapping (mmap) control
- **GPU Layers** - Configure how many layers run on GPU
- **NUMA Support** - Multi-socket server optimization
- **Save Custom Configs** - Save and load your own configurations

## Features

### Core Features
- 📄 **PDF Indexing** - Upload and index PDF documents with automatic text extraction
- 💬 **Chat with PDFs** - Ask questions and get AI-powered answers from your documents
- 🔗 **Session Management** - Organize work into separate sessions with isolated storage
- ⚡ **Lightweight Models** - Works with small models (qwen2, llama3.2, phi3, tinyllama)
- 🎯 **Vector Search** - ChromaDB for semantic similarity search
- 🔀 **Hybrid Search** - Combines vector + BM25 keyword search using Reciprocal Rank Fusion

### User Interfaces
- 🌐 **Web GUI** - Modern web interface with React frontend

### Advanced Features
- 💭 **Reasoning Model Support** - Special handling for thinking/reasoning models
- 📊 **Document Knowledge Graph** - Visualize document relationships in web GUI **(WIP)**
- 🔄 **Streaming Responses** - Real-time streaming output from LLM
- 📁 **Multi-Format Support** - PDF, TXT, MD, DOC, DOCX files **(WIP)**
- ⚙️ **Configurable Parameters** - Chunk size, overlap, top-k, hybrid alpha
- 🤖 **Model Selection** - Separate models for chat, summaries, and tags

### Testing & Benchmarking
- 🧪 **Comprehensive Test Suite** - Validate RAG system performance
- 📈 **Needle-in-Haystack** - Test retrieval accuracy with 20 files
- 🎯 **RAGAS-Lite** - Quality assessment (faithfulness, relevance, precision)
- 🔍 **Hallucination Detection** - Verify answer accuracy against sources
- ⏱️ **Performance Benchmarks** - Indexing speed, inference latency
- 📁 **Results Directory** - All test outputs saved to `results/` with `--results-dir` flag

## Architecture

```
BitRAG/
├── src/bitrag/              # Source code
│   ├── core/                # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── indexer.py      # PDF indexing with ChromaDB
│   │   ├── query.py        # Query engine with Ollama integration
│   │   ├── hybrid_search.py # Vector + BM25 hybrid search
│   │   ├── summary_generator.py  # LLM-based document summarization
│   │   ├── tag_extractor.py     # LLM-based tag extraction
│   │   ├── graph_builder.py     # Knowledge graph construction
│   │   └── session_exporter.py  # Session export utilities
│   ├── cli/                 # Command interface (Click-based)
│   │   └── main.py
├── frontend/               # React frontend for web GUI
├── web/                     # Flask web server
├── scripts/                 # Utility scripts
│   ├── download_model.py   # Model downloader
│   ├── create_session.py   # Session creator
│   └── activate_session.py # Session activator
├── tests/                   # Unit test suite
├── testing/                 # Comprehensive test suite
│   ├── test_indexing.py    # Indexing performance tests
│   ├── test_inference.py   # Inference tests
│   ├── test_needle_20.py   # Needle-in-haystack tests
│   ├── test_ragas_lite.py  # Quality assessment
│   ├── test_faithfulness.py # Hallucination detection
│   └── README.md           # Testing documentation
├── results/                 # Test results and benchmarks
│   ├── SUMMARY.md          # Results overview
│   ├── benchmarks/          # Performance benchmarks
│   ├── comprehensive/       # Detailed test results
│   └── raw/                # Raw JSON data
├── for_metrics/            # Sample PDFs for RAG evaluation
├── test_PDF/               # Test documents
├── web_app.py              # Flask web application
├── bitrag.py               # Main launcher
├── start.sh                # Main startup script (Web UI launcher)
├── setup.sh                # Setup script
├── install.sh              # Installation script
├── requirements.txt       # Python dependencies
├── web_requirements.txt    # Web-specific dependencies
└── README.md
```

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | |
| Ollama | Latest | [Install](https://ollama.com) |
| RAM | 3GB+ | Works with CPU |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nityam-vasu/BitRAG.git
cd BitRAG

# Run setup (creates venv, installs deps, checks Ollama)
./setup.sh

# or else Activate virtual environment
source .venv/bin/activate

# and Start Ollama (in another terminal)
ollama serve

# Download models (optional - see Model Downloader section)
./download_models.sh

# Run the web application
./start.sh
# Open http://localhost:5000

# Or run the terminal interface
./run.sh
```

## Installation

### Automatic Setup (Recommended)

```bash
# Run the setup script - handles everything
./setup.sh

# Or with options
./setup.sh --venv .venv           # Custom venv directory
./setup.sh --skip-ollama          # Skip Ollama check
./setup.sh --check                # Check requirements only
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r web_requirements.txt

# Install package
pip install -e .
```

### Quick Install (Minimal)

```bash
./install.sh                    # Full installation
./install.sh --skip-deps        # Skip pip install (already installed)
./install.sh --check            # Check system requirements
```

## Shell Scripts

All shell scripts support `--help` to show available options.

### `./setup.sh` - Environment Setup

```bash
./setup.sh [OPTIONS]

Options:
  --help, -h              Show help message
  --venv, -v <dir>        Virtual environment directory (default: .venv)
  --skip-venv             Skip virtual environment creation
  --skip-deps             Skip dependency installation
  --skip-ollama           Skip Ollama check
  --check                 Check system requirements only

Examples:
  ./setup.sh                       # Full setup
  ./setup.sh --venv myenv          # Use custom venv
  ./setup.sh --check              # Check requirements
```

### `./install.sh` - Quick Install

```bash
./install.sh [OPTIONS]

Options:
  --help, -h              Show help message
  --venv, -v <dir>        Virtual environment directory (default: venv)
  --skip-deps             Skip dependency installation
  --check                 Check system requirements only

Examples:
  ./install.sh                     # Full installation
  ./install.sh --skip-deps         # Skip pip install
  ./install.sh --check             # Check requirements
```

### `./start.sh` - Web Server (Main Startup)

```bash
./start.sh [OPTIONS]

Options:
  --help, -h              Show help message
  --port, -p <port>       Port to run server on (default: 5000)
  --host, -H <host>       Host to bind to (default: 0.0.0.0)
  --frontend-port, -f <port>  Frontend dev server port (default: 5173)
  --no-install            Skip dependency installation
  --check                 Check system requirements only

Examples:
  ./start.sh                        # Start on localhost:5000
  ./start.sh --port 8080            # Start on port 8080
  ./start.sh --host 127.0.0.1       # Bind to localhost only
  ./start.sh --check                # Check requirements
```

### `./download_models.sh` - Model Downloader

```bash
./download_models.sh [OPTIONS]

Options:
  --help, -h              Show help message
  --list, -l              List models in OLLAMA_MODELS.txt
  --model, -m <name>      Download specific model
  --check, -c             Check Ollama status only

Examples:
  ./download_models.sh                 # Download all models
  ./download_models.sh --list          # List available models
  ./download_models.sh --model llama3.2:1b  # Download specific model
  ./download_models.sh --check        # Check Ollama status
```

### `./run.sh` - Main Runner

```bash
./run.sh [command] [options]

Commands:
  status           Show system status
  logs             View log file
  clear-logs       Clear log file
  web              Start Web UI
  help             Show this help message

Options:
  --session <id>   Session ID to use
  --model <name>   Model to use

Examples:
  ./run.sh                    # Start Web UI
  ./run.sh web                # Start Web UI
  ./run.sh status             # Show status
  ./run.sh web --session myproject  # Start with custom session
```

## Python Scripts

### `web_app.py` - Flask Backend

```bash
python web_app.py [OPTIONS]

Options:
  --help, -h              Show help message
  --port, -p <port>       Port to run on (default: 5000)
  --host, -H <host>       Host to bind to (default: 0.0.0.0)
  --debug                 Enable debug mode
  --check                 Check system requirements only

Examples:
  python web_app.py                    # Run with defaults
  python web_app.py --port 8080        # Run on port 8080
  python web_app.py --host 127.0.0.1   # Bind to localhost
  python web_app.py --debug            # Enable debug mode
  python web_app.py --check            # Check requirements
```

### `bitrag.py` - Main Entry Point

```bash
bitrag [command] [options]

Commands:
  status           Show system status
  interactive      Start interactive mode

Examples:
  bitrag                     # Start web interface
  bitrag status              # Show status
  bitrag --help              # Show help
```

## Usage

### Web User Interface (GUI)

```bash
# Start the web server
./start.sh
# or
python web_app.py

# Open in browser
# http://localhost:5000
```

**Web GUI Features:**
- Modern React-based chat interface
- Document upload and management
- Knowledge graph visualization with AI summaries and tags
- Model selection for chat, summaries, and tags
- System information panel
- Real-time streaming responses
- Session export to TXT
- Reasoning model support with thinking display
- Custom Ollama parameters for CPU/memory optimization

### Session Scripts

```bash
# Create a new session
python scripts/create_session.py
python scripts/create_session.py --name my_project    # Custom name
python scripts/create_session.py --list                # List sessions
python scripts/create_session.py --delete <session_id>  # Delete session

# Activate session and upload documents
python scripts/activate_session.py --session <session_id>
python scripts/activate_session.py --session <id> --upload doc.pdf --index
python scripts/activate_session.py --session <id> --list  # List session documents
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
  "summary_model": "llama3.2:1b",
  "tag_model": "llama3.2:1b",
  "ollama_base_url": "http://localhost:11434",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k": 3,
  "ollama_params": {
    "threads": 4,
    "batch": 512,
    "ctx": 4096,
    "mmap": 1,
    "numa": false,
    "gpu": 0
  }
}
```

## Knowledge Graph

The knowledge graph provides visual document relationships:

### How It Works
1. **Document Upload** - PDFs are indexed and stored in ChromaDB
2. **Summary Generation** - LLM creates 2-3 sentence summaries
3. **Tag Extraction** - LLM extracts 5-10 semantic tags per document
4. **Edge Creation** - Documents sharing tags are connected
5. **Visualization** - Interactive force-graph displays the network

### Node Properties
- **Size** - Reflects number of connections (more connections = larger)
- **Color** - Category based on file type
- **Details** - Summary and tags on click

### Edge Properties
- **Weight** - Number of shared tags
- **Label** - Top 3 shared tags shown

## Hybrid Search

BitRAG supports hybrid search combining vector similarity with BM25 keyword search:

- **Vector Search** - Semantic similarity using embeddings
- **BM25 Search** - Traditional keyword-based retrieval
- **RRF Fusion** - Reciprocal Rank Fusion for combining results

The `alpha` parameter controls the balance:
- `alpha=0.0` - Pure keyword search
- `alpha=0.5` - Balanced (default)
- `alpha=1.0` - Pure vector search


Enable NUMA optimization for multi-socket server systems to improve memory locality and reduce latency.

### Real-World Examples

**Office Laptop (Core i5, 4 cores, 16GB RAM):**
```bash
# Download a model
python scripts/download_model.py --type ollama --model llama3.2:1b
```

## Supported Models

### Quick Setup

| Model | Size | Description |
|-------|------|-------------|
| **falcon3:1b** | ~1.2GB | Falcon 3B - Fast, capable, good for general use |
| **llama3.2:1b** | ~1.3GB | Meta Llama 3.2 1B - Excellent quality, recommended default |
| **llama3.2:3b** | ~2.0GB | Meta Llama 3.2 3B - Better reasoning, slightly larger |
| **qwen2.5:0.5b** | ~400MB | Qwen 2.5 0.5B - Ultra light, very fast |
| **qwen2.5:3b** | ~2.0GB | Qwen 2.5 3B - Great balance of speed and quality |
| **gemma3:1b** | ~800MB | Google Gemma 3 1B - Good multilingual support |
| **tinyllama:1.1b** | ~630MB | TinyLlama - Minimal resource usage |
| **deepseek-r1:1.5b** | ~1.4GB | DeepSeek R1 - Excellent reasoning, supports **thinking** |
| **qwen3:1.7b** | ~1.2GB | Qwen 3 1.7B - Latest Qwen, supports **thinking** |
| **qwen3:0.6b** | ~500MB | Qwen 3 0.6B - Lightweight with latest improvements, supports **thinking** |
| **qwen3.5:0.8b** | ~500MB | Qwen 3.5 0.8B - Best small model, supports **thinking** |
| **granite3.1-moe:1b** | ~700MB | IBM Granite 3.1 MoE - Mixture of experts, efficient |

> **Note**: Models that support "thinking" can display their reasoning process. Use `--thinking` or `--no-thinking` flags to control this.

### Model Selection for Different Tasks

| Task | Recommended Models |
|------|-------------------|
| **Fast responses** | falcon3:1b, qwen3:0.6b, qwen2.5:0.5b |
| **General Q&A** | llama3.2:1b, qwen3:1.7b, falcon3:1b |
| **Reasoning tasks** | deepseek-r1:1.5b, llama3.2:3b |
| **Low memory** | tinyllama:1.1b, qwen2.5:0.5b, qwen3:0.6b |
| **Document summarization** | llama3.2:1b, qwen2.5:3b |
| **Tag extraction** | falcon3:1b, llama3.2:1b |

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

# Or use the automatic downloader
./download_models.sh
```

### Model Download Issues

If automatic download fails:
```bash
# Manually download specific model
ollama pull llama3.2:1b

# Check which models are installed
ollama list

# Remove problematic model
ollama rm model_name
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

### Utilities
- `click>=8.1.0` - Command framework
- `python-dotenv>=1.0.0` - Environment variables
- `pyyaml>=6.0.0` - YAML support
- `requests>=2.31.0` - HTTP requests
- `tqdm>=4.65.0` - Progress bars
- `colorama>=0.4.0` - Terminal colors


---

<p align="center">
  BTech Final Year Project
</p>
