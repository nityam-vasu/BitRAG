#!/usr/bin/env python3
"""
BitRAG Latency & Resource Benchmark Test

Measures the performance of the full RAG pipeline on CPU-only systems.
Key metrics:
- Retrieval time (ChromaDB + LlamaIndex)
- Generation time (LLM inference)
- Total query time
- Tokens per second (TPS)
- Memory usage
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
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
    print("Warning: psutil not installed - memory metrics disabled")


# Test queries with varying complexity
BENCHMARK_QUERIES = [
    {
        "query": "What is this about?",
        "category": "simple",
        "description": "Basic overview query",
    },
    {
        "query": "Summarize the main points",
        "category": "summarization",
        "description": "Summary request",
    },
    {
        "query": "What are the key details discussed?",
        "category": "extraction",
        "description": "Information extraction",
    },
    {
        "query": "List all the important items mentioned",
        "category": "list",
        "description": "List extraction",
    },
    {
        "query": "Explain what happened and provide specific details",
        "category": "complex",
        "description": "Complex explanation request",
    },
]


# Sample document for testing
SAMPLE_DOCUMENT = """Project Alpha Documentation

Overview:
Project Alpha is a web-based application for managing customer relationships.
The system was developed by a team of 5 engineers over 6 months.

Key Features:
1. User Authentication - OAuth2 and JWT support
2. Dashboard - Real-time metrics and analytics
3. Contact Management - CRUD operations for customer data
4. Email Integration - Send automated follow-ups
5. Reporting - Generate PDF and CSV reports

Technical Stack:
- Frontend: React 18 with TypeScript
- Backend: Node.js with Express
- Database: PostgreSQL 14
- Cache: Redis 7
- Cloud: AWS (EC2, RDS, S3)

Team Members:
- Alice - Project Lead
- Bob - Backend Developer
- Carol - Frontend Developer
- Dave - DevOps Engineer
- Eve - QA Engineer

Timeline:
- Planning: January 2024
- Development: February - May 2024
- Testing: June 2024
- Launch: July 2024

Budget:
- Total: $150,000
- Spent: $120,000
- Remaining: $30,000

Risks:
- Tight deadline
- Limited testing resources
- Dependency on third-party API

Success Metrics:
- 99.9% uptime
- < 200ms response time
- 1000+ concurrent users
- Zero critical bugs at launch

Contact: team@projectalpha.com
"""


def get_memory_info() -> Dict[str, float]:
    """Get current memory usage."""
    if psutil is None:
        return {"current_mb": 0.0, "percent": 0.0}
    try:
        process = psutil.Process()
        return {
            "current_mb": process.memory_info().rss / (1024 * 1024),
            "percent": process.memory_percent(),
        }
    except Exception:
        return {"current_mb": 0.0, "percent": 0.0}


def run_single_benchmark(indexer, query_engine, query: str, top_k: int) -> Dict[str, Any]:
    """Run a single benchmark query."""
    # Get initial memory
    mem_before = get_memory_info()

    # Time the retrieval phase
    retrieval_start = time.time()
    # Note: In practice, retrieval is part of query()
    # We'll measure total and estimate

    # Run query
    start_time = time.time()
    result = query_engine.query(query)
    total_time = time.time() - start_time

    # Get memory after
    mem_after = get_memory_info()

    response_text = result.get("response", "")

    # Estimate tokens (rough: 1 token ≈ 4 chars for English)
    estimated_prompt_tokens = len(query) // 4
    estimated_response_tokens = len(response_text) // 4
    total_estimated_tokens = estimated_prompt_tokens + estimated_response_tokens

    # Calculate TPS (tokens per second)
    tps = total_estimated_tokens / total_time if total_time > 0 else 0

    # Get source count
    source_count = len(result.get("sources", []))

    return {
        "query": query,
        "response": response_text[:300],
        "total_time": total_time,
        "estimated_tokens": total_estimated_tokens,
        "tokens_per_second": tps,
        "source_count": source_count,
        "memory_delta_mb": mem_after["current_mb"] - mem_before["current_mb"],
        "memory_after_mb": mem_after["current_mb"],
    }


def run_benchmark(
    indexer, query_engine, queries: List[Dict], top_k: int, warmup: bool = True
) -> List[Dict[str, Any]]:
    """Run benchmark queries."""
    results = []

    # Warmup run (first query often slower due to model loading)
    if warmup:
        print("  Running warmup query...")
        query_engine.query(queries[0]["query"])

    print(f"\n  Running {len(queries)} benchmark queries...")

    for i, q in enumerate(queries, 1):
        print(f"  Query {i}/{len(queries)}: {q['description']}")
        result = run_single_benchmark(indexer, query_engine, q["query"], top_k)
        result["category"] = q["category"]
        result["description"] = q["description"]
        results.append(result)

        # Small delay between queries
        time.sleep(0.5)

    return results


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from benchmark results."""
    total_times = [r["total_time"] for r in results]
    tps_values = [r["tokens_per_second"] for r in results]
    memory_deltas = [r["memory_delta_mb"] for r in results]

    import statistics

    return {
        "avg_total_time": statistics.mean(total_times),
        "min_total_time": min(total_times),
        "max_total_time": max(total_times),
        "stdev_total_time": statistics.stdev(total_times) if len(total_times) > 1 else 0,
        "avg_tps": statistics.mean(tps_values),
        "min_tps": min(tps_values),
        "max_tps": max(tps_values),
        "avg_memory_delta": statistics.mean(memory_deltas),
        "peak_memory_mb": max(r["memory_after_mb"] for r in results),
    }


