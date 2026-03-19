# BitRAG Web GUI Backend

Flask server that serves the React frontend and provides API endpoints for BitRAG.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python3 app.py
   ```

3. **Open browser:** http://localhost:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Server status |
| GET | `/api/documents` | List documents |
| POST | `/api/documents` | Upload document |
| DELETE | `/api/documents/<id>` | Delete document |
| POST | `/api/chat` | Send message |
| POST | `/api/chat/stream` | Stream chat response |
| GET | `/api/models` | List available models |
| POST | `/api/models/download` | Download model |
| POST | `/api/models/delete` | Delete model |
| GET/POST | `/api/settings` | Get/update settings |
| GET | `/api/system/info` | System information |
