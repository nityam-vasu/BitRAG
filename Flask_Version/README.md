# BitRAG Flask Web Interface

A web-based GUI for BitRAG - Chat with your PDF documents using RAG (Retrieval-Augmented Generation).

## Features

- **Modern Web UI**: Bootstrap-based responsive interface
- **Real-time Chat**: Streaming responses for better UX
- **Document Management**: Upload, view, and delete PDF documents
- **Model Selection**: Switch between different Ollama models
- **System Information**: View configuration and status

## Requirements

- Python 3.8+
- Flask & Flask-CORS
- Ollama (running locally on port 11434)
- Virtual environment with dependencies from project root

## Installation

1. Ensure Ollama is installed and running:
   ```bash
   ollama serve
   ```

2. Install Flask-CORS if not already installed:
   ```bash
   pip install flask-cors
   ```

## Running the Application

### Method 1: Using run.sh
```bash
cd Flask_Version
./run.sh
```

### Method 2: Direct Python
```bash
cd Flask_Version
source ../env_8sem/bin/activate  # or your virtual environment
python3 app.py
```

### Method 3: Manual
```bash
# Activate virtual environment
source ../env_8sem/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$PWD/../src:$PYTHONPATH

# Run Flask
python3 app.py
```

## Access the Application

Open your browser and navigate to:
- **http://localhost:5000**

## Pages

### 1. Chat (/)
- Ask questions about your indexed documents
- View sources for responses
- Clear chat history

### 2. Documents (/documents)
- Upload PDF files
- View indexed documents
- Delete documents

### 3. Settings (/settings)
- Select Ollama model
- View system information

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send a question |
| `/api/chat/stream` | POST | Stream chat response |
| `/api/documents` | GET | List documents |
| `/api/documents` | POST | Upload document |
| `/api/documents/<filename>` | DELETE | Delete document |
| `/api/models` | GET | List available models |
| `/api/settings` | GET/POST | Get/Update settings |
| `/api/system/info` | GET | System information |

## Project Structure

```
Flask_Version/
├── app.py          # Main Flask application
├── run.sh          # Launcher script
├── templates/      # HTML templates
│   ├── base.html   # Base template
│   ├── index.html  # Chat page
│   ├── documents.html
│   └── settings.html
├── static/        # Static files (if any)
└── README.md      # This file
```

## Troubleshooting

### App won't start
- Ensure virtual environment is activated
- Check that Ollama is running: `ollama list`
- Install flask-cors: `pip install flask-cors`

### No documents found
- Upload PDF files in the Documents page first
- Wait for indexing to complete

### Model selection issues
- Make sure Ollama is running
- Check available models: `ollama list`

## Dependencies

Key dependencies (already in project):
- flask
- flask-cors
- llama-index
- llama-index-embeddings-huggingface
- llama-index-llms-ollama
- llama-index-vector-stores-chroma
- chromadb
- pypdf