def run_latency_benchmark(
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "llama3.2:1b",
    warmup: bool = True,
    iterations: int = 1,
) -> Dict[str, Any]:
    """Run complete latency benchmark."""
    from bitrag.core.config import Config
    from bitrag.core.indexer import DocumentIndexer
    from bitrag.core.query import QueryEngine

    temp_dir = tempfile.mkdtemp()

    try:
        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model,
        )

        # Create indexer and query engine
        indexer = DocumentIndexer(session_id="test_latency")
        query_engine = QueryEngine(
            session_id="test_latency",
            model=llm_model,
            _skip_ollama_check=False,
        )

        # Create and index test document
        doc_path = os.path.join(temp_dir, "test_doc.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_DOCUMENT)

        print("  Indexing test document...")
        indexer.index_document(doc_path)

        all_results = []

        for iteration in range(iterations):
            print(f"\n--- Iteration {iteration + 1}/{iterations} ---")
            results = run_benchmark(
                indexer,
                query_engine,
                BENCHMARK_QUERIES,
                top_k,
                warmup=(iteration == 0),  # Only warmup first iteration
            )
            all_results.extend(results)

        # Calculate statistics
        stats = calculate_statistics(all_results)

        return {
            "success": True,
            "total_queries": len(all_results),
            "iterations": iterations,
            "config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "llm_model": llm_model,
                "warmup": warmup,
            },
            "statistics": stats,
            "results": all_results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def save_results(results: Dict[str, Any], output_file: str):
    """Save benchmark results to file."""
    import json
    from datetime import datetime

    output_path = Path(output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== BitRAG Latency & Resource Benchmark Results ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Queries: {results.get('total_queries', 0)}\n")

        if results.get("success"):
            stats = results.get("statistics", {})
            f.write(f"\n--- Performance Statistics ---\n")
            f.write(f"Average Total Time: {stats.get('avg_total_time', 0):.3f}s\n")
            f.write(f"Min Total Time: {stats.get('min_total_time', 0):.3f}s\n")
            f.write(f"Max Total Time: {stats.get('max_total_time', 0):.3f}s\n")
            f.write(f"Std Dev: {stats.get('stdev_total_time', 0):.3f}s\n")
            f.write(f"\n--- Token Throughput ---\n")
            f.write(f"Average TPS: {stats.get('avg_tps', 0):.2f}\n")
            f.write(f"Min TPS: {stats.get('min_tps', 0):.2f}\n")
            f.write(f"Max TPS: {stats.get('max_tps', 0):.2f}\n")
            f.write(f"\n--- Memory Usage ---\n")
            f.write(f"Average Delta: {stats.get('avg_memory_delta', 0):.2f} MB\n")
            f.write(f"Peak Memory: {stats.get('peak_memory_mb', 0):.2f} MB\n")

            f.write(f"\n--- Configuration ---\n")
            for key, value in results.get("config", {}).items():
                f.write(f"  {key}: {value}\n")

            f.write(f"\n--- Per-Query Results ---\n")
            f.write("-" * 60 + "\n")
            for i, r in enumerate(results.get("results", []), 1):
                f.write(f"\nQuery {i}: {r.get('description', 'N/A')}\n")
                f.write(f"  Category: {r.get('category', 'N/A')}\n")
                f.write(f"  Query: {r.get('query', 'N/A')}\n")
                f.write(f"  Total Time: {r.get('total_time', 0):.3f}s\n")
                f.write(f"  Est. Tokens: {r.get('estimated_tokens', 0)}\n")
                f.write(f"  TPS: {r.get('tokens_per_second', 0):.2f}\n")
                f.write(f"  Sources: {r.get('source_count', 0)}\n")
                f.write(f"  Memory Delta: {r.get('memory_delta_mb', 0):.2f} MB\n")

        f.write(f"\n\n--- JSON Data ---\n")
        f.write(json.dumps(results, indent=2))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG Latency & Resource Benchmark")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    parser.add_argument(
        "--model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model"
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument("--llm-model", default="llama3.2:1b", help="LLM model")
    parser.add_argument("--no-warmup", action="store_true", help="Skip warmup run")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations")
    parser.add_argument("--output", default="latency_benchmark_results.txt", help="Output file")

    args = parser.parse_args()

    print("Starting Latency & Resource Benchmark...")

    results = run_latency_benchmark(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.model,
        top_k=args.top_k,
        llm_model=args.llm_model,
        warmup=not args.no_warmup,
        iterations=args.iterations,
    )

    save_results(results, args.output)

    if results.get("success"):
        stats = results.get("statistics", {})
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total Queries: {results['total_queries']}")
        print(f"\nPerformance:")
        print(f"  Avg Time: {stats.get('avg_total_time', 0):.3f}s")
        print(
            f"  Min/Max: {stats.get('min_total_time', 0):.3f}s / {stats.get('max_total_time', 0):.3f}s"
        )
        print(f"\nThroughput:")
        print(f"  Avg TPS: {stats.get('avg_tps', 0):.2f}")
        print(f"  Min/Max: {stats.get('min_tps', 0):.2f} / {stats.get('max_tps', 0):.2f}")
        print(f"\nMemory:")
        print(f"  Avg Delta: {stats.get('avg_memory_delta', 0):.2f} MB")
        print(f"  Peak: {stats.get('peak_memory_mb', 0):.2f} MB")
    else:
        print(f"Error: {results.get('error')}")

    print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
