# BitRAG Web Application

This directory contains the Flask web application for BitRAG.

## Structure

- `web/uploads/` - Directory for uploaded documents
- `web_app.py` - Main Flask application

## Running the Web Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web server
python web_app.py
```

Or use the convenience script:

```bash
./run_web.sh
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web interface |
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
| GET | `/api/graph` | Document knowledge graph |
