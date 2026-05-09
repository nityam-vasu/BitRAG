#!/usr/bin/env python3
"""
BitRAG Inference Test Script

Tests LLM inference performance and stores results.

Usage:
    python test_inference.py --model <model_name> --query <user_query> [--output <filename>.txt]
    python test_inference.py -m llama3.2:1b -q "What is the document about?" -o results.txt
    python test_inference.py --model llama3.2:1b -q "Summarize" --temperature 0.5 --top-p 0.9
"""

import argparse
import os
import sys
import time
import json
import platform
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

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
        self.retrieval_time = 0.0
        self.llm_generation_time = 0.0
        self.time_to_first_token = 0.0
        self.time_per_token = 0.0
        self.tokens_generated = 0
        self.tokens_per_second = 0.0
        self.memory_used_mb = 0.0
        self.peak_memory_mb = 0.0
        self.cpu_usage_percent = 0.0
        self.gpu_memory_delta_mb = 0.0
        self._initial_memory = 0.0

    def start(self):
        """Start timing."""
        self.start_time = time.time()
        self.peak_memory_mb = self.get_memory_usage()
        self._initial_memory = self.get_memory_usage()

    def stop(self):
        """Stop timing."""
        self.end_time = time.time()
        self.memory_used_mb = self.get_memory_usage() - self._initial_memory

    def get_total_time(self) -> float:
        """Get total elapsed time."""
        return self.end_time - self.start_time

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)


class OllamaParams:
    """Container for Ollama parameters."""

    def __init__(self, args: argparse.Namespace):
        self.temperature = args.temperature
        self.top_p = args.top_p
        self.top_k = args.ollama_top_k
        self.ctx_size = args.ctx
        self.num_ctx = args.num_ctx
        self.repeat_penalty = args.repeat_penalty
        self.seed = args.seed
        self.num_gpu_layers = args.num_gpu_layers
        self.threads = args.threads
        self.batch_size = args.batch
        self.mmap = args.mmap
        self.numa = args.numa
        self.format = args.format

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "ctx_size": self.ctx_size,
            "num_ctx": self.num_ctx,
            "repeat_penalty": self.repeat_penalty,
            "seed": self.seed,
            "num_gpu_layers": self.num_gpu_layers,
            "threads": self.threads,
            "batch_size": self.batch_size,
            "mmap": self.mmap,
            "numa": self.numa,
            "format": self.format,
        }


class InferenceTest:
    """Test class for LLM inference."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.metrics = PerformanceMetrics()
        self.ollama_params = OllamaParams(args)
        self.query_info: Dict[str, Any] = {}
        self.response_info: Dict[str, Any] = {}
        self.sources: List[Dict[str, Any]] = []
        self.token_usage: Dict[str, Any] = {}
        self.model_info: Dict[str, Any] = {}
        self.indexing_info: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        self.reasoning_info: Dict[str, Any] = {}

    def run_inference(self) -> Dict[str, Any]:
        """Run the inference process."""
        from bitrag.core.config import Config
        from bitrag.core.query import QueryEngine

        # Initialize config
        temp_dir = tempfile.mkdtemp()
        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            chunk_size=self.args.chunk_size,
            chunk_overlap=self.args.chunk_overlap,
        )

        try:
            # Initialize query engine
            self.metrics.get_memory_usage()
            self.metrics.start()

            engine = QueryEngine(
                session_id="test_session",
                model=self.args.model,
                _skip_ollama_check=False,
            )

            # Run query
            retrieval_start = time.time()
            result = engine.query(self.args.query)
            retrieval_end = time.time()

            self.metrics.retrieval_time = retrieval_end - retrieval_start

            # Calculate metrics
            if "sources" in result:
                for source in result.get("sources", []):
                    self.sources.append(
                        {
                            "text": source.get("text", "")[:200],
                            "document": source.get("file_name", "unknown"),
                            "page": source.get("page", "N/A"),
                            "chunk_index": source.get("chunk_index", 0),
                            "similarity_score": source.get("score", 0.0),
                        }
                    )

            # Get token usage from response if available
            if "token_usage" in result:
                self.token_usage = result["token_usage"]
            else:
                # Estimate based on response length
                response_text = result.get("response", "")
                self.token_usage = {
                    "prompt_tokens": len(self.args.query) // 4,
                    "completion_tokens": len(response_text) // 4,
                    "total_tokens": (len(self.args.query) + len(response_text)) // 4,
                }

            self.metrics.stop()
            self.metrics.cpu_usage_percent = self.metrics.get_cpu_usage()

            # Detect reasoning if present
            response_text = result.get("response", "")
            reasoning_content = ""
            support_reasoning = 0

            # Check for thinking tags (common in reasoning models like DeepSeek)
            if "<think>" in response_text and "</think>" in response_text:
                support_reasoning = 1
                start = response_text.index("<think>") + len("<think>")
                end = response_text.index("</think>")
                reasoning_content = response_text[start:end].strip()
            # Also check for other reasoning patterns
            elif response_text.startswith("Thinking:") or "Reasoning:" in response_text[:200]:
                support_reasoning = 1
                # Try to extract reasoning
                lines = response_text.split("\n")
                reasoning_lines = []
                for line in lines:
                    if line.startswith("Thinking:") or line.startswith("Reasoning:"):
                        reasoning_lines.append(line.split(":", 1)[1].strip())
                    elif reasoning_lines and not line.strip().startswith(("#", "-", "=")):
                        reasoning_lines.append(line.strip())
                    elif line.strip().startswith(("Answer:", "Final:", "Response:")):
                        break
                reasoning_content = "\n".join(reasoning_lines)

            return {
                "success": True,
                "response": result.get("response", ""),
                "reasoning_content": reasoning_content,
                "support_reasoning": support_reasoning,
                "model": result.get("model", self.args.model),
                "error": None,
            }
        except Exception as e:
            self.metrics.stop()
            return {
                "success": False,
                "response": "",
                "model": self.args.model,
                "error": str(e),
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def generate_output(self) -> str:
        """Generate output content."""
        sys_info = SystemInfo.get_system_info()
        timestamp = datetime.now().isoformat()
        timestamp_unix = int(time.time())

        # Build sources string - concise format
        sources_list = []
        for i, src in enumerate(self.sources, 1):
            # Clean text: remove excessive whitespace/newlines
            text = src.get("text", "")
            # Replace newlines and multiple spaces with single space
            text = " ".join(text.split())
            # Truncate to 150 chars
            text = text[:150] + "..." if len(text) > 150 else text

            sources_list.append(
                f'[{i}] doc={src.get("document", "unknown")} page={src.get("page", "N/A")} chunk={src.get("chunk_index", 0)} score={src.get("similarity_score", 0):.4f} | "{text}"'
            )

        sources_str = "\n".join(sources_list) if sources_list else "(no sources retrieved)"

        # Calculate throughput
        throughput = 0.0
        if self.metrics.get_total_time() > 0:
            throughput = self.metrics.tokens_generated / self.metrics.get_total_time()

        output = f"""=== BitRAG Inference Test Results ===

