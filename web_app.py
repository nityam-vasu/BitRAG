#!/usr/bin/env python3
"""
BitRAG - Flask Web GUI
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
PROJECT_ROOT = SCRIPT_DIR
# FRONTEND_DIR is the built React frontend
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

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
import requests

# Import BitRAG core modules
from bitrag.core.config import get_config
from bitrag.core.indexer import DocumentIndexer
from bitrag.core.query import QueryEngine
from bitrag.core.graph_builder import GraphBuilder, get_graph_builder
from bitrag.core.summary_generator import SummaryGenerator, get_summary_generator
from bitrag.core.tag_extractor import TagExtractor, get_tag_extractor

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.secret_key = os.urandom(24)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "web", "uploads")
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
graph_builder = None  # GraphBuilder instance
initializing = False
initialized = False
init_lock = threading.Lock()

# Reasoning models that have internal thought process
REASONING_MODELS = [
    "deepseek-r1",
    "deepseek-coder-v2",
    "qwq",  # Qwen with reasoning
    "qwen-coder-turbo",
    "llama3.1-gradient",  # Some Llama variants with reasoning
    "r1",
    "r1-lite",
    "r1-distill",
    "phi4-reasoning",
    "gemma3 Reasoning",  # Some variants
]


def is_reasoning_model(model_name: str) -> bool:
    """Check if the model is a reasoning model"""
    if not model_name:
        return False
    model_lower = model_name.lower()
    return any(rm in model_lower for rm in REASONING_MODELS)


def extract_thinking(response: str, model_name: str) -> tuple[str, str]:
    """
    Extract thinking from reasoning models.

    Returns tuple of (thinking, final_response)
    For reasoning models: extracts content between <think> and </think> tags
    For non-reasoning: returns placeholder thinking and original response
    """
    if not is_reasoning_model(model_name):
        # For non-reasoning models, return generic thinking steps
        return ("Analyzing your question and searching through indexed documents...", response)

    # Try to extract thinking from common reasoning formats
    # Format 1: <think>...</think>
    if "<think>" in response and "</think>" in response:
        start = response.find("<think>") + len("<think>")
        end = response.find("</think>")
        thinking = response[start:end].strip()
        final_response = response[end + len("</think>") :].strip()
        return thinking, final_response

    # Format 2: \n\n者 (for some Chinese models)
    # Just return the whole response as-is for now if no tags found

    # If no thinking found, return the whole response as final
    return "", response


def generate_thinking_steps(question: str, sources_count: int, has_context: bool) -> str:
    """Generate dynamic thinking steps based on the query"""
    steps = []

    # Step 1: Understanding the question
    question_words = len(question.split())
    steps.append(f"1. Analyzing your question ({question_words} words)...")

    # Step 2: Searching documents
    if has_context:
        steps.append(f"2. Searching through {sources_count} document(s) for relevant context...")
    else:
        steps.append("2. Searching through indexed documents...")

    # Step 3: Processing context
    steps.append("3. Extracting relevant information from found context...")

    # Step 4: Generating response
    if is_reasoning_model(current_model):
        steps.append("4. Applying reasoning to formulate the best answer...")
    else:
        steps.append("4. Synthesizing information into a coherent response...")

    return "\n".join(steps)


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
            print("\n⚠ Server will start but some features may not work until Ollama is available")
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

    # Return True if initialized, False otherwise
    return initialized


# ==================== Web Routes ====================


@app.route("/")
def index():
    """Serve the React frontend"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/debug")
def debug():
    """Debug endpoint to check server status"""
    return jsonify(
        {
            "status": "ok",
            "frontend_dir": FRONTEND_DIR,
            "initialized": initialized,
            "initializing": initializing,
        }
    )


@app.route("/graph")
@app.route("/settings")
@app.route("/documents")
@app.route("/<path:path>")
def serve_static(path=""):
    """Serve static files from React build"""
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except Exception as e:
        print(f"Static file error: {e}")
        return send_from_directory(FRONTEND_DIR, "index.html")


# ==================== API Endpoints ====================


