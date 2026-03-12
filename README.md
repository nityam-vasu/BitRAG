# BitRAG - 1-bit LLM RAG System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Version-0.1.0-orange?style=flat-square" alt="Version">
</p>

A lightweight **Retrieval-Augmented Generation (RAG)** system using 1-bit LLMs for chatting with PDF documents. Built with ChromaDB for vector storage and Ollama for local LLM inference. Features a beautiful **PyTermGUI-based Terminal User Interface (TUI)** for an enhanced user experience.

## ✨ Features

- 📄 **PDF Indexing** - Upload and index PDF documents with automatic text extraction
- 💬 **Chat with PDFs** - Ask questions and get AI-powered answers from your documents
- 🔗 **Session Management** - Organize work into separate sessions
- ⚡ **Lightweight Models** - Works with 1-bit models (qwen2, llama3.2, phi3)
- 🎯 **Vector Search** - ChromaDB for semantic similarity search
- 🖥️ **Interactive TUI** - Terminal interface with:
  - Interactive menu system
  - Chat mode for querying documents
  - Document management (upload, list, delete)
  - Settings display
  - Session management

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | |
| Ollama | Latest | [Install](https://ollama.com) |
| RAM | 4GB+ | Works with CPU |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/nityam-vasu/BitRAG.git
cd bitrag

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e .
# OR use requirements.txt
pip install -r requirements.txt

# 4. Install Ollama and pull a model
ollama pull qwen2:0.5b
```

### Usage

```bash
# Option 1: Run with bitrag.py (Recommended)
python bitrag.py              # Start TUI
python bitrag.py tui          # Start Terminal UI
python bitrag.py cli          # Start CLI
python bitrag.py status       # Show system status

# Option 2: Run with run.sh (Recommended - starts PyTermGUI TUI by default)
./run.sh              # Start TUI
./run.sh tui          # Start TUI
./run.sh cli          # Start CLI
./run.sh status       # Show status

# Option 3: Run with run.sh in CLI mode (legacy)
./run.sh --cli

## 📖 Usage Guide

### Quick Start

```bash
# Start TUI (recommended)
python bitrag.py
# OR
./run.sh

# Show system status
python bitrag.py status
./run.sh status
```

### bitrag.py Commands

```bash
python bitrag.py              # Start TUI (default)
python bitrag.py tui          # Start Terminal UI
python bitrag.py cli          # Start CLI
python bitrag.py status       # Show system status
python bitrag.py --help       # Help
```

### CLI Commands

```bash
# Upload and index a PDF
bitrag upload document.pdf

# List indexed documents
bitrag documents

# Get document details
bitrag get-document "document.pdf"

# Update document metadata
bitrag update-document "document.pdf" --key category=important

# Delete document
bitrag delete "document.pdf"

# Query documents
bitrag query "What is this document about?"

# Start chat mode
bitrag chat

# Model management
bitrag model list          # List available models
bitrag model status        # Show current model
bitrag model use llama3.2:1b  # Switch model
bitrag model download phi3:3.8b  # Download model

# Session management
bitrag session list        # List sessions
```

### Interactive Mode Commands

```
/upload <file>      Upload and index a PDF
/documents          List indexed documents  
/get <name>         Get document details
/delete <name>      Delete document
/browse             Browse for PDF files
/query <text>       Query indexed documents
/chat               Start interactive chat
/model <cmd>        Model management (list|status|use|download)
/session <cmd>      Session management
/status             Show system status
/clear              Clear screen
/help               Show help
/exit               Exit
```

## 🖥️ TUI Guide

BitRAG features an interactive Terminal User Interface (TUI) for easy document management and chatting.

### Starting the TUI

```bash
# Activate your virtual environment
source .venv/bin/activate

# Start the TUI (Recommended)
python bitrag.py
# OR
./run.sh

# Or start with run.sh
./run.sh tui
```

### TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **C** | Chat screen (main window) |
| **S** | Settings |
| **U** | Upload/Documents |
| **Q** | Quit |

### TUI Modes

| Mode | Description |
|------|-------------|
| **Chat** | Ask questions about your indexed documents |
| **Documents** | Manage indexed PDFs (upload, list, delete) |
| **Settings** | View current configuration |

### Using the TUI

1. **Start the TUI**
   - Run `python src/bitrag/tui/main.py` or `./run.sh`
   - You'll see the main menu

2. **Select a Mode**
   - Type `1` for Chat mode
   - Type `2` for Documents mode
   - Type `3` for Settings
   - Type `4` to Quit

3. **Chat Mode**
   - Ask questions about your documents
   - Type `help` for commands
   - Type `exit` to return to main menu

4. **Documents Mode**
   - `list` - Show indexed documents
   - `upload <path>` - Index a PDF
   - `delete <id>` - Remove a document
   - Type `exit` to return to main menu

### Command Line Options

```bash
# Start in specific mode
python src/bitrag/tui/main.py chat
python src/bitrag/tui/main.py documents
python src/bitrag/tui/main.py settings

# Or use run.sh
./run.sh --cli chat
```

### Troubleshooting

**No documents found:**
```bash
# First upload a PDF in Documents mode
upload /path/to/your/document.pdf
```

**Ollama not running:**
```bash
# Start Ollama
ollama serve
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -e .
```

## 🏗️ Project Structure

```
bitrag/
├── src/
│   └── bitrag/
│       ├── cli/           # Command-line interface
│       │   └── main.py   # CLI entry point
│       ├── core/         # Core functionality
│       │   ├── config.py    # Configuration
│       │   ├── indexer.py   # PDF indexing
│       │   └── query.py     # Query engine
│       ├── tui/          # PyTermGUI TUI
│       │   ├── __main__.py  # TUI entry point
│       │   ├── app.py       # Main application
│       │   ├── chat_display.py  # Chat widgets
│       │   ├── document_manager.py  # Document management
│       │   ├── settings.py  # Settings panel
│       │   ├── documents.py # Document management UI
│       │   └── ...
│       ├── models/       # Data models
│       └── utils/        # Utilities
├── scripts/              # Utility scripts
├── bitrag.py            # Main launcher
├── pyproject.toml       # Package configuration
├── requirements.txt     # Python dependencies
├── run.sh              # Quick start script
└── ...
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `./data` | Data directory |
| `CHROMA_DIR` | `./chroma_db` | ChromaDB directory |
| `SESSIONS_DIR` | `./sessions` | Sessions directory |
| `DEFAULT_LLM_MODEL` | `qwen2.5:0.5b` | Default LLM model |
| `LLM_TYPE` | `ollama` | LLM type |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama URL |

### Config File

Create `.bitrag_config.json` to customize settings:

```json
{
  "data_dir": "./data",
  "chroma_dir": "./chroma_db", 
  "sessions_dir": "./sessions",
  "default_model": "qwen2.5:0.5b",
  "llm_type": "ollama",
  "ollama_base_url": "http://localhost:11434",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k": 3
}
```

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Style

```bash
# Format code
ruff check --fix .
ruff format .
```

## 📝 Troubleshooting

### Ollama not found
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### No documents found
```bash
# Upload a PDF
bitrag upload data/your_document.pdf
```

### Model not available
```bash
# Pull a model
ollama pull qwen2.5:0.5b
```

### Port already in use
```bash
# Check what's using port 11434
lsof -i :11434
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) - For the indexing infrastructure
- [ChromaDB](https://www.trychroma.com/) - For vector storage
- [Ollama](https://ollama.ai/) - For local LLM inference
- [HuggingFace](https://huggingface.co/) - For embedding models


---

<p align="center">BTech Project</p>
