# BitRAG - Local RAG System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-1.0.0-green?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="License">
</p>

A lightweight **Retrieval-Augmented Generation (RAG)** system for chatting with PDF documents. Built with ChromaDB for vector storage, Ollama for local LLM inference, and supports hybrid search combining vector similarity with BM25 keyword search.

## ✨ New Features

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
- 📊 **Knowledge Graph** - Visualize document relationships with AI-generated summaries and tags
- 🔄 **Streaming Responses** - Real-time streaming output from LLM
- 📁 **Multi-Format Support** - PDF, TXT, MD, DOC, DOCX files
- ⚙️ **Configurable Parameters** - Chunk size, overlap, top-k, hybrid alpha
- 🤖 **Model Selection** - Separate models for chat, summaries, and tags

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
│   ├── cli/                 # CLI interface (Click-based)
│   │   └── main.py
│   └── tui/                 # Terminal User Interface
│       ├── app.py          # Main TUI application
│       ├── chat.py         # Chat session management
│       ├── documents.py    # Document management UI
│       └── settings.py     # Settings management
├── frontend/               # React frontend for web GUI
├── web_app.py             # Flask web application
├── requirements.txt       # Python dependencies
├── web_requirements.txt    # Web-specific dependencies
└── README.md
```

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | |
| Ollama | Latest | [Install](https://ollama.com) |
| RAM | 4GB+ | Works with CPU |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/BitRAG.git
cd BitRAG

# Install dependencies
pip install -e .

# Install frontend dependencies (if using web GUI)
cd frontend && npm install && cd ..

# Start Ollama (in another terminal)
ollama serve

# Run the web application
python web_app.py
# Open http://localhost:5000
```

## Installation

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

## Usage

### Web User Interface (GUI)

```bash
# Start the web server
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

### Terminal User Interface (TUI)

```bash
./run.sh
```

Interactive menu options:
- **1. Chat** - Ask questions about your documents
- **2. Documents** - Manage indexed documents (upload, list, delete)
- **3. Settings** - View configuration
- **4. Status** - System information
- **5. Exit** - Exit the application

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
  "summary_model": "llama3.2:1b",
  "tag_model": "llama3.2:1b",
  "ollama_base_url": "http://localhost:11434",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k": 3
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

## Supported Models

### Ollama Models (Recommended)

| Model | Size | Description |
|-------|------|-------------|
| llama3.2:1b | ~1.3GB | Fast, reliable - recommended for beginners |
| llama3.2:3b | ~1.8GB | Better quality, larger model |
| qwen2.5:0.5b | ~350MB | Lightest option - ultra fast |
| qwen2.5:3b | ~900MB | Small but capable |
| phi3:3.8b | ~2.3GB | Microsoft Phi-3, good reasoning |
| phi3:14b | ~7.9GB | Larger Phi-3, best reasoning |
| tinyllama:1.1b | ~630MB | Very small, fast |
| mistral:7b | ~4GB | Good all-around model |

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

### PyTermGUI issues

If the TUI fails to start with PyTermGUI, the application will automatically fall back to text-based menu mode.

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

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with ❤️ for educational purposes
</p>
