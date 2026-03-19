#!/usr/bin/env python3
"""
BitRAG - Flask Web GUI Version
A web-based GUI for chatting with PDF documents using RAG.
"""

import os
import sys
import warnings
import logging

# Add src to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

# Suppress warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import queue
import uuid

# Import BitRAG core modules
from bitrag.core.config import get_config
from bitrag.core.indexer import DocumentIndexer
from bitrag.core.query import QueryEngine

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max

# Global state
session_id = "default"
current_model = "llama3.2:1b"
indexer = None
query_engine = None

# Message queue for background tasks
task_queue = queue.Queue()


def initialize_components():
    """Initialize BitRAG components"""
    global indexer, query_engine

    print("Initializing BitRAG components...")

    # Initialize config
    config = get_config()

    # Initialize indexer
    indexer = DocumentIndexer(session_id)

    # Initialize query engine
    query_engine = QueryEngine(session_id, model=current_model)

    print("Initialization complete!")


@app.route("/")
def index():
    """Main chat page"""
    return render_template("index.html")


@app.route("/documents")
def documents_page():
    """Documents management page"""
    return render_template("documents.html")


@app.route("/settings")
def settings_page():
    """Settings page"""
    return render_template("settings.html")


# ==================== API Endpoints ====================


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process chat message"""
    global query_engine

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    if not indexer or indexer.get_document_count() == 0:
        return jsonify(
            {"error": "No documents indexed", "message": "Please upload PDF documents first"}
        ), 400

    try:
        # Get streaming response
        response_text = ""
        sources = []

        for chunk in query_engine.query_streaming(question):
            if chunk["type"] == "sources":
                sources = chunk["sources"]
            elif chunk["type"] == "chunk":
                response_text += chunk["delta"]
            elif chunk["type"] == "done":
                response_text = chunk["response"]

        return jsonify(
            {
                "question": question,
                "response": response_text,
                "sources": sources,
                "model": query_engine.get_current_model()["model"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """Process chat message with streaming"""
    from flask import Response
    import json

    global query_engine

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Empty question"}), 400

    if not indexer or indexer.get_document_count() == 0:
        return jsonify(
            {"error": "No documents indexed", "message": "Please upload PDF documents first"}
        ), 400

    def generate():
        try:
            for chunk in query_engine.query_streaming(question):
                if chunk["type"] == "sources":
                    yield f"data: {json.dumps({'type': 'sources', 'sources': chunk['sources']})}\n\n"
                elif chunk["type"] == "chunk":
                    yield f"data: {json.dumps({'type': 'chunk', 'text': chunk['delta']})}\n\n"
                elif chunk["type"] == "done":
                    yield f"data: {json.dumps({'type': 'done', 'response': chunk['response']})}\n\n"
                elif chunk["type"] == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': chunk['message']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get list of indexed documents"""
    global indexer

    if not indexer:
        return jsonify([])

    docs = indexer.list_documents()
    return jsonify(docs)


@app.route("/api/documents", methods=["POST"])
def upload_document():
    """Upload and index a document"""
    global indexer

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        # Save file temporarily
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(temp_path)

        # Index the document
        doc_id = indexer.index_document(temp_path)

        # Clean up temp file
        os.remove(temp_path)

        return jsonify({"success": True, "doc_id": doc_id, "filename": file.filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<path:filename>", methods=["DELETE"])
def delete_document(filename):
    """Delete a document"""
    global indexer

    try:
        indexer.delete_document_by_filename(filename)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/count", methods=["GET"])
def get_document_count():
    """Get document count"""
    global indexer

    if not indexer:
        return jsonify({"count": 0})

    return jsonify({"count": indexer.get_document_count()})


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
                        models.append(parts[0])
            return jsonify({"models": models if models else ["llama3.2:1b"]})
    except Exception as e:
        pass

    return jsonify({"models": ["llama3.2:1b"]})


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get current settings"""
    global current_model, query_engine, indexer

    return jsonify(
        {
            "model": current_model,
            "document_count": indexer.get_document_count() if indexer else 0,
            "session_id": session_id,
        }
    )


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update settings"""
    global current_model, query_engine

    data = request.get_json()
    new_model = data.get("model")

    if new_model and new_model != current_model:
        current_model = new_model
        if query_engine:
            query_engine.set_model(current_model)

    return jsonify({"success": True, "model": current_model})


@app.route("/api/system/info", methods=["GET"])
def get_system_info():
    """Get system information"""
    global indexer, query_engine

    config = get_config()

    info = {
        "project_root": PROJECT_ROOT,
        "data_dir": config.data_dir,
        "chroma_dir": config.chroma_dir,
        "embedding_model": config.embedding_model,
        "default_model": config.default_model,
        "ollama_base_url": config.ollama_base_url,
        "chunk_size": config.chunk_size,
        "top_k": config.top_k,
        "session_id": session_id,
        "document_count": indexer.get_document_count() if indexer else 0,
        "current_model": query_engine.get_current_model() if query_engine else {},
    }

    # Check Ollama
    import subprocess

    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            info["ollama_status"] = "running"
            lines = result.stdout.strip().split("\n")[1:]
            info["ollama_models"] = [line.split()[0] for line in lines if line.strip()]
        else:
            info["ollama_status"] = "not responding"
    except FileNotFoundError:
        info["ollama_status"] = "not installed"
    except Exception as e:
        info["ollama_status"] = f"error: {str(e)}"

    return jsonify(info)


@app.route("/favicon.ico")
def favicon():
    """Serve favicon"""
    return send_from_directory(os.path.join(SCRIPT_DIR, "static"), "favicon.ico")


def main():
    """Main entry point"""
    # Initialize components
    initialize_components()

    # Run Flask app
    print("\n" + "=" * 50)
    print("  BitRAG Flask Web Interface")
    print("=" * 50)
    print("\n🌐 Opening http://localhost:5000")
    print("\nPress CTRL+C to stop the server\n")

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


if __name__ == "__main__":
    main()
