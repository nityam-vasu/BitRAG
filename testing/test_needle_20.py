#!/usr/bin/env python3
"""
BitRAG Needle In A Haystack Test

Tests retrieval accuracy with 20 small txt files, each containing
a unique piece of information. The system must find the correct
file based on natural language queries.

Test Design:
- 20 small documents, each with 1 unique fact
- Natural language queries to find specific information
- Tests if ChromaDB can retrieve the correct chunk
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_NEEDLE_DOCS_DIR = os.path.join(_PROJECT_ROOT, "testing", "needle_docs")

if "" in sys.path:
    sys.path.remove("")
if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)

sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

# Force CPU-only mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""


# Test cases - 20 unique facts with queries
NEEDLE_TESTS = [
    {
        "file": "01_server_password.txt",
        "query": "What is the server room password?",
        "expected_keywords": ["QUANTUM-2026-X7", "server room"],
    },
    {
        "file": "02_ceo_mobile.txt",
        "query": "What is the CEO's personal mobile number?",
        "expected_keywords": ["+1-555-0127-8944", "CEO"],
    },
    {
        "file": "03_deadline.txt",
        "query": "When is the project deadline?",
        "expected_keywords": ["November 15th", "2026", "5:00 PM EST"],
    },
    {
        "file": "04_hidden_password.txt",
        "query": "What is the hidden password for backup system?",
        "expected_keywords": ["龙卷风2026", "tornado2026"],
    },
    {
        "file": "05_usb_label.txt",
        "query": "What is the label on the USB drive with encryption key?",
        "expected_keywords": ["KEY-SILVER-773", "USB"],
    },
    {
        "file": "06_budget.txt",
        "query": "What is the annual AI research budget?",
        "expected_keywords": ["$2,847,500", "AI research"],
    },
    {
        "file": "07_building_code.txt",
        "query": "What is the security code for the main building?",
        "expected_keywords": ["4921", "north entrance"],
    },
    {
        "file": "08_wifi_password.txt",
        "query": "What is the guest WiFi password?",
        "expected_keywords": ["WelcomeGuest2026", "Corp-Guest"],
    },
    {
        "file": "09_meeting_code.txt",
        "query": "What is the booking code for client meeting room?",
        "expected_keywords": ["MTG-ROOM-ALPHA-77"],
    },
    {
        "file": "10_api_endpoint.txt",
        "query": "What is the production API endpoint URL?",
        "expected_keywords": ["api.company.com", "v2", "prod"],
    },
    {
        "file": "11_db_password.txt",
        "query": "What is the main database password?",
        "expected_keywords": ["PostgresSecure#2026"],
    },
    {
        "file": "12_license_code.txt",
        "query": "What is the software activation code?",
        "expected_keywords": ["ACTIV-8F3D-2026-X"],
    },
    {
        "file": "13_emergency_contact.txt",
        "query": "What is the emergency contact number for after-hours?",
        "expected_keywords": ["+1-555-0199", "SUPPORT", "24/7"],
    },
    {
        "file": "14_vault_combo.txt",
        "query": "What is the vault combination?",
        "expected_keywords": ["34-7-19-42", "CFO"],
    },
    {
        "file": "15_satellite_phone.txt",
        "query": "What is the satellite phone number?",
        "expected_keywords": ["+1-555-8823", "MARS"],
    },
    {
        "file": "16_launch_date.txt",
        "query": "When is the product launch date?",
        "expected_keywords": ["June 1st", "2026"],
    },
    {
        "file": "17_bonus_q1.txt",
        "query": "What is the Q1 2026 quarterly bonus percentage?",
        "expected_keywords": ["15%", "April 15th"],
    },
    {
        "file": "18_ssh_key.txt",
        "query": "What is the admin SSH key fingerprint?",
        "expected_keywords": ["SHA256:A1B2C3D4E5F6G7H8I9J0"],
    },
    {
        "file": "19_vpn_code.txt",
        "query": "What is the VPN access code?",
        "expected_keywords": ["VPN-SPLIT-TUNNEL-442"],
    },
    {
        "file": "20_report_id.txt",
        "query": "What is the confidential report ID?",
        "expected_keywords": ["RPT-2026-ALPHA-OMEGA-X", "Top Secret"],
    },
]

# Distractor document (generic content to add noise)
DISTRACTOR_CONTENT = """
General Company Information

Our company was founded in 2010 and has grown to over 500 employees.
We operate in the technology sector with a focus on software development.
The main office is located in San Francisco, California.

