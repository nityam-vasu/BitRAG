#!/usr/bin/env python3
"""
BitRAG Metrics Script

Measures and records performance metrics for the BitRAG RAG system including:
- Indexing time
- Query response time
- Token usage
- Memory and GPU stats
- Model information
"""

import argparse
import csv
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bitrag.core.indexer import DocumentIndexer
    from bitrag.core.hybrid_search import HybridSearch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from bitrag.core.indexer import DocumentIndexer
from bitrag.core.query import QueryEngine
from bitrag.core.hybrid_search import HybridSearch
from bitrag.core.config import get_config


REASONING_MODELS = [
    "deepSeek-R1:1.5b",
    "qwen3:1.7b",
    "qwen3:0.6b",
]


def is_reasoning_model(model_name: str) -> bool:
    """Check if the model is a reasoning model"""
    model_lower = model_name.lower()
    for rm in REASONING_MODELS:
        if rm.lower() in model_lower or model_lower in rm.lower():
            return True
    return False


def get_gpu_stats() -> Dict[str, Any]:
    """Get GPU statistics using nvidia-smi"""
    gpu_stats = {
        "gpu_available": False,
        "gpu_name": "N/A",
        "gpu_memory_used_mb": 0,
        "gpu_memory_total_mb": 0,
        "gpu_memory_percent": 0,
        "gpu_utilization_percent": 0,
    }

    try:
        import subprocess

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            gpu_info = lines[0].split(",")

            gpu_stats["gpu_available"] = True
            gpu_stats["gpu_name"] = gpu_info[0].strip()
            gpu_stats["gpu_memory_used_mb"] = float(gpu_info[1].strip())
            gpu_stats["gpu_memory_total_mb"] = float(gpu_info[2].strip())
            gpu_stats["gpu_memory_percent"] = (
                round((gpu_stats["gpu_memory_used_mb"] / gpu_stats["gpu_memory_total_mb"]) * 100, 2)
                if gpu_stats["gpu_memory_total_mb"] > 0
                else 0
            )
            gpu_stats["gpu_utilization_percent"] = float(gpu_info[3].strip())

    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError, ValueError):
        pass

    return gpu_stats


def get_memory_stats() -> Dict[str, Any]:
    """Get system memory statistics"""
    memory_stats = {
        "ram_used_gb": 0,
        "ram_total_gb": 0,
        "ram_percent": 0,
    }

    try:
        import subprocess

        result = subprocess.run(["free", "-b"], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                mem_line = lines[1].split()
                total = int(mem_line[1])
                used = int(mem_line[2])

                memory_stats["ram_total_gb"] = round(total / (1024**3), 2)
                memory_stats["ram_used_gb"] = round(used / (1024**3), 2)
                memory_stats["ram_percent"] = round((used / total) * 100, 2)

    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError, ValueError):
        pass

    return memory_stats


def get_token_count(text: str) -> int:
    """Estimate token count (rough approximation: ~4 chars per token)"""
    return len(text) // 4


def index_document_vector(pdf_path: str, session_id: str) -> tuple[str, float]:
    """
    Index document using vector search only.

    Returns:
        Tuple of (document_id, indexing_time_seconds)
    """
    start_time = time.time()

    indexer = DocumentIndexer(session_id)
    doc_id = indexer.index_document(pdf_path, metadata={"source": "metrics", "method": "vector"})

    indexing_time = time.time() - start_time

    return doc_id, indexing_time


def index_document_hybrid(pdf_path: str, session_id: str, alpha: float = 0.5) -> tuple[str, float]:
    """
    Index document using hybrid search (vector + BM25).

    Returns:
        Tuple of (document_id, indexing_time_seconds)
    """
    start_time = time.time()

    indexer = DocumentIndexer(session_id)
    doc_id = indexer.index_document(pdf_path, metadata={"source": "metrics", "method": "hybrid"})

    indexer2 = DocumentIndexer(session_id)
    hybrid_search = HybridSearch(
        session_id=session_id, chroma_dir=str(indexer2.chroma_dir), alpha=alpha
    )
    hybrid_search.rebuild_index()

    indexing_time = time.time() - start_time

    return doc_id, indexing_time


