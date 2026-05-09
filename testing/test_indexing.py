#!/usr/bin/env python3
"""
BitRAG Indexing Test Script

Tests document indexing performance and stores results.

Usage:
    python test_indexing.py --input <file_path> [--output <filename>.txt]
    python test_indexing.py -i input.pdf -o results.txt
    python test_indexing.py --input document.pdf --chunk-size 1024 --model sentence-transformers/all-MiniLM-L6-v2
"""

import argparse
import os
import sys
import time
import json
import platform
import subprocess
import tempfile

# Add src to path - this must be FIRST to avoid bitrag.py conflict
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = _SCRIPT_DIR
_SRC_PATH = os.path.join(_PROJECT_ROOT, "src")

# Remove any conflicting paths first (like '' which would pick up bitrag.py)
if "" in sys.path:
    sys.path.remove("")
if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)

# Add src at the BEGINNING to ensure it's found before any other paths
sys.path.insert(0, _SRC_PATH)

# Force CPU-only mode (disable CUDA GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None
    print("Warning: psutil not installed - some metrics disabled")

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_SRC_PATH = os.path.join(_PROJECT_ROOT, "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)


def get_venv_python() -> str:
    """Get Python path from venv or .venv."""
    if (Path(_PROJECT_ROOT) / ".venv/bin/python").exists():
        return str((Path(_PROJECT_ROOT) / ".venv/bin/python").resolve())
    elif (Path(_PROJECT_ROOT) / "venv/bin/python").exists():
        return str((Path(_PROJECT_ROOT) / "venv/bin/python").resolve())
    return sys.executable


class SystemInfo:
    """Collect system information."""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }

        # Try to get GPU info (if available)
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,driver_version,memory.total,memory.used",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_info = result.stdout.strip().split(",")
                info["gpu_info"] = gpu_info[0].strip() if len(gpu_info) > 0 else "Unknown"

                # Parse memory - handle formats like "580.126.09 MiB" or "4096MiB"
                def parse_memory(mem_str):
                    mem_str = gpu_info[1].strip() if len(gpu_info) > 1 else "0"
                    mem_str = mem_str.replace("MiB", "").replace("Mi", "").replace("GB", "").strip()
                    try:
                        return int(float(mem_str))
                    except:
                        return 0

                info["gpu_memory_total_mb"] = parse_memory(gpu_info[1]) if len(gpu_info) > 1 else 0
                info["gpu_memory_used_mb"] = parse_memory(gpu_info[2]) if len(gpu_info) > 2 else 0
            else:
                info["gpu_info"] = "Not available"
                info["gpu_memory_total_mb"] = 0
                info["gpu_memory_used_mb"] = 0
        except (subprocess.TimeoutExpired, FileNotFoundError, IndexError, ValueError):
            info["gpu_info"] = "Not available"
            info["gpu_memory_total_mb"] = 0
            info["gpu_memory_used_mb"] = 0

        return info


class PerformanceMetrics:
    """Class to collect and store performance metrics."""

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.embedding_time = 0.0
        self.vector_storage_time = 0.0
        self.memory_used_mb = 0.0
        self.peak_memory_mb = 0.0
        self.cpu_usage_percent = 0.0

    def start(self):
        """Start timing."""
        self.start_time = time.time()
        self.peak_memory_mb = self.get_memory_usage()

    def stop(self):
        """Stop timing."""
        self.end_time = time.time()
        self.memory_used_mb = self.get_memory_usage() - self.get_initial_memory()

    def get_total_time(self) -> float:
        """Get total elapsed time."""
        return self.end_time - self.start_time

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def get_initial_memory(self) -> float:
        """Get initial memory usage."""
        process = psutil.Process()
        self._initial_memory = process.memory_info().rss / (1024 * 1024)
        return self._initial_memory

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)


class DocumentIndexerTest:
    """Test class for document indexing."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.metrics = PerformanceMetrics()
        self.document_info: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}

    def get_document_info(self) -> Dict[str, Any]:
        """Extract document information."""
        file_path = Path(self.args.input)

        info = {
            "document_type": file_path.suffix.lower().replace(".", ""),
            "file_size_bytes": file_path.stat().st_size,
            "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
        }

        # Additional info based on document type
        if info["document_type"] == "pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(file_path)
                info["pages"] = len(reader.pages)
                info["total_characters"] = sum(len(page.extract_text()) for page in reader.pages)
            except Exception:
                info["pages"] = 0
                info["total_characters"] = 0
        else:
            # For text files
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    info["total_characters"] = len(content)
                    info["total_words"] = len(content.split())
            except Exception:
                info["total_characters"] = 0
                info["total_words"] = 0

        return info

    def run_indexing(self) -> Dict[str, Any]:
        """Run the indexing process."""
        from bitrag.core.config import Config
        from bitrag.core.indexer import DocumentIndexer

        # Initialize config
        temp_dir = tempfile.mkdtemp()
        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            chunk_size=self.args.chunk_size,
            chunk_overlap=self.args.chunk_overlap,
            embedding_model=self.args.model,
        )

        try:
            # Get initial memory
            self.metrics.get_initial_memory()
            self.metrics.start()

            # Create indexer
            indexer = DocumentIndexer(session_id="test_session")

            # Time embedding generation
            embedding_start = time.time()
            doc_id = indexer.index_document(self.args.input)
            embedding_end = time.time()

            self.metrics.embedding_time = embedding_end - embedding_start

            # Get document count
            doc_count = indexer.get_document_count()

            self.metrics.stop()
            self.metrics.cpu_usage_percent = self.metrics.get_cpu_usage()

            return {
                "success": True,
                "document_id": doc_id,
                "total_chunks": doc_count,
                "error": None,
            }
        except Exception as e:
            self.metrics.stop()
            return {
                "success": False,
                "document_id": None,
                "total_chunks": 0,
                "error": str(e),
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def generate_output(self) -> str:
        """Generate output content."""
        sys_info = SystemInfo.get_system_info()
        timestamp = datetime.now().isoformat()
        timestamp_unix = int(time.time())

        output = f"""=== BitRAG Indexing Test Results ===