Office Hours: Monday through Friday, 9:00 AM to 6:00 PM
Holidays: New Year's Day, Memorial Day, Independence Day,
Labor Day, Thanksgiving, Christmas Day

Benefits include health insurance, dental coverage, vision plan,
401(k) matching, paid time off, and professional development.

For general inquiries, email info@company.com or call +1-555-0100.
"""


def load_needle_docs() -> List[Tuple[str, str]]:
    """Load all needle documents from the directory."""
    docs = []

    names = [
        "server_password",
        "ceo_mobile",
        "deadline",
        "hidden_password",
        "usb_label",
        "budget",
        "building_code",
        "wifi_password",
        "meeting_code",
        "api_endpoint",
        "db_password",
        "license_code",
        "emergency_contact",
        "vault_combo",
        "satellite_phone",
        "launch_date",
        "bonus_q1",
        "ssh_key",
        "vpn_code",
        "report_id",
    ]

    for i in range(1, 21):
        name = names[i - 1]
        filepath = os.path.join(_NEEDLE_DOCS_DIR, f"{i:02d}_{name}.txt")

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                docs.append((filepath, content))

    return docs


def run_needle_test(indexer, query_engine, test_case: Dict, top_k: int) -> Dict[str, Any]:
    """Run a single needle test with enhanced metrics."""
    temp_dir = tempfile.mkdtemp()

    try:
        # Create distractor files
        for i in range(5):
            distractor_path = os.path.join(temp_dir, f"distractor_{i}.txt")
            with open(distractor_path, "w", encoding="utf-8") as f:
                f.write(DISTRACTOR_CONTENT)

        # Index all distractor documents
        for i in range(5):
            indexer.index_document(os.path.join(temp_dir, f"distractor_{i}.txt"))

        # Also index the needle document
        needle_path = os.path.join(_NEEDLE_DOCS_DIR, test_case["file"])
        if os.path.exists(needle_path):
            indexer.index_document(needle_path)
        else:
            return {
                "success": False,
                "error": f"Needle file not found: {needle_path}",
            }

        # Now query for the needle
        question = test_case["query"]

        start_time = time.time()
        result = query_engine.query(question)
        query_time = time.time() - start_time

        response_text = result.get("response", "")

        # Extract thinking content if available (for models that support it)
        thinking_content = result.get("thinking", "")

        # Check retrieved sources
        retrieved_texts = []
        source_files = []
        source_scores = []
        for source in result.get("sources", []):
            retrieved_texts.append(source.get("text", ""))
            # Try both locations for file_name
            file_name = source.get("file_name") or source.get("metadata", {}).get("file_name", "")
            source_files.append(file_name)
            # Get similarity score if available
            score = source.get("score", source.get("similarity_score", 0.0))
            source_scores.append(score)

        expected_keywords = test_case.get("expected_keywords", [])

        # ========== ENHANCED METRICS ==========

        # 1. File Retrieval (basic)
        needle_file_retrieved = any(test_case["file"] in f for f in source_files)

        # 2. Precision: How many retrieved chunks are relevant?
        relevant_chunks = 0
        for text in retrieved_texts:
            if any(kw.lower() in text.lower() for kw in expected_keywords):
                relevant_chunks += 1
        retrieval_precision = relevant_chunks / len(retrieved_texts) if retrieved_texts else 0.0

        # 3. Recall: How many relevant keywords were found in retrieved chunks?
        found_keywords = []
        for kw in expected_keywords:
            for text in retrieved_texts:
                if kw.lower() in text.lower():
                    found_keywords.append(kw)
                    break
        keyword_match = len(found_keywords) / len(expected_keywords) if expected_keywords else 0.0

        # 4. Source Citation Verification: Does answer cite info from sources?
        source_citation_verified = False
        if retrieved_texts:
            # Check if answer contains keywords that also appear in sources
            answer_keywords_in_sources = [
                kw
                for kw in expected_keywords
                if any(kw.lower() in rt.lower() for rt in retrieved_texts)
            ]
            source_citation_verified = (
                len(answer_keywords_in_sources) >= len(expected_keywords) * 0.5
            )

        # 5. Hallucination Detection: Does answer match retrieved context?
        # Hallucination = answer mentions info not in any retrieved source
        hallucinated = False
        if response_text:
            has_keywords_in_answer = any(
                kw.lower() in response_text.lower() for kw in expected_keywords
            )
            has_keywords_in_sources = any(
                kw.lower() in text.lower() for kw in expected_keywords for text in retrieved_texts
            )
            if has_keywords_in_answer and not has_keywords_in_sources:
                hallucinated = True

        # 6. Answer Accuracy: Model extracted correct info
        answer_contains_info = any(kw.lower() in response_text.lower() for kw in expected_keywords)

        # 7. Avg retrieval confidence score
        avg_confidence = sum(source_scores) / len(source_scores) if source_scores else 0.0

        return {
            "success": True,
            "file": test_case["file"],
            "query": question,
            "expected_keywords": expected_keywords,
            "found_keywords": found_keywords,
            "keyword_match_rate": keyword_match,
            "retrieval_precision": retrieval_precision,
            "source_citation_verified": source_citation_verified,
            "hallucination_detected": hallucinated,
            "needle_file_retrieved": needle_file_retrieved,
            "answer_contains_info": answer_contains_info,
            "response": response_text[:500],
            "thinking": thinking_content if thinking_content else None,
            "query_time": query_time,
            "retrieved_files": source_files,
            "avg_confidence": avg_confidence,
            "relevant_chunks": relevant_chunks,
            "total_retrieved": len(retrieved_texts),
        }

    except Exception as e:
        return {
            "success": False,
            "file": test_case["file"],
            "error": str(e),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_needle_tests(
    chunk_size: int = 1500,
    chunk_overlap: int = 100,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "llama3.2:1b",
    thinking: bool = True,
) -> Dict[str, Any]:
    """Run all needle tests."""
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
            thinking=thinking,
        )

        indexer = DocumentIndexer(session_id="test_needle")
        query_engine = QueryEngine(
            session_id="test_needle",
            model=llm_model,
            _skip_ollama_check=False,
        )

        results = []
        files_retrieved = 0
        keywords_matched = 0
        answers_correct = 0
        # Enhanced metrics accumulators
        precision_total = 0.0
        citations_verified = 0
        hallucinations = 0
        confidence_scores = []

        print(f"\nRunning Needle-in-Haystack Tests (20 files)")
        print(f"=" * 60)
        print(f"Configuration:")
        print(f"  Chunk Size: {chunk_size}")
        print(f"  Chunk Overlap: {chunk_overlap}")
        print(f"  Embedding Model: {embedding_model}")
        print(f"  Top-K: {top_k}")
        print(f"  LLM: {llm_model}")
        print(f"  Needle Docs: {_NEEDLE_DOCS_DIR}")
        print("=" * 60)

        for i, test_case in enumerate(NEEDLE_TESTS, 1):
            print(f"\nTest {i}/{len(NEEDLE_TESTS)}: {test_case['file']}")
            result = run_needle_test(indexer, query_engine, test_case, top_k)

            if result.get("success"):
                file_ok = result.get("needle_file_retrieved", False)
                kw_ok = result.get("keyword_match_rate", 0) >= 0.5
                ans_ok = result.get("answer_contains_info", False)
                # Enhanced metrics
                prec_ok = result.get("retrieval_precision", 0) >= 0.5
                cite_ok = result.get("source_citation_verified", False)
                hall_ok = not result.get("hallucination_detected", False)

                if file_ok:
                    files_retrieved += 1
                if kw_ok:
                    keywords_matched += 1
                if ans_ok:
                    answers_correct += 1
                if prec_ok:
                    precision_total += 1
                if cite_ok:
                    citations_verified += 1
                if hall_ok:
                    hallucinations += 1
                confidence_scores.append(result.get("avg_confidence", 0.0))

                status = "✓" if (file_ok and ans_ok) else "✗"
                print(f"  {status} File retrieved: {file_ok}")
                print(f"  Keyword match: {result.get('keyword_match_rate', 0):.1%}")
                print(f"  Retrieval precision: {result.get('retrieval_precision', 0):.1%}")
                print(f"  Source citation: {cite_ok}")
                print(f"  Halucination free: {hall_ok}")
                print(f"  Answer correct: {ans_ok}")
                print(f"  Avg confidence: {result.get('avg_confidence', 0):.3f}")
                print(f"  Time: {result.get('query_time', 0):.2f}s")

            results.append(result)

        return {
            "total_tests": len(NEEDLE_TESTS),
            "files_retrieved": files_retrieved,
            "keywords_matched": keywords_matched,
            "answers_correct": answers_correct,
            "retrieval_accuracy": f"{100 * files_retrieved / len(NEEDLE_TESTS):.1f}%",
            "keyword_accuracy": f"{100 * keywords_matched / len(NEEDLE_TESTS):.1f}%",
            "answer_accuracy": f"{100 * answers_correct / len(NEEDLE_TESTS):.1f}%",
            # Enhanced metrics
            "retrieval_precision": f"{100 * precision_total / len(NEEDLE_TESTS):.1f}%"
            if precision_total
            else "N/A",
            "source_citations_verified": f"{100 * citations_verified / len(NEEDLE_TESTS):.1f}%",
            "hallucination_rate": f"{100 * hallucinations / len(NEEDLE_TESTS):.1f}%",
            "avg_confidence": sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0,
            "config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "llm_model": llm_model,
                "thinking": thinking,
            },
            "results": results,
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def save_results(results: Dict[str, Any], output_file: str):
    """Save test results to file."""
    import json
    from datetime import datetime

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"=== BitRAG Needle-in-Haystack Test Results ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

        f.write(f"--- ENHANCED METRICS Summary ---\n")
        f.write(f"Total Tests: {results['total_tests']}\n")
        f.write(
            f"Files Retrieved: {results['files_retrieved']} ({results['retrieval_accuracy']})\n"
        )
        f.write(
            f"Keywords Matched: {results['keywords_matched']} ({results['keyword_accuracy']})\n"
        )
        f.write(f"Answers Correct: {results['answers_correct']} ({results['answer_accuracy']})\n")
        # Enhanced metrics output
        f.write(f"Retrieval Precision: {results.get('retrieval_precision', 'N/A')}\n")
        f.write(f"Source Citations Verified: {results.get('source_citations_verified', 'N/A')}\n")
        f.write(f"Hallucination Rate: {results.get('hallucination_rate', 'N/A')}\n")
        f.write(f"Avg Confidence Score: {results.get('avg_confidence', 'N/A'):.3f}\n")
        f.write("\n")

        f.write(f"--- Configuration ---\n")
        for k, v in results["config"].items():
            f.write(f"  {k}: {v}\n")

        f.write(f"\n--- Detailed Results ---\n")
        f.write("-" * 60 + "\n")

        for i, r in enumerate(results["results"], 1):
            f.write(f"\nTest {i}: {r.get('file', 'N/A')}\n")
            f.write(f"  Query: {r.get('query', 'N/A')}\n")
            f.write(f"  File retrieved: {r.get('needle_file_retrieved', False)}\n")
            f.write(f"  Keyword match: {r.get('keyword_match_rate', 0):.1%}\n")
            f.write(f"  Answer correct: {r.get('answer_contains_info', False)}\n")
            f.write(f"  Time: {r.get('query_time', 0):.2f}s\n")
            if r.get("error"):
                f.write(f"  Error: {r.get('error')}\n")

        f.write(f"\n\n--- JSON ---\n")
        f.write(json.dumps(results, indent=2))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG Needle-in-Haystack Test (20 files)")
    parser.add_argument("--chunk-size", type=int, default=1500)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--llm-model", default="llama3.2:1b")
    parser.add_argument("--output", default="needle_20_results.txt")
    parser.add_argument(
        "--results-dir", "-r", default="results",
        help="Directory to save results (default: results)"
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable thinking mode for models that support it",
    )

    args = parser.parse_args()

    print("Starting Needle-in-Haystack Tests (20 files)...")

    # Handle thinking mode
    thinking_enabled = not args.no_thinking

    results = run_all_needle_tests(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.model,
        top_k=args.top_k,
        llm_model=args.llm_model,
        thinking=thinking_enabled,
    )

    # Store thinking mode in results
    results["config"]["thinking"] = thinking_enabled

    # Create results directory if it doesn't exist
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = results_dir / args.output
    save_results(results, str(output_path))

    print(f"\n{'=' * 60}")
    print("ENHANCED METRICS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Thinking Mode: {'Enabled' if thinking_enabled else 'Disabled'}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Files Retrieved: {results['files_retrieved']} ({results['retrieval_accuracy']})")
    print(f"Keywords Matched: {results['keywords_matched']} ({results['keyword_accuracy']})")
    print(f"Answers Correct: {results['answers_correct']} ({results['answer_accuracy']})")
    # Enhanced metrics display
    print(f"Retrieval Precision: {results.get('retrieval_precision', 'N/A')}")
    print(f"Source Citations Verified: {results.get('source_citations_verified', 'N/A')}")
    print(f"Hallucination Rate: {results.get('hallucination_rate', 'N/A')}")
    print(f"Avg Confidence Score: {results.get('avg_confidence', 0.0):.3f}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