[Metadata]
timestamp: {timestamp}
timestamp_unix: {timestamp_unix}
query: {self.args.query}
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

[Ollama Configuration]
llm_model: {self.args.model}
temperature: {self.ollama_params.temperature}
top_p: {self.ollama_params.top_p}
top_k: {self.ollama_params.top_k}
ctx_size: {self.ollama_params.ctx_size}
num_ctx: {self.ollama_params.num_ctx}
repeat_penalty: {self.ollama_params.repeat_penalty}
seed: {self.ollama_params.seed}
num_gpu_layers: {self.ollama_params.num_gpu_layers}
threads: {self.ollama_params.threads}
batch_size: {self.ollama_params.batch_size}
mmap: {self.ollama_params.mmap}
numa: {self.ollama_params.numa}
format: {self.ollama_params.format}
inference_method: ollama

[Indexing Information]
embedding_model: {self.args.embedding_model}
chunk_size: {self.args.chunk_size}
chunk_overlap: {self.args.chunk_overlap}
total_documents_indexed: {self.results.get("document_count", 0)}
total_chunks_stored: {self.results.get("total_chunks", 0)}
vector_store: ChromaDB

[Performance Metrics]
total_inference_time_seconds: {self.metrics.get_total_time():.4f}
retrieval_time_seconds: {self.metrics.retrieval_time:.4f}
llm_generation_time_seconds: {self.metrics.llm_generation_time:.4f}
time_to_first_token_seconds: {self.metrics.time_to_first_token:.4f}
time_per_token_seconds: {self.metrics.time_per_token:.4f}
tokens_generated: {self.metrics.tokens_generated}
tokens_per_second: {self.metrics.tokens_per_second:.2f}
memory_used_mb: {self.metrics.memory_used_mb:.2f}
peak_memory_mb: {self.metrics.peak_memory_mb:.2f}
cpu_usage_percent: {self.metrics.cpu_usage_percent:.2f}
gpu_memory_delta_mb: {self.metrics.gpu_memory_delta_mb:.2f}

[Query Information]
query_length_chars: {len(self.args.query)}
query_length_words: {len(self.args.query.split())}
query_timestamp: {timestamp}

[Response Information]
response: {self.results.get("response", "")}
response_length_chars: {len(self.results.get("response", ""))}
response_length_words: {len(self.results.get("response", "").split())}
response_timestamp: {datetime.now().isoformat()}

[Source Context]
retrieved_chunks: {len(self.sources)}
sources: {sources_str}

[Token Usage]
prompt_tokens: {self.token_usage.get("prompt_tokens", 0)}
completion_tokens: {self.token_usage.get("completion_tokens", 0)}
total_tokens: {self.token_usage.get("total_tokens", 0)}
prompt_token_time_seconds: {self.token_usage.get("prompt_token_time", 0):.4f}
completion_token_time_seconds: {self.token_usage.get("completion_token_time", 0):.4f}

[Reasoning Information]
support_reasoning: {self.reasoning_info.get("support_reasoning", 0)}
reasoning_content: {self.reasoning_info.get("reasoning_content", "N/A")}