[Metadata]
timestamp: {timestamp}
timestamp_unix: {timestamp_unix}
input_file: {self.args.input}
output_file: {self.args.output}

[System Information]
platform: {sys_info["platform"]}
python_version: {sys_info["python_version"]}
cpu_count_physical: {sys_info["cpu_count_physical"]}
cpu_count_logical: {sys_info["cpu_count_logical"]}
total_memory_gb: {sys_info["total_memory_gb"]}
available_memory_gb: {sys_info["available_memory_gb"]}
gpu_info: {sys_info["gpu_info"]}
gpu_memory_total_mb: {sys_info.get("gpu_memory_total_mb", 0)}
gpu_memory_used_mb: {sys_info.get("gpu_memory_used_mb", 0)}

[Indexing Configuration]
chunk_size: {self.args.chunk_size}
chunk_overlap: {self.args.chunk_overlap}
embedding_model: {self.args.model}
vector_store: ChromaDB

[Performance Metrics]
total_indexing_time_seconds: {self.metrics.get_total_time():.4f}
embedding_generation_time_seconds: {self.metrics.embedding_time:.4f}
vector_storage_time_seconds: {self.metrics.vector_storage_time:.4f}
memory_used_mb: {self.metrics.memory_used_mb:.2f}
peak_memory_mb: {self.metrics.peak_memory_mb:.2f}
cpu_usage_percent: {self.metrics.cpu_usage_percent:.2f}
memory_delta_mb: {self.metrics.memory_used_mb:.2f}

[Document Information]
document_type: {self.document_info.get("document_type", "unknown")}
file_size_bytes: {self.document_info.get("file_size_bytes", 0)}
file_size_mb: {self.document_info.get("file_size_mb", 0)}
total_characters: {self.document_info.get("total_characters", 0)}
total_words: {self.document_info.get("total_words", 0)}
total_chunks: {self.results.get("total_chunks", 0)}
pages: {self.document_info.get("pages", "N/A")}

[Results]
document_id: {self.results.get("document_id", "None")}
indexed: {self.results.get("success", False)}
error: {self.results.get("error", "None")}
"""

        return output

    def save_output(self, content: str):
        """Save output to file."""
        # Create results directory if it doesn't exist
        results_dir = Path(self.args.results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = results_dir / self.args.output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Results saved to: {output_path}")

    def run(self):
        """Run the indexing test."""
        # Check if input file exists
        if not os.path.exists(self.args.input):
            print(f"Error: Input file not found: {self.args.input}")
            sys.exit(1)

        # Get document info
        print(f"Processing: {self.args.input}")
        self.document_info = self.get_document_info()

        # Run indexing
        print("Running indexing...")
        self.results = self.run_indexing()

        # Generate and save output
        output_content = self.generate_output()
        self.save_output(output_content)

        # Print summary
        print("\n=== Summary ===")
        print(f"Total indexing time: {self.metrics.get_total_time():.4f}s")
        print(f"Embedding time: {self.metrics.embedding_time:.4f}s")
        print(f"Memory used: {self.metrics.memory_used_mb:.2f} MB")
        print(f"Chunks: {self.results.get('total_chunks', 0)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BitRAG Indexing Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Input/Output
    parser.add_argument(
        "--input", "-i", required=True, help="Path to file to index (PDF, TXT, etc.)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="indexing_results.txt",
        help="Output filename (default: indexing_results.txt)",
    )
    parser.add_argument(
        "--results-dir",
        "-r",
        default="results",
        help="Directory to save results (default: results)",
    )

    # Indexing options
    parser.add_argument(
        "--chunk-size", type=int, default=512, help="Chunk size for text splitting (default: 512)"
    )
    parser.add_argument(
        "--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model to use (default: sentence-transformers/all-MiniLM-L6-v2)",
    )

    args = parser.parse_args()

    # Run test
    tester = DocumentIndexerTest(args)
    tester.run()


if __name__ == "__main__":
    main()