def run_query_vector(
    question: str, session_id: str, model: str, engine: Optional["QueryEngine"] = None
) -> Dict[str, Any]:
    """Run a query using vector search and return metrics"""

    # Reuse existing engine if provided, otherwise create new one
    if engine is None:
        engine = QueryEngine(session_id=session_id, model=model)

    start_time = time.time()
    result = engine.query(question)
    inference_time_ms = (time.time() - start_time) * 1000

    context_parts = []
    for src in result.get("sources", []):
        context_parts.append(src.get("text", ""))
    context_text = "\n\n---\n\n".join(context_parts)

    input_tokens = get_token_count(f"Context: {context_text}\n\nQuestion: {question}")
    output_tokens = get_token_count(result.get("response", ""))
    total_tokens = input_tokens + output_tokens

    return {
        "query_passed": question,
        "answer_returned": result.get("response", ""),
        "model_name": model,
        "is_reasoning_model": is_reasoning_model(model),
        "context_file": result["sources"][0]["metadata"].get("file_name", "N/A")
        if result.get("sources")
        else "N/A",
        "method_used": "vector",
        "inference_time_ms": round(inference_time_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def run_query_hybrid(
    question: str,
    session_id: str,
    model: str,
    alpha: float = 0.5,
    indexer: Optional["DocumentIndexer"] = None,
    hybrid_search: Optional["HybridSearch"] = None,
) -> Dict[str, Any]:
    """Run a query using hybrid search and return metrics"""

    # Reuse existing indexer and hybrid_search if provided, otherwise create new ones
    if indexer is None:
        indexer = DocumentIndexer(session_id)

    if hybrid_search is None:
        hybrid_search = HybridSearch(
            session_id=session_id, chroma_dir=str(indexer.chroma_dir), alpha=alpha
        )

    config = get_config()

    start_time = time.time()

    results = hybrid_search.hybrid_search(question, k=config.top_k)

    if not results:
        return {
            "query_passed": question,
            "answer_returned": "No results found",
            "model_name": model,
            "is_reasoning_model": is_reasoning_model(model),
            "context_file": "N/A",
            "method_used": f"hybrid_alpha_{alpha}",
            "inference_time_ms": round((time.time() - start_time) * 1000, 2),
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    context_parts = [r["text"] for r in results]
    context_text = "\n\n---\n\n".join(context_parts)

    from bitrag.core.query import DEFAULT_RAG_PROMPT

    prompt = DEFAULT_RAG_PROMPT.format(context=context_text, question=question)

    engine = QueryEngine(session_id=session_id, model=model)
    llm_response = engine.llm.complete(prompt)

    inference_time_ms = (time.time() - start_time) * 1000

    input_tokens = get_token_count(prompt)
    output_tokens = get_token_count(llm_response.text)
    total_tokens = input_tokens + output_tokens

    return {
        "query_passed": question,
        "answer_returned": llm_response.text,
        "model_name": model,
        "is_reasoning_model": is_reasoning_model(model),
        "context_file": results[0].get("metadata", {}).get("file_name", "N/A")
        if results
        else "N/A",
        "method_used": f"hybrid_alpha_{alpha}",
        "inference_time_ms": round(inference_time_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def load_queries(query_file: str) -> List[str]:
    """Load queries from a text file (one query per line)"""
    queries = []
    with open(query_file, "r") as f:
        for line in f:
            query = line.strip()
            if query and not query.startswith("#"):
                queries.append(query)
    return queries


def run_benchmark(
    pdf_path: str,
    queries: List[str],
    model: str,
    method: str,
    alpha: float = 0.5,
    session_id: str = "metrics_session",
) -> List[Dict[str, Any]]:
    """Run the full benchmark and return results"""

    results = []

    print(f"\n{'=' * 60}")
    print(f"BitRAG Metrics Benchmark")
    print(f"{'=' * 60}")
    print(f"PDF: {pdf_path}")
    print(f"Model: {model}")
    print(f"Method: {method}")
    if method == "both":
        print(f"Alpha: {alpha}")
    print(f"Queries: {len(queries)}")
    print(f"{'=' * 60}\n")

    print("Step 1: Indexing document...")

    if method in ["vector", "both"]:
        doc_id, indexing_time_vector = index_document_vector(pdf_path, session_id)
        print(f"  Vector indexing time: {indexing_time_vector:.2f} seconds")

    if method in ["hybrid", "both"]:
        doc_id, indexing_time_hybrid = index_document_hybrid(pdf_path, session_id)
        print(f"  Hybrid indexing time: {indexing_time_hybrid:.2f} seconds")

    indexing_time = indexing_time_vector if method == "vector" else indexing_time_hybrid

    # Create QueryEngine ONCE before the query loop to avoid reloading the model each time
    # Also create DocumentIndexer and HybridSearch once for hybrid mode to avoid OOM
    print("\nStep 2: Running queries...\n")

    engine = None
    indexer = None
    hybrid_search = None

    if method == "vector":
        print("  Initializing QueryEngine (vector mode)...")
        engine = QueryEngine(session_id=session_id, model=model)
        print("  QueryEngine initialized - model loaded once")
    elif method in ["hybrid", "both"]:
        print("  Initializing DocumentIndexer and HybridSearch (hybrid mode)...")
        indexer = DocumentIndexer(session_id)
        hybrid_search = HybridSearch(
            session_id=session_id, chroma_dir=str(indexer.chroma_dir), alpha=alpha
        )
        print("  HybridSearch initialized - embedding model loaded once")

    for i, query in enumerate(queries, 1):
        print(f"  Query {i}/{len(queries)}: {query[:50]}...")

        if method == "vector":
            query_result = run_query_vector(query, session_id, model, engine=engine)
        elif method == "hybrid":
            query_result = run_query_hybrid(
                query, session_id, model, alpha, indexer=indexer, hybrid_search=hybrid_search
            )
        else:  # method == "both"
            query_result = run_query_hybrid(
                query, session_id, model, alpha, indexer=indexer, hybrid_search=hybrid_search
            )

        query_result["indexing_time_seconds"] = round(indexing_time, 2)
        query_result["query_number"] = i

        gpu_stats = get_gpu_stats()
        mem_stats = get_memory_stats()

        query_result["gpu_available"] = gpu_stats["gpu_available"]
        query_result["gpu_name"] = gpu_stats["gpu_name"]
        query_result["gpu_memory_used_mb"] = gpu_stats["gpu_memory_used_mb"]
        query_result["gpu_memory_total_mb"] = gpu_stats["gpu_memory_total_mb"]
        query_result["gpu_memory_percent"] = gpu_stats["gpu_memory_percent"]
        query_result["gpu_utilization_percent"] = gpu_stats["gpu_utilization_percent"]

        query_result["ram_used_gb"] = mem_stats["ram_used_gb"]
        query_result["ram_total_gb"] = mem_stats["ram_total_gb"]
        query_result["ram_percent"] = mem_stats["ram_percent"]

        query_result["timestamp"] = datetime.now().isoformat()

        results.append(query_result)

        print(f"    -> Inference time: {query_result['inference_time_ms']:.2f} ms")

    print(f"\n{'=' * 60}")
    print("Benchmark complete!")
    print(f"{'=' * 60}\n")

    return results


def save_results_csv(results: List[Dict[str, Any]], output_file: str):
    """Save results to CSV file"""

    fieldnames = [
        "query_number",
        "indexing_time_seconds",
        "query_passed",
        "answer_returned",
        "model_name",
        "is_reasoning_model",
        "context_file",
        "method_used",
        "inference_time_ms",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "gpu_available",
        "gpu_name",
        "gpu_memory_used_mb",
        "gpu_memory_total_mb",
        "gpu_memory_percent",
        "gpu_utilization_percent",
        "ram_used_gb",
        "ram_total_gb",
        "ram_percent",
        "timestamp",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = {field: result.get(field, "N/A") for field in fieldnames}
            writer.writerow(row)

    print(f"Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="BitRAG Metrics - Benchmark RAG system performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python metrics.py -f document.pdf -v -input_query queries.txt -m llama3.2:1b
  python metrics.py -f document.pdf -h -input_query queries.txt -m llama3.2:1b
  python metrics.py -f document.pdf -b 0.7 -input_query queries.txt -m llama3.2:1b
        """,
    )

    parser.add_argument("-f", "--file", required=True, help="Path to the PDF file to index")

    parser.add_argument(
        "-v", "--vector", action="store_true", help="Use vector search indexing method"
    )

    parser.add_argument("--hybrid", action="store_true", help="Use hybrid search indexing method")

    parser.add_argument(
        "-b",
        "--both",
        type=float,
        default=None,
        metavar="ALPHA",
        help="Test both methods. ALPHA is the weight for vector search (0=keyword, 1=vector)",
    )

    parser.add_argument(
        "-input_query",
        "--input-query",
        required=True,
        help="Path to the file containing queries (one per line)",
    )

    parser.add_argument(
        "-m",
        "--model",
        required=True,
        help="Model name to use for inference (e.g., llama3.2:1b, deepseek-r1:1.5b)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="rag_metrics_results.csv",
        help="Output CSV file path (default: rag_metrics_results.csv)",
    )

    parser.add_argument(
        "-s",
        "--session",
        default="metrics_session",
        help="Session ID for indexing (default: metrics_session)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    if not os.path.exists(args.input_query):
        print(f"Error: Query file not found: {args.input_query}")
        sys.exit(1)

    method = "vector"
    alpha = 0.5

    if args.hybrid:
        method = "hybrid"
    elif args.both is not None:
        method = "both"
        alpha = args.both
    elif args.vector:
        method = "vector"
    else:
        print("Error: Please specify indexing method (-v, -h, or -b)")
        sys.exit(1)

    queries = load_queries(args.input_query)

    if not queries:
        print("Error: No queries found in the input file")
        sys.exit(1)

    results = run_benchmark(
        pdf_path=args.file,
        queries=queries,
        model=args.model,
        method=method,
        alpha=alpha,
        session_id=args.session,
    )

    save_results_csv(results, args.output)

    print("\nSummary:")
    total_inference = sum(r["inference_time_ms"] for r in results)
    avg_inference = total_inference / len(results) if results else 0
    print(f"  Total queries: {len(results)}")
    print(f"  Average inference time: {avg_inference:.2f} ms")
    print(f"  Total indexing time: {results[0]['indexing_time_seconds']:.2f} seconds")


if __name__ == "__main__":
    main()
