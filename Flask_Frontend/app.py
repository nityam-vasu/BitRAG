#!/usr/bin/env python3
"""
BitRAG - Flask Web GUI (Using Custom Frontend)
Serves the React frontend and provides API endpoints for BitRAG.
Lazy initialization - components are only loaded when first requested.
"""

import os
import sys
import warnings
import logging
import threading

# Add src to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "Flask_Frontend", "dist")

sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

# Suppress warnings BEFORE importing libraries
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Filter all warnings
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.CRITICAL)
logging.getLogger("sentence_transformers").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)
logging.getLogger("llama_index").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("ollama._client").setLevel(logging.CRITICAL)

from flask import Flask, send_from_directory, jsonify, request, Response
from flask_cors import CORS
import uuid
import time
import json

# Import BitRAG core modules
from bitrag.core.config import get_config
from bitrag.core.indexer import DocumentIndexer
from bitrag.core.query import QueryEngine

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.secret_key = os.urandom(24)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max

# Global state - lazy initialization
session_id = "default"
current_model = "llama3.2:1b"
ollama_port = "11434"
hybrid_mode = 0
dual_mode = False
dual_model1 = "llama3.2:1b"
dual_model2 = "deepseek-r1:1.5b"

indexer = None
query_engine = None
initializing = False
initialized = False
init_lock = threading.Lock()


