#!/usr/bin/env python3
"""
BitRAG Comprehensive Test Suite

Runs all four specialized tests for low-resource, CPU-only RAG setups:
1. Needle-in-Haystack (Retrieval Accuracy)
2. Faithfulness & Hallucination (Hallucination Detection)
3. Latency & Resource Benchmark (Performance)
4. RAGAS-Lite (Quality Assessment)

Usage:
    python test_comprehensive.py --all                    # Run all tests
    python test_comprehensive.py --needle                # Just needle test
    python test_comprehensive.py --hallucination        # Just hallucination test
    python test_comprehensive.py --latency              # Just latency test
    python test_comprehensive.py --ragas                # Just RAGAS test

    # Custom configuration
    python test_comprehensive.py --all --llm-model qwen2.5:1.5b --embedding-model BAAI/bge-small-en-v1.5
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_SRC_PATH = os.path.join(_PROJECT_ROOT, "src")

if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)


def get_python_path():
    """Get Python path from venv."""
    if (Path(_PROJECT_ROOT) / "venv/bin/python").exists():
        return os.path.abspath(str(Path(_PROJECT_ROOT) / "venv/bin/python"))
    if (Path(_PROJECT_ROOT) / ".venv/bin/python").exists():
        return os.path.abspath(str(Path(_PROJECT_ROOT) / ".venv/bin/python"))
    return "python3"


def get_python_env():
    """Get environment with CPU-only mode."""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONPATH"] = _SRC_PATH
    env["CUDA_VISIBLE_DEVICES"] = ""
    return env


_PYTHON_PATH = get_python_path()


def run_test_script(script_name: str, args: list, description: str) -> dict:
    """Run a test script and return results."""
    import subprocess

    cmd = [_PYTHON_PATH, script_name] + args

    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"{'=' * 60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=_PROJECT_ROOT,
            env=get_python_env(),
            timeout=600,  # 10 minute timeout
        )

        if result.returncode == 0:
            print(result.stdout)
            return {"success": True, "output": result.stdout}
        else:
            print(f"Error: {result.stderr}")
            return {"success": False, "error": result.stderr, "output": result.stdout}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Test timed out after 10 minutes"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_all_tests(args):
    """Run all comprehensive tests."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(_PROJECT_ROOT) / "testing" / f"comprehensive_results_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"BitRAG Comprehensive Test Suite")
    print(f"{'=' * 60}")
    print(f"Timestamp: {timestamp}")
    print(f"Results Directory: {results_dir}")
    print(f"\nConfiguration:")
    print(f"  LLM Model: {args.llm_model}")
    print(f"  Embedding Model: {args.embedding_model}")
    print(f"  Chunk Size: {args.chunk_size}")
    print(f"  Chunk Overlap: {args.chunk_overlap}")
    print(f"  Top-K: {args.top_k}")

    # Build common args
    common_args = [
        "--llm-model",
        args.llm_model,
        "--model",
        args.embedding_model,
        "--chunk-size",
        str(args.chunk_size),
        "--chunk-overlap",
        str(args.chunk_overlap),
        "--top-k",
        str(args.top_k),
    ]

    test_results = {}

    # 1. Needle-in-Haystack Test
    if args.all or args.needle:
        output_file = str(results_dir / "needle_results.txt")
        result = run_test_script(
            "testing/test_needle_haystack.py",
            common_args + ["--output", output_file],
            "Needle-in-Haystack (Retrieval Accuracy)",
        )
        test_results["needle"] = result

    # 2. Faithfulness & Hallucination Test
    if args.all or args.hallucination:
        output_file = str(results_dir / "hallucination_results.txt")
        result = run_test_script(
            "testing/test_faithfulness.py",
            common_args + ["--output", output_file],
            "Faithfulness & Hallucination",
        )
        test_results["hallucination"] = result

    # 3. Latency & Resource Benchmark
    if args.all or args.latency:
        output_file = str(results_dir / "latency_results.txt")
        result = run_test_script(
            "testing/test_latency_benchmark.py",
            common_args + ["--output", output_file, "--no-warmup"],
            "Latency & Resource Benchmark",
        )
        test_results["latency"] = result

    # 4. RAGAS-Lite Test
    if args.all or args.ragas:
        output_file = str(results_dir / "ragas_results.txt")
        result = run_test_script(
            "testing/test_ragas_lite.py",
            common_args + ["--output", output_file],
            "RAGAS-Lite Quality Assessment",
        )
        test_results["ragas"] = result

    # Summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")

    passed = 0
    failed = 0

    for test_name, result in test_results.items():
        status = "✓ PASS" if result.get("success") else "✗ FAIL"
        print(f"{test_name.upper()}: {status}")
        if result.get("success"):
            passed += 1
        else:
            failed += 1
            if result.get("error"):
                print(f"  Error: {result.get('error')[:200]}")

    print(f"\nTotal: {passed} passed, {failed} failed")
    print(f"Results saved to: {results_dir}")

    return {
        "timestamp": timestamp,
        "passed": passed,
        "failed": failed,
        "results": test_results,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BitRAG Comprehensive Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Test selection
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--needle", action="store_true", help="Run needle-in-haystack test")
    parser.add_argument("--hallucination", action="store_true", help="Run hallucination test")
    parser.add_argument("--latency", action="store_true", help="Run latency benchmark")
    parser.add_argument("--ragas", action="store_true", help="Run RAGAS-lite test")

    # Common configuration
    parser.add_argument(
        "--llm-model", default="llama3.2:1b", help="LLM model for inference (default: llama3.2:1b)"
    )
    parser.add_argument(
        "--embedding-model",
        "-m",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model (default: sentence-transformers/all-MiniLM-L6-v2)",
    )
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size (default: 512)")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap (default: 50)")
    parser.add_argument(
        "--top-k", type=int, default=3, help="Number of chunks to retrieve (default: 3)"
    )

    args = parser.parse_args()

    # Default to --all if no specific test selected
    if not any([args.all, args.needle, args.hallucination, args.latency, args.ragas]):
        args.all = True

    print("BitRAG Comprehensive Test Suite")
    print("=" * 60)

    run_all_tests(args)


if __name__ == "__main__":
    main()
