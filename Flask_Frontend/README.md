# BitRAG Flask Frontend

This is the custom frontend UI for BitRAG, built with React, TypeScript, and Tailwind CSS.

## Features

- **Chat Interface**: Ask questions about your documents
- **Document Management**: Upload, view, and delete PDF documents
- **Settings**: Configure model selection, Ollama connection, and hybrid retrieval
- **Modern Design**: Clean dark-mode UI matching the original Figma design

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python 3.8+
- Ollama running with an available model (e.g., `llama3.2:1b`)

### Installation

1. Install frontend dependencies:
   ```bash
   npm install
   npm install react react-dom
   ```

2. Build the frontend:
   ```bash
   npm run build
   ```

3. Install Python dependencies:
   ```bash
   pip install flask flask-cors
   pip install -e ../src
   ```

### Running the Application

1. **Ensure Ollama is running**:
   ```bash
   ollama serve  # or start Ollama app
   ```

2. **Pull a model if needed**:
   ```bash
   ollama pull llama3.2:1b
   ```

3. **Start the Flask server**:
   ```bash
   python3 app.py
   ```

4. **Open your browser**:
   - **http://localhost:5000**

## Lazy Initialization

The server uses **lazy initialization** - components are only loaded when needed:

```
============================================================
  BitRAG Flask Backend
  Powered by Ollama & ChromaDB
============================================================

✓ Server ready - initialization will happen on first request

🌐 Web server: http://localhost:5000
Press CTRL+C to stop
```

**Behavior:**
- Server starts **instantly** (no initialization at startup)
- Homepage loads immediately
- When you make your first API request (chat, upload, etc.), the backend initializes:
  - Loading embedding model
  - Connecting to Ollama
  - Setting up indexer
- Subsequent requests are fast

**Status check:** `GET /api/status` returns `{"status":"initializing"}` or `{"status":"ready"}`

## API Endpoints

The Flask backend provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Check server initialization status |
| `/api/chat` | POST | Send chat message |
| `/api/chat/stream` | POST | Stream chat response |
| `/api/documents` | GET | List indexed documents |
| `/api/documents` | POST | Upload & index document |
| `/api/documents/<id>` | DELETE | Delete document |
| `/api/models` | GET | List available Ollama models |
| `/api/models/download` | POST | Download Ollama model |
| `/api/models/delete` | POST | Delete Ollama model |
| `/api/settings` | GET/POST | Get/update settings |
| `/api/system/info` | GET | System information |

## Project Structure

```
Flask_Frontend/
├── app.py              # Flask backend server
├── dist/               # Built frontend (production)
├── src/                # React source code
│   ├── app/
│   │   ├── pages/      # ChatPage, SettingsPage, DocumentsPage
│   │   ├── components/ # UI components
│   │   └── routes.tsx  # React Router config
│   └── main.tsx        # App entry point
└── package.json        # Frontend dependencies
```

## Development

Run development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

## Troubleshooting

### Warning: "Sending unauthenticated requests to the HF Hub"
This is a harmless warning from the embedding model. To remove it:
```bash
export HF_TOKEN=your_token_here
```
Or ignore it - it doesn't affect functionality.

### Model not found error
Make sure your model name matches what's available in Ollama:
```bash
ollama list
```
Update the default model in `app.py` if needed:
```python
current_model = "llama3.2:1b"  # Change to your model name
```

### Server not responding
Check if Ollama is running:
```bash
ollama list
```
If not, start it:
```bash
ollama serve
```

## Performance Tips

- **First request**: Takes 5-30 seconds (initializes embeddings + connects to Ollama)
- **Subsequent requests**: Instant response
- Server stays initialized until stopped
