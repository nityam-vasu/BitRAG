# BitRAG Web Application

This directory contains the Flask web application for BitRAG.

## Structure

```
web/
├── uploads/          # Directory for uploaded documents
└── README.md         # This file
```

The main Flask application (`web_app.py`) is located at the project root.

## Running the Web Application

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r web_requirements.txt

# Run the web server
python web_app.py
```

Or use the convenience script:

```bash
./start.sh
```

Then open http://localhost:5000 in your browser.

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
| GET | `/api/sessions` | List sessions |
| POST | `/api/sessions` | Create session |
| DELETE | `/api/sessions/<id>` | Delete session |

## Testing Results Integration

Test results from the `testing/` directory can be viewed and analyzed through the web interface. Use the `--results-dir` flag to specify output location:

```bash
python testing/test_indexing.py -i test.pdf -r results
```