@app.route("/api/status", methods=["GET"])
def api_status():
    """Check API status - now always ready since we initialize at startup"""
    return jsonify(
        {
            "status": "ready" if initialized else "initializing",
            "message": "Server is running and ready" if initialized else "Server is starting up...",
            "initialized": initialized,
            "initializing": initializing,
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
        raw_response = ""  # Store full response to extract thinking later

        # Get initial thinking steps based on model type
        thinking_steps = generate_thinking_steps(question, 0, False)

        for chunk in query_engine.query_streaming(question):
            if chunk["type"] == "sources":
                sources = chunk["sources"]
                # Update thinking with source count
                thinking_steps = generate_thinking_steps(question, len(sources), len(sources) > 0)
            elif chunk["type"] == "chunk":
                delta = chunk.get("delta") or chunk.get("text", "")
                raw_response += delta
            elif chunk["type"] == "done":
                raw_response = chunk.get("response", raw_response)

        # Extract thinking from reasoning models
        thinking, response_text = extract_thinking(raw_response, current_model)

        # If no thinking was extracted (non-reasoning model or no special format)
        if not thinking:
            thinking = thinking_steps

        source_names = [s.get("metadata", {}).get("file_name", "Unknown") for s in sources]

        return jsonify(
            {
                "id": str(uuid.uuid4()),
                "type": "assistant",
                "thinking": thinking,
                "output": response_text,
                "sources": source_names,
                "model": current_model,
                "is_reasoning_model": is_reasoning_model(current_model),
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
            # Get initial thinking based on model type
            thinking_steps = generate_thinking_steps(question, 0, False)

            # For reasoning models, indicate that reasoning is happening
            if is_reasoning_model(current_model):
                yield f"data: {json.dumps({'type': 'thinking', 'thinking': 'Starting reasoning process...'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'thinking', 'thinking': thinking_steps})}\n\n"

            raw_response = ""
            sources_count = 0

            for chunk in query_engine.query_streaming(question):
                if chunk["type"] == "sources":
                    sources_count = len(chunk["sources"])
                    # Update thinking with source info
                    thinking_steps = generate_thinking_steps(question, sources_count, True)
                    source_names = [
                        s.get("metadata", {}).get("file_name", "Unknown") for s in chunk["sources"]
                    ]
                    yield f"data: {json.dumps({'type': 'sources', 'sources': source_names})}\n\n"
                elif chunk["type"] == "chunk":
                    delta = chunk.get("delta") or chunk.get("text", "")
                    raw_response += delta
                    yield f"data: {json.dumps({'type': 'chunk', 'output': delta})}\n\n"
                elif chunk["type"] == "done":
                    # Extract thinking if it's a reasoning model
                    raw_response = chunk.get("response", raw_response)
                    thinking, final_response = extract_thinking(raw_response, current_model)

                    if thinking and is_reasoning_model(current_model):
                        yield f"data: {json.dumps({'type': 'thinking', 'thinking': thinking, 'is_reasoning': True})}\n\n"

                    yield f"data: {json.dumps({'type': 'done', 'output': final_response})}\n\n"
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
    try:
        if not ensure_initialized():
            return jsonify(
                {"error": "Server starting up", "message": "Please wait a moment and try again"}
            ), 503

        if "file" not in request.files:
            return jsonify(
                {"error": "No file provided", "message": "Please select a file to upload"}
            ), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected", "message": "Please select a file"}), 400

        # Validate file type
        allowed_extensions = {".pdf", ".txt", ".md", ".doc", ".docx"}
        import os

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            return jsonify(
                {
                    "error": "Invalid file type",
                    "message": f"File type {ext} not supported. Please upload PDF, TXT, MD, or DOC files.",
                }
            ), 400

        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(temp_path)

        # Check if file was saved
        if not os.path.exists(temp_path):
            return jsonify(
                {"error": "File save failed", "message": "Could not save uploaded file"}
            ), 500

        doc_id = indexer.index_document(temp_path)
        os.remove(temp_path)

        return jsonify(
            {
                "success": True,
                "id": doc_id,
                "name": file.filename,
            }
        )

    except FileNotFoundError as e:
        return jsonify({"error": "File not found", "message": str(e)}), 404
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"Error indexing document: {e}")
        print(error_details)
        return jsonify(
            {
                "error": "Indexing failed",
                "message": str(e),
                "details": "Check if the file is a valid PDF document",
            }
        ), 500


@app.route("/api/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    """Delete a document"""
    global graph_builder

    if not ensure_initialized():
        return jsonify(
            {"error": "Server starting up", "message": "Please wait a moment and try again"}
        ), 503

    try:
        indexer.delete_document_by_filename(doc_id)

        # Clear from graph builder cache if exists
        if graph_builder is not None and doc_id in graph_builder._cache:
            del graph_builder._cache[doc_id]

        return jsonify({"success": True})
    except Exception as e:
        try:
            indexer.delete_document(doc_id)
            return jsonify({"success": True})
        except:
            return jsonify({"error": str(e)}), 500


@app.route("/api/documents/<doc_id>/regenerate-tags", methods=["POST"])
def regenerate_document_tags(doc_id):
    """Regenerate summary and tags for a specific document."""
    global graph_builder

    if not ensure_initialized():
        return jsonify(
            {"error": "Server not initialized", "message": "Please wait and try again"}
        ), 503

    try:
        # Get document info
        docs = indexer.list_documents()
        doc_info = None
        for doc in docs:
            if doc.get("id") == doc_id or doc.get("file_name") == doc_id:
                doc_info = doc
                break

        if not doc_info:
            return jsonify(
                {"error": "Document not found", "message": f"No document found with id '{doc_id}'"}
            ), 404

        # Get or create graph builder
        if graph_builder is None:
            graph_builder = GraphBuilder(indexer=indexer)

        # Regenerate metadata
        metadata = graph_builder.regenerate_document(
            doc_id=doc_id, file_name=doc_info.get("file_name", doc_id)
        )

        return jsonify(
            {
                "success": True,
                "document_id": doc_id,
                "metadata": {
                    "summary": metadata.summary,
                    "tags": metadata.tags,
                    "keywords": metadata.keywords,
                    "category": metadata.category,
                    "generated_at": metadata.generated_at,
                },
            }
        )

    except Exception as e:
        print(f"Error regenerating tags for {doc_id}: {e}")
        import traceback

        traceback.print_exc()
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
    # Check Ollama status using HTTP (same as system/info)
    # Use 127.0.0.1 to avoid IPv6 issues
    ollama_status = "not responding"
    try:
        response = requests.get(f"http://127.0.0.1:{ollama_port}/api/tags", timeout=2)
        if response.status_code == 200:
            ollama_status = "running"
    except:
        ollama_status = "not responding"

    # Get model settings from config
    config = get_config()

    if not ensure_initialized():
        return jsonify(
            {
                "model": current_model,
                "summary_model": getattr(config, "summary_model", "llama3.2:1b"),
                "tag_model": getattr(config, "tag_model", "llama3.2:1b"),
                "ollamaPort": ollama_port,
                "hybridMode": hybrid_mode,
                "dualMode": dual_mode,
                "model1": dual_model1,
                "model2": dual_model2,
                "documentCount": 0,
                "ollamaStatus": ollama_status,
            }
        )

    return jsonify(
        {
            "model": current_model,
            "summary_model": getattr(config, "summary_model", "llama3.2:1b"),
            "tag_model": getattr(config, "tag_model", "llama3.2:1b"),
            "ollamaPort": ollama_port,
            "hybridMode": hybrid_mode,
            "dualMode": dual_mode,
            "model1": dual_model1,
            "model2": dual_model2,
            "documentCount": indexer.get_document_count() if indexer else 0,
            "ollamaStatus": ollama_status,
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
        query_engine, \
        graph_builder

    data = request.get_json()

    new_model = data.get("model")
    if new_model and new_model != current_model:
        current_model = new_model
        if query_engine:
            try:
                query_engine.set_model(current_model)
            except Exception:
                pass

    # Update summary model
    new_summary_model = data.get("summary_model")
    if new_summary_model:
        config = get_config()
        config.summary_model = new_summary_model
        # Update graph builder if exists
        if graph_builder:
            graph_builder.summary_generator.set_model(new_summary_model)

    # Update tag model
    new_tag_model = data.get("tag_model")
    if new_tag_model:
        config = get_config()
        config.tag_model = new_tag_model
        # Update graph builder if exists
        if graph_builder:
            graph_builder.tag_extractor.set_model(new_tag_model)

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
            "summary_model": getattr(get_config(), "summary_model", "llama3.2:1b"),
            "tag_model": getattr(get_config(), "tag_model", "llama3.2:1b"),
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
    import psutil

    # Get CPU usage
    info["cpu"] = psutil.cpu_percent()

    # Get Memory usage
    memory = psutil.virtual_memory()
    info["memory"] = {
        "used": round(memory.used / (1024**3), 1),  # GB
        "total": round(memory.total / (1024**3), 1),  # GB
        "percent": memory.percent,
    }

    # Get GPU usage (using nvidia-smi if available)
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines and lines[0]:
                parts = lines[0].split(", ")
                if len(parts) >= 3:
                    info["gpu"] = {
                        "utilization": float(parts[0]),
                        "memory_used": round(int(parts[1]) / 1024, 1),  # GB
                        "memory_total": round(int(parts[2]) / 1024, 1),  # GB
                    }
                else:
                    info["gpu"] = {"utilization": 0, "memory_used": 0, "memory_total": 0}
            else:
                info["gpu"] = {"utilization": 0, "memory_used": 0, "memory_total": 0}
        else:
            info["gpu"] = {"utilization": 0, "memory_used": 0, "memory_total": 0}
    except FileNotFoundError:
        info["gpu"] = {"utilization": 0, "memory_used": 0, "memory_total": 0}
    except Exception as e:
        info["gpu"] = {"utilization": 0, "memory_used": 0, "memory_total": 0}

    # Check Ollama status - use 127.0.0.1 to avoid IPv6 issues
    try:
        # Use 127.0.0.1 instead of 'localhost' to bypass IPv6 resolution issues
        target_url = f"http://127.0.0.1:{ollama_port}/api/tags"
        response = requests.get(target_url, timeout=3)

        if response.status_code == 200:
            info["ollamaStatus"] = "running"
            data = response.json()
            info["ollamaModels"] = [m["name"] for m in data.get("models", [])]
        else:
            info["ollamaStatus"] = "error"
            info["ollamaError"] = f"Ollama returned status code {response.status_code}"

    except requests.exceptions.ConnectionError:
        info["ollamaStatus"] = "not responding"
        info["ollamaError"] = f"Failed to connect to Ollama at {target_url}. Is it running?"
    except requests.exceptions.Timeout:
        info["ollamaStatus"] = "not responding"
        info["ollamaError"] = f"Timeout connecting to Ollama at {target_url}"
    except Exception as e:
        info["ollamaStatus"] = "error"
        info["ollamaError"] = str(e)[:200]

    return jsonify(info)


@app.route("/api/graph", methods=["GET"])
def get_graph_data():
    """Get graph data for document visualization with AI-generated summaries and tags.

    Query params:
        - refresh: If 'true', force regeneration of all metadata
    """
    global graph_builder

    if not ensure_initialized():
        return jsonify({"nodes": [], "links": []})

    if not indexer:
        return jsonify({"nodes": [], "links": []})

    try:
        # Check for refresh parameter
        force_refresh = request.args.get("refresh", "false").lower() == "true"

        # Create graph builder if not exists
        if graph_builder is None:
            config = get_config()
            # Create generators with configured models
            summary_gen = SummaryGenerator(
                model=getattr(config, "summary_model", config.default_model),
                ollama_base_url=config.ollama_base_url,
            )
            tag_gen = TagExtractor(
                model=getattr(config, "tag_model", config.default_model),
                ollama_base_url=config.ollama_base_url,
            )
            graph_builder = GraphBuilder(
                indexer=indexer,
                summary_generator=summary_gen,
                tag_extractor=tag_gen,
            )
            print(
                f"[Graph] Created GraphBuilder with summary_model={summary_gen.model}, tag_model={tag_gen.model}"
            )

        # Build graph data
        graph_data = graph_builder.build_graph(force_refresh=force_refresh)

        # Convert to dict for JSON response
        return jsonify(graph_data.to_dict())

    except Exception as e:
        print(f"Error generating graph data: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"nodes": [], "links": []})


@app.route("/api/graph/regenerate", methods=["GET"])
def regenerate_graph():
    """Regenerate entire graph with fresh metadata."""
    global graph_builder

    if not ensure_initialized():
        return jsonify({"error": "Server not initialized"}), 503

    try:
        # Clear existing builder to force regeneration
        if graph_builder is not None:
            graph_builder.clear_cache()

        # Create fresh builder
        graph_builder = GraphBuilder(indexer=indexer)

        # Build with fresh data
        graph_data = graph_builder.build_graph(force_refresh=True)

        return jsonify(
            {
                "success": True,
                "message": "Graph regenerated successfully",
                "stats": {
                    "nodes": len(graph_data.nodes),
                    "links": len(graph_data.links),
                },
            }
        )

    except Exception as e:
        print(f"Error regenerating graph: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/graph/info", methods=["GET"])
def graph_info():
    """Get information about the graph builder and cache status."""
    global graph_builder

    if not ensure_initialized():
        return jsonify({"error": "Server not initialized"}), 503

    if graph_builder is None:
        return jsonify(
            {
                "initialized": False,
                "cache_size": 0,
            }
        )

    return jsonify(
        {
            "initialized": True,
            "cache_size": len(graph_builder._cache),
            "use_llm": graph_builder.use_llm,
            "summary_model": graph_builder.summary_generator.model,
            "tag_model": graph_builder.tag_extractor.model,
        }
    )


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  BitRAG Flask Backend")
    print("  Powered by Ollama & ChromaDB")
    print("=" * 60)
    print("\n✓ Server ready - initialization will happen on first request")
    print("\n🌐 Web server: http://localhost:5000")
    print("Press CTRL+C to stop\n")

    # Run Flask app - initialization happens on first API request
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)


if __name__ == "__main__":
    import json

    main()