def initialize_components():
    """Initialize BitRAG components (called lazily on first request)"""
    global indexer, query_engine, initialized, initializing

    # Double-check with lock to avoid race conditions
    if initialized:
        return

    with init_lock:
        if initialized:
            return

        initializing = True
        print("\n" + "=" * 50)
        print("  BitRAG Backend - Initializing")
        print("=" * 50)

        try:
            # Initialize config (fast)
            config = get_config()
            print("✓ Configuration loaded")

            # Initialize indexer
            print("✓ Initializing indexer...", end=" ")
            sys.stdout.flush()
            start_time = time.time()
            indexer = DocumentIndexer(session_id)
            print(f"done ({time.time() - start_time:.1f}s)")

            # Initialize query engine (connects to Ollama)
            print("✓ Connecting to Ollama...", end=" ")
            sys.stdout.flush()
            start_time = time.time()
            query_engine = QueryEngine(session_id, model=current_model)
            print(f"done ({time.time() - start_time:.1f}s)")

            initialized = True
            print("\n" + "=" * 50)
            print("  BitRAG Backend Ready!")
            print("=" * 50 + "\n")

        except Exception as e:
            print(f"\n✗ Initialization failed: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            initializing = False


def ensure_initialized():
    """Ensure components are initialized on first request"""
    global initialized, initializing

    if initialized:
        return True

    if not initializing:
        # Start initialization in background thread
        init_thread = threading.Thread(target=initialize_components, daemon=True)
        init_thread.start()

    # Wait for initialization to complete (with timeout)
    start_wait = time.time()
    while not initialized and (time.time() - start_wait) < 30:
        time.sleep(0.1)

    return initialized


# ==================== Web Routes ====================


@app.route("/")
def index():
    """Serve the React frontend"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files from React build"""
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except:
        return send_from_directory(FRONTEND_DIR, "index.html")


# ==================== API Endpoints ====================


@app.route("/api/status", methods=["GET"])
def api_status():
    """Check API status without initializing"""
    return jsonify(
        {
            "status": "ready" if initialized else "initializing",
            "message": "Server is running" if initialized else "Server starting up...",
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process chat message"""
    if not ensure_initialized():
        return jsonify(
            {"error": "Server starting up", "message": "Please wait a moment and try again"}
        ), 503

    data = request.get_json()
    question = data.get("query", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    if not indexer or indexer.get_document_count() == 0:
        return jsonify(
            {"error": "No documents indexed", "message": "Please upload PDF documents first"}
        ), 400

    try:
        response_text = ""
        sources = []
        thinking = []

        thinking.append("1. First, I need to search for relevant documents")
        thinking.append("2. Extract key information from retrieved context")
        thinking.append("3. Formulate a comprehensive response")

        for chunk in query_engine.query_streaming(question):
            if chunk["type"] == "sources":
                sources = chunk["sources"]
            elif chunk["type"] == "chunk":
                delta = chunk.get("delta") or chunk.get("text", "")
                response_text += delta
            elif chunk["type"] == "done":
                response_text = chunk["response"]

        source_names = [s.get("metadata", {}).get("file_name", "Unknown") for s in sources]

        return jsonify(
            {
                "id": str(uuid.uuid4()),
                "type": "assistant",
                "thinking": "\n".join(thinking),
                "output": response_text,
                "sources": source_names,
            }
        )

    except Exception as e:
        return jsonify(
            {
                "error": str(e),
                "output": f"Error: {str(e)}",
                "thinking": "An error occurred while processing your request.",
                "sources": [],
            }
        ), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """Process chat message with streaming (SSE)"""
    if not ensure_initialized():
        return Response(
            f"data: {json.dumps({'type': 'error', 'message': 'Server starting up...'})}\n\n",
            mimetype="text/event-stream",
        )

    data = request.get_json()
    question = data.get("query", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    if not indexer or indexer.get_document_count() == 0:
        return jsonify(
            {"error": "No documents indexed", "message": "Please upload PDF documents first"}
        ), 400

    def generate():
        try:
            thinking_steps = [
                "1. First, I need to search for relevant documents",
                "2. Extract key information from retrieved context",
                "3. Formulate a comprehensive response",
            ]

            yield f"data: {json.dumps({'type': 'thinking', 'thinking': thinking_steps})}\n\n"

            for chunk in query_engine.query_streaming(question):
                if chunk["type"] == "sources":
                    source_names = [
                        s.get("metadata", {}).get("file_name", "Unknown") for s in chunk["sources"]
                    ]
                    yield f"data: {json.dumps({'type': 'sources', 'sources': source_names})}\n\n"
                elif chunk["type"] == "chunk":
                    delta = chunk.get("delta") or chunk.get("text", "")
                    yield f"data: {json.dumps({'type': 'chunk', 'output': delta})}\n\n"
                elif chunk["type"] == "done":
                    yield f"data: {json.dumps({'type': 'done', 'output': chunk['response']})}\n\n"
                elif chunk["type"] == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': chunk['message']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get list of indexed documents"""
    if not ensure_initialized():
        return jsonify([])

    if not indexer:
        return jsonify([])

    docs = indexer.list_documents()

    result = []
    for doc in docs:
        result.append({"id": doc.get("id", ""), "name": doc.get("file_name", "Unknown")})

    return jsonify(result)


@app.route("/api/documents", methods=["POST"])
def upload_document():
    """Upload and index a document"""
    if not ensure_initialized():
        return jsonify(
            {"error": "Server starting up", "message": "Please wait a moment and try again"}
        ), 503

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(temp_path)
        doc_id = indexer.index_document(temp_path)
        os.remove(temp_path)

        return jsonify(
            {
                "success": True,
                "id": doc_id,
                "name": file.filename,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    """Delete a document"""
    if not ensure_initialized():
        return jsonify(
            {"error": "Server starting up", "message": "Please wait a moment and try again"}
        ), 503

    try:
        indexer.delete_document_by_filename(doc_id)
        return jsonify({"success": True})
    except Exception as e:
        try:
            indexer.delete_document(doc_id)
            return jsonify({"success": True})
        except:
            return jsonify({"error": str(e)}), 500


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available Ollama models"""
    import subprocess

    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        if model_name not in models:
                            models.append(model_name)

            return jsonify({"models": models if models else ["llama3.2:1b"]})
    except Exception:
        pass

    return jsonify({"models": ["llama3.2:1b"]})


@app.route("/api/models/download", methods=["POST"])
def download_model():
    """Download an Ollama model"""
    import subprocess

    data = request.get_json()
    model_name = data.get("model", "")

    if not model_name:
        return jsonify({"error": "No model specified"}), 400

    try:
        result = subprocess.run(
            ["ollama", "pull", model_name], capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return jsonify({"success": True, "message": f"Model {model_name} downloaded"})
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/models/delete", methods=["POST"])
def delete_model():
    """Delete an Ollama model"""
    import subprocess

    data = request.get_json()
    model_name = data.get("model", "")

    if not model_name:
        return jsonify({"error": "No model specified"}), 400

    try:
        result = subprocess.run(
            ["ollama", "rm", model_name], capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return jsonify({"success": True, "message": f"Model {model_name} deleted"})
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get current settings"""
    if not ensure_initialized():
        return jsonify(
            {
                "model": current_model,
                "ollamaPort": ollama_port,
                "hybridMode": hybrid_mode,
                "dualMode": dual_mode,
                "model1": dual_model1,
                "model2": dual_model2,
                "documentCount": 0,
            }
        )

    return jsonify(
        {
            "model": current_model,
            "ollamaPort": ollama_port,
            "hybridMode": hybrid_mode,
            "dualMode": dual_mode,
            "model1": dual_model1,
            "model2": dual_model2,
            "documentCount": indexer.get_document_count() if indexer else 0,
        }
    )


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update settings"""
    global \
        current_model, \
        ollama_port, \
        hybrid_mode, \
        dual_mode, \
        dual_model1, \
        dual_model2, \
        query_engine

    data = request.get_json()

    new_model = data.get("model")
    if new_model and new_model != current_model:
        current_model = new_model
        if query_engine:
            try:
                query_engine.set_model(current_model)
            except Exception:
                pass

    new_port = data.get("ollamaPort")
    if new_port:
        ollama_port = new_port

    new_hybrid = data.get("hybridMode")
    if new_hybrid is not None:
        hybrid_mode = new_hybrid

    new_dual = data.get("dualMode")
    if new_dual is not None:
        dual_mode = new_dual

    new_model1 = data.get("model1")
    if new_model1:
        dual_model1 = new_model1

    new_model2 = data.get("model2")
    if new_model2:
        dual_model2 = new_model2

    return jsonify(
        {
            "success": True,
            "model": current_model,
            "ollamaPort": ollama_port,
            "hybridMode": hybrid_mode,
            "dualMode": dual_mode,
            "model1": dual_model1,
            "model2": dual_model2,
        }
    )


@app.route("/api/system/info", methods=["GET"])
def get_system_info():
    """Get system information"""
    ensure_initialized()

    config = get_config()

    info = {
        "sessionId": session_id,
        "documentCount": indexer.get_document_count() if indexer else 0,
        "embeddingModel": config.embedding_model,
        "chunkSize": config.chunk_size,
        "topK": config.top_k,
    }

    import subprocess

    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info["ollamaStatus"] = "running"
            lines = result.stdout.strip().split("\n")[1:]
            info["ollamaModels"] = [line.split()[0] for line in lines if line.strip()]
        else:
            info["ollamaStatus"] = "not responding"
    except FileNotFoundError:
        info["ollamaStatus"] = "not installed"
    except Exception as e:
        info["ollamaStatus"] = f"error: {str(e)}"

    return jsonify(info)


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  BitRAG Flask Backend")
    print("  Powered by Ollama & ChromaDB")
    print("=" * 60)
    print("\n✓ Server ready - initialization will happen on first request")
    print("\n🌐 Web server: http://localhost:5000")
    print("Press CTRL+C to stop\n")

    # Run Flask app without pre-initialization
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    import json

    main()
