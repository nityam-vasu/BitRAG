#!/usr/bin/env python3
"""
BitRAG Faithfulness & Hallucination Test

Tests if small LLM models properly acknowledge when they cannot find
the answer in the provided context, rather than hallucinating.

This is critical for small models (< 1.5B) which tend to "make up"
answers when context is insufficient.
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


# Test questions that CANNOT be answered by any document
UNANSWERABLE_QUESTIONS = [
    "What is the capital of France?",
    "Who won the 2024 World Cup?",
    "What is the meaning of life?",
    "How do I bake a cake?",
    "What year was the company founded?",
    "Who is the President of the United States?",
    "What is quantum computing?",
    "Tell me about nuclear fusion.",
    "What are the symptoms of COVID-19?",
    "How do I fix my car engine?",
]

# Document topics (completely unrelated to unanswerable questions)
CONTEXT_DOCUMENTS = [
    (
        "meeting_notes.txt",
        """Project Alpha Weekly Update

Team: Alice (Lead), Bob (Backend), Carol (Frontend), Dave (DevOps)

Progress:
- Completed user authentication module
- Fixed 15 bugs in the payment system
- Deployed staging environment
- Started work on dashboard redesign

Blockers:
- Waiting on API documentation from vendor
- Need more QA resources for testing

Next Week:
- Bob: Complete REST API endpoints
- Carol: Implement responsive design
- Dave: Setup CI/CD pipeline

Budget: $45,000 spent of $100,000 allocated
""",
    ),
    (
        "specs.txt",
        """Software Architecture Specification

Components:
1. Web Application (React + TypeScript)
2. REST API (Node.js + Express)
3. Database (PostgreSQL)
4. Cache (Redis)
5. Message Queue (RabbitMQ)

API Endpoints:
- GET /api/users - List all users
- POST /api/users - Create user
- GET /api/users/:id - Get user by ID
- PUT /api/users/:id - Update user
- DELETE /api/users/:id - Delete user

Authentication: JWT tokens with 24-hour expiry
Authorization: Role-based access control (Admin, User, Guest)

Performance Requirements:
- API response time < 200ms
- Database queries < 50ms
- Frontend load time < 3 seconds
""",
    ),
    (
        "policy.txt",
        """Remote Work Policy

Effective Date: January 1, 2024

Eligible Employees:
- All full-time employees after 90-day probation
- Remote work approved by manager
- Must maintain productivity metrics

Requirements:
- Available during core hours (10 AM - 4 PM)
- Respond to messages within 2 hours
- Attend all scheduled meetings
- Maintain secure home office setup

Equipment:
- Company provides laptop and monitor
- $500 stipend for home office furniture
- Internet reimbursement up to $50/month

Performance:
- Bi-weekly check-ins with manager
- Quarterly performance reviews
- Must meet all project deadlines
""",
    ),
]


def create_test_documents(temp_dir: str) -> List[str]:
    """Create test documents."""
    doc_paths = []

    for filename, content in CONTEXT_DOCUMENTS:
        path = os.path.join(temp_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        doc_paths.append(path)

    return doc_paths


def check_hallucination(response: str, question: str) -> Dict[str, Any]:
    """Check if the response contains hallucinations or appropriate uncertainty."""
    response_lower = response.lower()
    question_lower = question.lower()

    # Phrases that indicate appropriate uncertainty
    uncertainty_phrases = [
        "i don't know",
        "i cannot find",
        "the document",
        "the text does not mention",
        "not mentioned",
        "not provided",
        "not contained",
        "i cannot answer",
        "based on the",
        "from the provided",
        "the provided",
        "the context does not",
        "i couldn't find",
        "i wasn't given",
        "no information about",
        "not specified",
        "i'm not sure",
        "there is no",
        "does not contain",
    ]

    # Phrases that suggest hallucination (making things up)
    hallucination_phrases = [
        "according to",
        "historical records show",
        "it is well known",
        "research has shown",
        "experts believe",
        "typically",
        "usually",
        "often",
        "in general",
        "it is commonly",
    ]

    # Check for uncertainty indicators
    shows_uncertainty = any(phrase in response_lower for phrase in uncertainty_phrases)

    # Check for hallucination indicators
    shows_hallucination = any(phrase in response_lower for phrase in hallucination_phrases)

    # Additional check: does response contain specific factual claims not in context?
    # This is harder to detect without a fact-checking model

    return {
        "shows_uncertainty": shows_uncertainty,
        "shows_hallucination": shows_hallucination,
        "likely_appropriate": shows_uncertainty and not shows_hallucination,
    }


def run_hallucination_test(
    indexer, query_engine, question: str, system_prompt: str
) -> Dict[str, Any]:
    """Run a single hallucination test."""
    temp_dir = tempfile.mkdtemp()

    try:
        # Create documents
        doc_paths = create_test_documents(temp_dir)

        # Index all documents
        for doc_path in doc_paths:
            indexer.index_document(doc_path)

        # Query (using custom system prompt if provided)
        # Note: The QueryEngine should use the system prompt
        print(f"  Question: {question}")

        start_time = time.time()
        result = query_engine.query(question)
        query_time = time.time() - start_time

        response_text = result.get("response", "")

        # Check for hallucination indicators
        hallucination_check = check_hallucination(response_text, question)

        return {
            "success": True,
            "question": question,
            "response": response_text[:500],
            "query_time": query_time,
            "shows_uncertainty": hallucination_check["shows_uncertainty"],
            "shows_hallucination": hallucination_check["shows_hallucination"],
            "likely_appropriate": hallucination_check["likely_appropriate"],
        }

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "error": str(e),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_hallucination_tests(
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "llama3.2:1b",
    system_prompt: str = None,
) -> Dict[str, Any]:
    """Run all hallucination tests."""
    from bitrag.core.config import Config
    from bitrag.core.indexer import DocumentIndexer
    from bitrag.core.query import QueryEngine

    temp_dir = tempfile.mkdtemp()

    # Default prompt if not provided
    if system_prompt is None:
        system_prompt = """You are a helpful assistant. 