[Model Information]
model_size_bytes: {self.model_info.get("size_bytes", 0)}
model_size_mb: {self.model_info.get("size_mb", 0):.2f}
model_quantization: {self.model_info.get("quantization", "N/A")}
model_architecture: {self.model_info.get("architecture", "N/A")}

[Results]
success: {self.results.get("success", False)}
error: {self.results.get("error", "None")}
error_type: {self.results.get("error_type", "None")}

[Chart Data]
total_time: {self.metrics.get_total_time():.4f}
retrieval_time: {self.metrics.retrieval_time:.4f}
generation_time: {self.metrics.llm_generation_time:.4f}
memory_delta: {self.metrics.memory_used_mb:.2f}
throughput_tokens_per_sec: {throughput:.2f}
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
        """Run the inference test."""
        print(f"Model: {self.args.model}")
        print(f"Query: {self.args.query}")

        # Run inference
        print("Running inference...")
        self.results = self.run_inference()

        if not self.results.get("success"):
            print(f"Error: {self.results.get('error')}")
            sys.exit(1)

        # Extract reasoning info
        self.reasoning_info = {
            "support_reasoning": self.results.get("support_reasoning", 0),
            "reasoning_content": self.results.get("reasoning_content", ""),
        }

        # Calculate tokens per second
        if self.metrics.llm_generation_time > 0 and self.metrics.tokens_generated > 0:
            self.metrics.tokens_per_second = (
                self.metrics.tokens_generated / self.metrics.llm_generation_time
            )

        # Generate and save output
        output_content = self.generate_output()
        self.save_output(output_content)

        # Print summary
        print("\n=== Summary ===")
        print(f"Total inference time: {self.metrics.get_total_time():.4f}s")
        print(f"Retrieval time: {self.metrics.retrieval_time:.4f}s")
        print(f"Response: {self.results.get('response', '')[:100]}...")
        print(f"Sources: {len(self.sources)} chunks retrieved")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BitRAG Inference Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Required arguments
    parser.add_argument(
        "--model", "-m", required=True, help="LLM model for inference (e.g., llama3.2:1b)"
    )
    parser.add_argument("--query", "-q", required=True, help="User query string")

    # Output
    parser.add_argument(
        "--output",
        "-o",
        default="inference_results.txt",
        help="Output filename (default: inference_results.txt)",
    )
    parser.add_argument(
        "--results-dir",
        "-r",
        default="results",
        help="Directory to save results (default: results)",
    )

    # Query options
    parser.add_argument(
        "--system-prompt", default="You are a helpful assistant.", help="Custom system prompt"
    )
    parser.add_argument(
        "--top-k", type=int, default=3, help="Number of similar chunks to retrieve (default: 3)"
    )

    # Ollama parameters
    parser.add_argument(
        "--temperature", "-t", type=float, default=0.1, help="Sampling temperature (default: 0.1)"
    )
    parser.add_argument(
        "--top-p", type=float, default=0.9, help="Nucleus sampling threshold (default: 0.9)"
    )
    parser.add_argument(
        "--ollama-top-k", type=int, default=40, help="Ollama top-k sampling (default: 40)"
    )
    parser.add_argument(
        "--ctx",
        "-c",
        type=int,
        dest="ctx",
        default=2048,
        help="Context window size (default: 2048)",
    )
    parser.add_argument("--num-ctx", type=int, default=2048, help="Alias for ctx (default: 2048)")
    parser.add_argument(
        "--repeat-penalty", type=float, default=1.1, help="Repetition penalty (default: 1.1)"
    )
    parser.add_argument(
        "--seed", type=int, default=-1, help="Random seed for reproducibility (default: -1)"
    )
    parser.add_argument(
        "--num-gpu-layers",
        type=int,
        default=-1,
        help="Number of GPU layers to use (default: -1 for all)",
    )
    parser.add_argument(
        "--threads", type=int, default=-1, help="Number of CPU threads (default: -1 for auto)"
    )
    parser.add_argument(
        "--batch", type=int, default=512, help="Batch size for prompt processing (default: 512)"
    )
    parser.add_argument(
        "--mmap", action="store_true", default=True, help="Use memory mapping (default: True)"
    )
    parser.add_argument(
        "--no-mmap", action="store_false", dest="mmap", help="Disable memory mapping"
    )
    parser.add_argument(
        "--numa", action="store_true", default=True, help="NUMA binding (default: True)"
    )
    parser.add_argument("--no-numa", action="store_false", dest="numa", help="Disable NUMA binding")
    parser.add_argument(
        "--format",
        choices=["json", "beauty", "json"],
        default="json",
        help="Output format (default: json)",
    )

    # Indexing options (for context)
    parser.add_argument(
        "--embedding-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model used for indexing",
    )
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size used for indexing")
    parser.add_argument(
        "--chunk-overlap", type=int, default=50, help="Chunk overlap used for indexing"
    )

    args = parser.parse_args()

    # Run test
    tester = InferenceTest(args)
    tester.run()


if __name__ == "__main__":
    main()
