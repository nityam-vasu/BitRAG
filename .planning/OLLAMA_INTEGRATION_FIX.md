# Ollama Integration Improvements

## Overview

Based on the working OLLAMA_INTEGRATION.md from the previous project (Comic Crafter / BitRAG-Web-GUI), I've implemented proper Ollama integration in the BitRAG core module.

## Changes Made

### 1. Added OllamaService Class (`src/bitrag/core/query.py`)

A new `OllamaService` class provides centralized Ollama management:

```python
class OllamaService:
    def is_available() -> bool       # Check if Ollama server is running
    def list_models() -> List[str]   # Get available models
    def model_exists(model) -> bool  # Validate model exists
    def get_model_info(model) -> Dict  # Get model details
    def pull_model(model) -> bool    # Pull model from registry
    def invalidate_cache()           # Refresh model list
```

**Key Features:**
- Uses `GET /api/tags` endpoint (same as working implementation)
- Caches model list for performance
- Proper timeout handling (3 second default)
- Uses `127.0.0.1` instead of `localhost` to avoid IPv6 issues

### 2. Enhanced QueryEngine Integration

The `QueryEngine` class now includes:

- **Availability checking** on initialization
- **Model validation** before switching models
- **`get_ollama_status()` method** for status reporting
- **`refresh_ollama_models()` method** to update cached model list

```python
engine = QueryEngine(session_id='test')
status = engine.get_ollama_status()
# Returns: {'available': True, 'model_exists': True, 'model': 'llama3.2:1b', ...}
```

### 3. Improved TUI Status Display (`src/bitrag/tui/app.py`)

The TUI now shows:
- Number of available models
- List of available models (truncated to 5)
- Proper fallback to subprocess if imports fail

## Issues Fixed

| Issue | Before | After |
|-------|--------|-------|
| No availability check | Silent failure | Warns if Ollama not running |
| Model not validated | Tries to use any model | Validates model exists before use |
| No model list | Unknown what models available | Shows available models |
| Hardcoded URLs | Always used localhost | Uses config.ollama_base_url |

## Usage Examples

### Check Ollama Status
```python
from bitrag.core.query import OllamaService

service = OllamaService(base_url='http://localhost:11434')
if service.is_available():
    models = service.list_models()
    print(f"Available models: {models}")
```

### Validate Model Before Use
```python
from bitrag.core.query import QueryEngine

engine = QueryEngine(session_id='my_session')
if not engine.set_model('llama3.2:1b'):
    print("Model not available!")
    available = engine.get_ollama_status()['available_models']
    print(f"Try one of these: {available}")
```

### Get Ollama Status
```python
engine = QueryEngine(session_id='my_session')
status = engine.get_ollama_status()
print(f"Ollama: {status['available']}")
print(f"Model '{status['model']}': {status['model_exists']}")
```

## Files Changed

- `src/bitrag/core/query.py` - Added OllamaService class and validation
- `src/bitrag/tui/app.py` - Improved TUI status display

## Testing

Run the following to verify the integration:

```bash
source venv/bin/activate
python -c "
from src.bitrag.core.query import QueryEngine, OllamaService

# Test service
service = OllamaService()
print(f'Ollama available: {service.is_available()}')
print(f'Models: {service.list_models()}')

# Test engine
engine = QueryEngine(session_id='test', _skip_ollama_check=False)
print(f'Status: {engine.get_ollama_status()}')
"
```

## Notes

- The integration follows the same patterns as the working OLLAMA_INTEGRATION.md
- Uses `requests` library for HTTP calls (lightweight, no async issues)
- Model validation can be skipped with `validate=False` if needed
- Caching is invalidated automatically when setting new models