Only use the provided context to answer questions. 
If the answer cannot be found in the context, say so clearly.
Do NOT make up information or hallucinate."""

    try:
        config = Config(
            data_dir=os.path.join(temp_dir, "data"),
            chroma_dir=os.path.join(temp_dir, "chroma_db"),
            sessions_dir=os.path.join(temp_dir, "sessions"),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model,
        )

        indexer = DocumentIndexer(session_id="test_hallucination")

        # Note: QueryEngine may not support custom system prompts
        # This is a limitation that would need to be addressed in the core
        query_engine = QueryEngine(
            session_id="test_hallucination",
            model=llm_model,
            _skip_ollama_check=False,
        )

        results = []
        appropriate_responses = 0
        uncertain_count = 0
        hallucination_count = 0

        print(f"\nRunning Faithfulness & Hallucination Tests")
        print(f"=" * 60)
        print(f"Configuration:")
        print(f"  Chunk Size: {chunk_size}")
        print(f"  Chunk Overlap: {chunk_overlap}")
        print(f"  Embedding Model: {embedding_model}")
        print(f"  Top-K: {top_k}")
        print(f"  LLM: {llm_model}")
        print(f"  System Prompt: {system_prompt[:50]}...")
        print(f"=" * 60)

        for i, question in enumerate(UNANSWERABLE_QUESTIONS, 1):
            print(f"\nTest {i}/{len(UNANSWERABLE_QUESTIONS)}:")
            result = run_hallucination_test(indexer, query_engine, question, system_prompt)

            if result.get("success"):
                likely_ok = result.get("likely_appropriate", False)
                uncertain = result.get("shows_uncertainty", False)
                hallucinated = result.get("show_hallucination", False)

                if likely_ok:
                    appropriate_responses += 1
                    status = "✓ GOOD"
                elif uncertain:
                    uncertain_count += 1
                    status = "~ UNCERTAIN"
                else:
                    hallucination_count += 1
                    status = "✗ HALLUCINATION"

                print(f"  {status}")
                print(f"  Shows uncertainty: {uncertain}")
                print(f"  Likely hallucination: {hallucinated}")
                print(f"  Query time: {result.get('query_time', 0):.3f}s")

            results.append(result)

        return {
            "total_tests": len(UNANSWERABLE_QUESTIONS),
            "appropriate_responses": appropriate_responses,
            "uncertain_responses": uncertain_count,
            "hallucination_responses": hallucination_count,
            "pass_rate": f"{100 * appropriate_responses / len(UNANSWERABLE_QUESTIONS):.1f}%"
            if appropriate_responses > 0
            else "0%",
            "config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "llm_model": llm_model,
                "system_prompt": system_prompt,
            },
            "results": results,
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def save_results(results: Dict[str, Any], output_file: str):
    """Save test results to file."""
    import json
    from datetime import datetime

    output_path = Path(output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== BitRAG Faithfulness & Hallucination Test Results ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Tests: {results['total_tests']}\n")
        f.write(f"Appropriate Responses: {results['appropriate_responses']}\n")
        f.write(f"Uncertain Responses: {results['uncertain_responses']}\n")
        f.write(f"Hallucination Responses: {results['hallucination_responses']}\n")
        f.write(f"Pass Rate: {results['pass_rate']}\n\n")

        f.write(f"Configuration:\n")
        for key, value in results["config"].items():
            f.write(f"  {key}: {value}\n")

        f.write(f"\nDetailed Results:\n")
        f.write("-" * 60 + "\n")

        for i, result in enumerate(results["results"], 1):
            f.write(f"\nTest {i}:\n")
            f.write(f"  Question: {result.get('question', 'N/A')}\n")
            f.write(f"  Shows uncertainty: {result.get('shows_uncertainty', False)}\n")
            f.write(f"  Likely hallucination: {result.get('shows_hallucination', False)}\n")
            f.write(f"  Query time: {result.get('query_time', 0):.3f}s\n")
            f.write(f"  Response: {result.get('response', '')[:200]}...\n")
            if result.get("error"):
                f.write(f"  Error: {result.get('error')}\n")

        f.write(f"\n\n--- JSON Data ---\n")
        f.write(json.dumps(results, indent=2))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG Faithfulness & Hallucination Test")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    parser.add_argument(
        "--model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model"
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument("--llm-model", default="llama3.2:1b", help="LLM model")
    parser.add_argument("--system-prompt", default=None, help="System prompt for LLM")
    parser.add_argument("--output", default="hallucination_test_results.txt", help="Output file")
    parser.add_argument(
        "--results-dir", "-r", default="results",
        help="Directory to save results (default: results)"
    )

    args = parser.parse_args()

    print("Starting Faithfulness & Hallucination Tests...")

    results = run_all_hallucination_tests(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.model,
        top_k=args.top_k,
        llm_model=args.llm_model,
        system_prompt=args.system_prompt,
    )

    # Create results directory if it doesn't exist
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = results_dir / args.output
    save_results(results, str(output_path))

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Appropriate: {results['appropriate_responses']}")
    print(f"Uncertain: {results['uncertain_responses']}")
    print(f"Hallucination: {results['hallucination_responses']}")
    print(f"Pass Rate: {results['pass_rate']}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
