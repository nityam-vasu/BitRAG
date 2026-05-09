#!/usr/bin/env python3
"""
Run needle-in-haystack tests with all available Ollama models and save results.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_NEEDLE_DOCS_DIR = os.path.join(_PROJECT_ROOT, "testing", "needle_docs")

if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)
sys.path.insert(0, _PROJECT_ROOT)


def get_ollama_models():
    """Get list of available Ollama models."""
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    models = []
    for line in result.stdout.strip().split("\n")[1:]:  # Skip header
        if line.strip():
            parts = line.split()
            if parts:
                models.append(parts[0])
    return models


def filter_models(models: list, include: str = None, exclude: str = None) -> list:
    """Filter models based on include/exclude patterns."""
    filtered = models

    if include:
        include_patterns = include.split(",")
        filtered = [m for m in filtered if any(p in m.lower() for p in include_patterns)]

    if exclude:
        exclude_patterns = exclude.split(",")
        filtered = [m for m in filtered if not any(p in m.lower() for p in exclude_patterns)]

    return filtered


def run_needle_test_with_model(model_name: str, args) -> dict:
    """Run needle test with a specific model."""
    cmd = [
        sys.executable,
        os.path.join(_SCRIPT_DIR, "test_needle_20.py"),
    ]

    # Add arguments
    if args.chunk_size:
        cmd.extend(["--chunk-size", str(args.chunk_size)])
    if args.chunk_overlap:
        cmd.extend(["--chunk-overlap", str(args.chunk_overlap)])
    if args.embedding_model:
        cmd.extend(["--model", args.embedding_model])
    if args.top_k:
        cmd.extend(["--top-k", str(args.top_k)])
    if model_name:
        cmd.extend(["--llm-model", model_name])

    # Thinking parameter - --no-thinking by default, --thinking to enable
    thinking_enabled = getattr(args, "thinking", False)
    no_thinking = getattr(args, "no_thinking", False)

    # If --thinking is passed, enable it. Otherwise --no-thinking (default)
    if thinking_enabled:
        pass  # Don't add flag - model default
    elif no_thinking:
        cmd.extend(["--no-thinking"])
    else:
        # Default: disable thinking for faster testing
        cmd.extend(["--no-thinking"])

    print(f"  Running: {' '.join(cmd)}")
    timeout = getattr(args, "timeout", 300)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {
        "model": model_name,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def parse_summary(output: str) -> dict:
    """Parse summary from test output."""
    summary = {}
    lines = output.split("\n")
    in_summary = False

    for line in lines:
        if "SUMMARY" in line:
            in_summary = True
            continue
        if in_summary:
            if "Total Tests:" in line:
                summary["total_tests"] = int(line.split(":")[-1].strip())
            elif "Files Retrieved:" in line:
                summary["files_retrieved"] = line.split(":")[-1].strip().split(" ")[0]
            elif "Keywords Matched:" in line:
                summary["keywords_matched"] = line.split(":")[-1].strip().split(" ")[0]
            elif "Answers Correct:" in line:
                summary["answers_correct"] = line.split(":")[-1].strip().split(" ")[0]
            elif "Results saved to:" in line:
                summary["results_file"] = line.split(":")[-1].strip()

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run needle-in-haystack tests with all available Ollama models"
    )

    # Model filtering
    parser.add_argument(
        "--include",
        "-i",
        type=str,
        help="Include only models matching these patterns (comma-separated)",
    )
    parser.add_argument(
        "--exclude", "-e", type=str, help="Exclude models matching these patterns (comma-separated)"
    )

    # Test configuration
    parser.add_argument(
        "--chunk-size",
        "-c",
        type=int,
        default=1500,
        help="Chunk size for text splitting (default: 1500)",
    )
    parser.add_argument(
        "--chunk-overlap",
        "-o",
        type=int,
        default=100,
        help="Chunk overlap for text splitting (default: 100)",
    )
    parser.add_argument(
        "--embedding-model",
        "-m",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Embedding model to use (default: sentence-transformers/all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--top-k", "-k", type=int, default=3, help="Number of documents to retrieve (default: 3)"
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        default=False,
        help="Enable thinking mode for reasoning models (qwen3, deepseek-r1)",
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        default=False,
        help="Disable thinking mode (default, faster)",
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=300, help="Timeout per model in seconds (default: 300)"
    )

    # Output
    parser.add_argument(
        "--output", "-O", type=str, help="Output JSON file name (default: auto-generated)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Running Needle-in-Haystack Tests with All Models")
    print("=" * 60)

    # Get all available models
    all_models = get_ollama_models()
    print(f"Found {len(all_models)} models: {all_models}")

    # Filter models
    models = filter_models(all_models, args.include, args.exclude)
    print(f"Testing {len(models)} models: {models}")
    print()

    # Results storage
    thinking_setting = getattr(
        args, "thinking", None
    )  # None = default, True = enabled, False = disabled

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
            "embedding_model": args.embedding_model,
            "top_k": args.top_k,
            "thinking": thinking_setting,
            "timeout": args.timeout,
        },
        "models_tested": [],
        "results": [],
    }

    # Run tests with each model
    for model in models:
        print(f"\n{'=' * 60}")
        print(f"Testing with model: {model}")
        print(f"{'=' * 60}")

        # Run the test
        result = run_needle_test_with_model(model, args)

        if result["returncode"] == 0:
            summary = parse_summary(result["stdout"])
            all_results["models_tested"].append(model)
            all_results["results"].append(
                {
                    "model": model,
                    "summary": summary,
                    "output": result["stdout"],
                    "thinking": thinking_setting,
                }
            )
            print(f"  Files Retrieved: {summary.get('files_retrieved', 'N/A')}")
            print(f"  Keywords Matched: {summary.get('keywords_matched', 'N/A')}")
            print(f"  Answers Correct: {summary.get('answers_correct', 'N/A')}")
        else:
            # Check if there's actual output despite possible warnings
            if result["stdout"] and "SUMMARY" in result["stdout"]:
                summary = parse_summary(result["stdout"])
                all_results["models_tested"].append(model)
                all_results["results"].append(
                    {
                        "model": model,
                        "summary": summary,
                        "output": result["stdout"],
                        "thinking": thinking_setting,
                    }
                )
                print(f"  Files Retrieved: {summary.get('files_retrieved', 'N/A')}")
                print(f"  Keywords Matched: {summary.get('keywords_matched', 'N/A')}")
                print(f"  Answers Correct: {summary.get('answers_correct', 'N/A')}")
            else:
                print(f"  ERROR: {result['stderr'][:200]}")
                all_results["results"].append(
                    {"model": model, "error": result["stderr"], "thinking": thinking_setting}
                )

    # Save results
    if args.output:
        output_file = args.output
    else:
        output_file = f"needle_20_all_models_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")
    print(f"\nResults saved to: {output_file}")
    print("\nModel Performance:")
    print("-" * 70)
    print(f"{'Model':<25} {'Files':<12} {'Keywords':<12} {'Answers':<12}")
    print("-" * 70)

    for r in all_results["results"]:
        if "summary" in r:
            model = r["model"]
            summary = r["summary"]
            files = summary.get("files_retrieved", "N/A")
            keywords = summary.get("keywords_matched", "N/A")
            answers = summary.get("answers_correct", "N/A")
            print(f"{model:<25} {files:<12} {keywords:<12} {answers:<12}")
        else:
            print(f"{r['model']:<25} ERROR")

    print("-" * 70)


if __name__ == "__main__":
    main()
