# BitRAG Web GUI

A modern web interface for BitRAG - Chat with your PDF documents using RAG (Retrieval-Augmented Generation).

## Features

- **RAG-Powered Chat**: Ask questions about your uploaded documents
- **Document Management**: Upload, view, and delete PDF documents
- **Model Selection**: Configure Ollama models and settings
- **Clean UI**: Dark-themed, responsive interface
- **Lazy Initialization**: Server starts instantly

## Repository Structure

```
BitRAG-Web-GUI/
├── backend/          # Flask server + API
│   ├── app.py        # Main Flask application
│   ├── requirements.txt
│   ├── static/       # Built React frontend
│   └── README.md
├── frontend/         # React source code
│   ├── src/          # Source files
│   ├── index.html    # Vite entry point
│   ├── package.json
│   └── README.md
├── docs/             # Documentation
├── run.sh            # Linux/Mac run script (wrapper)
├── run.py            # Python run script (wrapper)
├── run_backend.py    # Backend specific script
├── run_frontend.py   # Frontend specific script
└── README.md         # This file
```

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Ollama** running with models (e.g., `llama3.2:1b`)

## Quick Start

### Option 1: Use Run Scripts (Recommended)

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x run.sh

# Start both servers
./run.sh both

# Or start backend only
./run.sh backend

# Or start frontend dev server only
./run.sh frontend
```

**Windows:**
```cmd
# Start both servers
python run.py both

# Or start backend only
python run.py backend

# Or start frontend dev server only
python run.py frontend
```

**Python Script (Cross-platform):**
```bash
# Start both servers
python run.py both

# Or start backend only
python run.py backend

# Or start frontend dev server only
python run.py frontend
```

### Option 2: Manual Setup

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Build the Frontend

```bash
cd ../frontend
npm install
npm run build
```

### 3. Copy Built Frontend to Backend

```bash
cp -r dist/* ../backend/static/
```

### 4. Run the Server

```bash
cd ../backend
python3 app.py
```

### 5. Open Browser

Visit **http://localhost:5000**

## Using Run Scripts

The run scripts automate the entire setup process:

### Available Commands

| Command | Description |
|---------|-------------|
| `both` | Start both backend and frontend servers (recommended for development) |
| `backend` | Start backend only (serves built frontend) |
| `frontend` | Start frontend dev server only (Vite dev server) |
| `build` | Build frontend only |
| `install` | Install dependencies only |
| `help` | Show help message (supports `--help` and `-h` aliases) |

### Examples

**Development mode (recommended):**
```bash
# Linux/Mac
./run.sh both

# Windows / Python (Cross-platform)
python run.py both
```

This will:
1. Check prerequisites (Python, Node.js, Ollama)
2. Install backend dependencies
3. Build the frontend
4. Start backend server on port 5000
5. Start frontend dev server on port 5173

**Production mode (backend only):**
```bash
# Linux/Mac
./run.sh backend

# Windows / Python (Cross-platform)
python run.py backend
```

This will:
1. Build the frontend
2. Copy it to backend/static/
3. Start backend server on port 5000 (serves built frontend)

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Server status (ready/initializing) |
| GET | `/api/documents` | List indexed documents |
| POST | `/api/documents` | Upload & index PDF |
| DELETE | `/api/documents/<id>` | Delete document |
| POST | `/api/chat` | Send message (with sources) |
| POST | `/api/chat/stream` | Stream chat response (SSE) |
| GET | `/api/models` | List available Ollama models |
| POST | `/api/models/download` | Download Ollama model |
| POST | `/api/models/delete` | Delete Ollama model |
| GET/POST | `/api/settings` | Get/update settings |
| GET | `/api/system/info` | System information |

### Example Chat Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents do I have?"}'
```

### Example Response

```json
{
  "id": "uuid",
  "type": "assistant",
  "thinking": "1. First, I need to search...",
  "output": "Based on your documents...",
  "sources": ["document1.pdf"]
}
```

## Development

### Backend Development

```bash
cd backend
python3 app.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

The development server will run on http://localhost:5173

### Production Build

1. Build frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Copy to backend:
   ```bash
   cp -r dist/* ../backend/static/
   ```

3. Start backend:
   ```bash
   cd ../backend
   python3 app.py
   ```

## Environment Setup

### Ollama Setup

1. Install Ollama: https://ollama.ai/download
2. Start Ollama: `ollama serve` (or run the Ollama app)
3. Pull a model: `ollama pull llama3.2:1b`

### Virtual Environment (Optional)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Troubleshooting

### Server not starting

```bash
# Check if port 5000 is free
lsof -i :5000

# Try a different port
python3 app.py --port 5001
```

### Model not found

```bash
# List available models
ollama list

# Update model in app.py if needed
# Change: current_model = "llama3.2:1b"
```

### Frontend not updating

```bash
# Rebuild frontend
cd frontend
npm run build
cp -r dist/* ../backend/static/
```

### Build fails with "Could not resolve entry module 'index.html'"

The `frontend/index.html` file might be missing. This file is required by Vite to build the frontend.

**Solution:**
Ensure `frontend/index.html` exists. If it's missing, create it with the following content:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BitRAG - Chat with your Documents</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## License

MIT
