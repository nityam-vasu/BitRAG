#!/usr/bin/env python3
"""
BitRAG Batch Inference Test Script

Reads test parameters from input CSV and writes results to output CSV for data analysis.

Usage:
    python test_inference_batch.py --input test_inference_params.csv --output results.csv
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
import csv
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = _SCRIPT_DIR
_SRC_PATH = os.path.join(_PROJECT_ROOT, "src")

if "" in sys.path:
    sys.path.remove("")
if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)

sys.path.insert(0, _SRC_PATH)

# Force CPU-only mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""

try:
    import psutil
except ImportError:
    psutil = None
    print("Warning: psutil not installed - some metrics disabled")


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
            "python_version": platform.version(),
            "python_implementation": platform.python_implementation(),
        }

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
                info["gpu_memory_total_mb"] = (
                    int(gpu_info[1].strip().replace("MiB", "").replace("Mi", ""))
                    if len(gpu_info) > 1
                    else 0
                )
                info["gpu_memory_used_mb"] = (
                    int(gpu_info[2].strip().replace("MiB", "").replace("Mi", ""))
                    if len(gpu_info) > 2
                    else 0
                )
            else:
                info["gpu_info"] = "Not available"
                info["gpu_memory_total_mb"] = 0
                info["gpu_memory_used_mb"] = 0
        except:
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
        self.start_time = time.time()
        self.peak_memory_mb = self.get_memory_usage()
        self._initial_memory = self.get_memory_usage()

    def stop(self):
        self.end_time = time.time()
        self.memory_used_mb = self.get_memory_usage() - self._initial_memory

    def get_total_time(self) -> float:
        return self.end_time - self.start_time

    def get_memory_usage(self) -> float:
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def get_cpu_usage(self) -> float:
        return psutil.cpu_percent(interval=0.1)


# Placeholder for thinking tag closing - we'll use a variable
THINK_END_TAG = ""


class BatchInferenceTest:
    """Batch test class for LLM inference."""

    def __init__(self, input_csv: str, output_csv: str):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.test_cases: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.sys_info = SystemInfo.get_system_info()

    def load_test_cases(self) -> int:
        """Load test cases from input CSV."""
        test_cases = []

        with open(self.input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append(row)

        self.test_cases = test_cases
        print(f"Loaded {len(test_cases)} test cases from {self.input_csv}")
        return len(test_cases)

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single inference test."""
        from bitrag.core.config import Config
        from bitrag.core.query import QueryEngine

        metrics = PerformanceMetrics()
        result = {
            "test_type": test_case.get("test_type", "inference"),
            "output_file": test_case.get("output_file", ""),
            "model": test_case.get("model", ""),
            "query": test_case.get("query", ""),
            "system_prompt": test_case.get("system_prompt", "You are a helpful assistant."),
            "top_k": test_case.get("top_k", "3"),
            "temperature": test_case.get("temperature", "0.1"),
            "top_p": test_case.get("top_p", "0.9"),
            "top_k_ollama": test_case.get("top_k_ollama", "40"),
            "ctx": test_case.get("ctx", "2048"),
            "repeat_penalty": test_case.get("repeat_penalty", "1.1"),
            "seed": test_case.get("seed", "-1"),
            "gpu_layers": test_case.get("gpu_layers", "-1"),
            "threads": test_case.get("threads", "-1"),
            "batch": test_case.get("batch", "512"),
            "mmap": test_case.get("mmap", "true"),
            "numa": test_case.get("numa", "true"),
            "format": test_case.get("format", "json"),
            "embedding_model": test_case.get(
                "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            "chunk_size": test_case.get("chunk_size", "512"),
            "chunk_overlap": test_case.get("chunk_overlap", "50"),
        }

        # Convert string values to proper types
        top_k = int(test_case.get("top_k", 3))
        temperature = float(test_case.get("temperature", 0.1))
        top_p = float(test_case.get("top_p", 0.9))
        ctx = int(test_case.get("ctx", 2048))
        repeat_penalty = float(test_case.get("repeat_penalty", 1.1))
        seed = int(test_case.get("seed", -1))
        chunk_size = int(test_case.get("chunk_size", 512))
        chunk_overlap = int(test_case.get("chunk_overlap", 50))

        model = test_case.get("model", "")
        query = test_case.get("query", "")
        system_prompt = test_case.get("system_prompt", "You are a helpful assistant.")

        temp_dir = tempfile.mkdtemp()

        try:
            # Initialize config
            config = Config(
                data_dir=os.path.join(temp_dir, "data"),
                chroma_dir=os.path.join(temp_dir, "chroma_db"),
                sessions_dir=os.path.join(temp_dir, "sessions"),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            # Start metrics
            metrics.start()

            # Initialize query engine
            engine = QueryEngine(
                session_id="test_session",
                model=model,
                _skip_ollama_check=False,
            )

            # Run query
            retrieval_start = time.time()
            query_result = engine.query(query)
            retrieval_end = time.time()

            metrics.retrieval_time = retrieval_end - retrieval_start

            # Get response
            response = query_result.get("response", "")
            response_length = len(response)
            response_words = len(response.split())

            # Estimate tokens (rough estimate: 1 token = 4 characters)
            completion_tokens = response_length // 4
            prompt_tokens = len(query) // 4
            total_tokens = prompt_tokens + completion_tokens

            # Calculate generation time (approximate)
            metrics.llm_generation_time = metrics.get_total_time() - metrics.retrieval_time

            if metrics.llm_generation_time > 0 and completion_tokens > 0:
                metrics.tokens_per_second = completion_tokens / metrics.llm_generation_time
            metrics.tokens_generated = completion_tokens

            metrics.stop()
            metrics.cpu_usage_percent = metrics.get_cpu_usage()

            # Detect reasoning - check for thinking tags
            support_reasoning = 0
            reasoning_content = ""
            think_start = ""
            think_end = ""
            if "<think>" in response and "" in response:
                support_reasoning = 1
                think_start = "<think>"
                think_end = ""
                start = response.index(think_start) + len(think_start)
                end = response.index(think_end)
                reasoning_content = response[start:end].strip()[:500]

            # Success result
            result.update(
                {
                    "success": True,
                    "error": "",
                    "total_time_seconds": round(metrics.get_total_time(), 4),
                    "retrieval_time_seconds": round(metrics.retrieval_time, 4),
                    "generation_time_seconds": round(metrics.llm_generation_time, 4),
                    "tokens_generated": completion_tokens,
                    "tokens_per_second": round(metrics.tokens_per_second, 2),
                    "memory_used_mb": round(metrics.memory_used_mb, 2),
                    "peak_memory_mb": round(metrics.peak_memory_mb, 2),
                    "cpu_usage_percent": round(metrics.cpu_usage_percent, 2),
                    "response_length_chars": response_length,
                    "response_length_words": response_words,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "support_reasoning": support_reasoning,
                    "reasoning_content": reasoning_content[:200] if reasoning_content else "",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            metrics.stop()
            result.update(
                {
                    "success": False,
                    "error": str(e)[:500],
                    "total_time_seconds": round(metrics.get_total_time(), 4),
                    "retrieval_time_seconds": round(metrics.retrieval_time, 4),
                    "generation_time_seconds": round(
                        metrics.get_total_time() - metrics.retrieval_time, 4
                    ),
                    "tokens_generated": 0,
                    "tokens_per_second": 0.0,
                    "memory_used_mb": round(metrics.memory_used_mb, 2),
                    "peak_memory_mb": round(metrics.peak_memory_mb, 2),
                    "cpu_usage_percent": round(metrics.get_cpu_usage(), 2),
                    "response_length_chars": 0,
                    "response_length_words": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "support_reasoning": 0,
                    "reasoning_content": "",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return result

    def save_results(self):
        """Save results to output CSV."""
        if not self.results:
            print("No results to save")
            return

        # Define output fields
        fieldnames = [
            "test_type",
            "output_file",
            "model",
            "query",
            "system_prompt",
            "top_k",
            "temperature",
            "top_p",
            "top_k_ollama",
            "ctx",
            "repeat_penalty",
            "seed",
            "gpu_layers",
            "threads",
            "batch",
            "mmap",
            "numa",
            "format",
            "embedding_model",
            "chunk_size",
            "chunk_overlap",
            "success",
            "error",
            "total_time_seconds",
            "retrieval_time_seconds",
            "generation_time_seconds",
            "tokens_generated",
            "tokens_per_second",
            "memory_used_mb",
            "peak_memory_mb",
            "cpu_usage_percent",
            "response_length_chars",
            "response_length_words",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "support_reasoning",
            "reasoning_content",
            "timestamp",
        ]

        with open(self.output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"Results saved to: {self.output_csv}")

    def run(self):
        """Run all test cases."""
        # Load test cases
        total = self.load_test_cases()

        if total == 0:
            print("No test cases found!")
            return

        print(f"\nRunning {total} test cases...")
        print("-" * 50)

        successful = 0
        failed = 0

        for i, test_case in enumerate(self.test_cases, 1):
            model = test_case.get("model", "unknown")
            query = test_case.get("query", "")[:50]

            print(f"[{i}/{total}] Testing {model}: {query}...")

            try:
                result = self.run_single_test(test_case)
                self.results.append(result)

                if result.get("success"):
                    successful += 1
                    print(
                        f"  OK - Time: {result.get('total_time_seconds', 0)}s, Tokens: {result.get('tokens_generated', 0)}"
                    )
                else:
                    failed += 1
                    error = result.get("error", "Unknown error")[:100]
                    print(f"  FAIL - {error}")

            except Exception as e:
                failed += 1
                print(f"  EXCEPTION - {str(e)[:100]}")

                # Add failed result
                failed_result = {
                    "test_type": test_case.get("test_type", "inference"),
                    "output_file": test_case.get("output_file", ""),
                    "model": test_case.get("model", ""),
                    "query": test_case.get("query", ""),
                    "success": False,
                    "error": str(e)[:500],
                    "timestamp": datetime.now().isoformat(),
                }
                # Add default values for other fields
                for key in [
                    "system_prompt",
                    "top_k",
                    "temperature",
                    "top_p",
                    "top_k_ollama",
                    "ctx",
                    "repeat_penalty",
                    "seed",
                    "gpu_layers",
                    "threads",
                    "batch",
                    "mmap",
                    "numa",
                    "format",
                    "embedding_model",
                    "chunk_size",
                    "chunk_overlap",
                    "total_time_seconds",
                    "retrieval_time_seconds",
                    "generation_time_seconds",
                    "tokens_generated",
                    "tokens_per_second",
                    "memory_used_mb",
                    "peak_memory_mb",
                    "cpu_usage_percent",
                    "response_length_chars",
                    "response_length_words",
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                    "support_reasoning",
                    "reasoning_content",
                ]:
                    failed_result[key] = test_case.get(key, "")

                self.results.append(failed_result)

            # Save intermediate results every 10 tests
            if i % 10 == 0:
                self.save_results()
                print(f"  [Auto-saved at {i} tests]")

        print("-" * 50)
        print(f"Completed: {successful} successful, {failed} failed")

        # Save final results
        self.save_results()

        # Print summary statistics
        if self.results:
            success_results = [r for r in self.results if r.get("success")]
            if success_results:
                avg_time = sum(r.get("total_time_seconds", 0) for r in success_results) / len(
                    success_results
                )
                avg_tokens = sum(r.get("tokens_generated", 0) for r in success_results) / len(
                    success_results
                )
                avg_tps = sum(r.get("tokens_per_second", 0) for r in success_results) / len(
                    success_results
                )

                print("\n=== Summary Statistics ===")
                print(f"Average total time: {avg_time:.2f}s")
                print(f"Average tokens generated: {avg_tokens:.0f}")
                print(f"Average tokens/second: {avg_tps:.2f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BitRAG Batch Inference Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--input", "-i", required=True, help="Input CSV file with test parameters")
    parser.add_argument("--output", "-o", required=True, help="Output CSV file for results")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Run batch tests
    tester = BatchInferenceTest(args.input, args.output)
    tester.run()


if __name__ == "__main__":
    main()
