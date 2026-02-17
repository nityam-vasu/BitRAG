# BitRAG - 1-bit LLM RAG System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.1.0-orange?style=flat-square" alt="Version">
</p>

A lightweight **Retrieval-Augmented Generation (RAG)** system using 1-bit LLMs for chatting with PDF documents. Built with ChromaDB for vector storage and Ollama for local LLM inference.

## ✨ Features

- 📄 **PDF Indexing** - Upload and index PDF documents with automatic text extraction
- 💬 **Chat with PDFs** - Ask questions and get AI-powered answers from your documents
- 🔗 **Session Management** - Organize work into separate sessions
- ⚡ **Lightweight Models** - Works with 1-bit models (qwen2, llama3.2, phi3)
- 🎯 **Vector Search** - ChromaDB for semantic similarity search
- 🖥️ **Interactive CLI** - User-friendly terminal interface with TUI

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
git clone https://github.com/yourusername/bitrag.git
cd bitrag

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e .

# 4. Install Ollama and pull a model
ollama pull qwen2:0.5b
```

### Usage

```bash
# Start interactive mode
bitrag interactive

# Or use the run script
./run.sh
```

## 📖 Usage Guide

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
│       ├── models/       # Data models
│       └── utils/        # Utilities
├── scripts/              # Utility scripts
│   ├── download_model.py
│   ├── create_session.py
│   └── activate_session.py
├── data/                # Sample data directory
├── pyproject.toml       # Package configuration
├── setup.sh            # Setup script
├── run.sh              # Quick start script
└── demo.sh             # Demo script
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) - For the indexing infrastructure
- [ChromaDB](https://www.trychroma.com/) - For vector storage
- [Ollama](https://ollama.ai/) - For local LLM inference
- [HuggingFace](https://huggingface.co/) - For embedding models

---

<p align="center">Made with ❤️ for AI-powered document chat</p>
