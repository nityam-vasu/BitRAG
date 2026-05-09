#!/usr/bin/env python3
"""
BitRAG Needle In A Haystack Test

Tests retrieval accuracy by hiding a specific fact in a document and checking
if ChromaDB + LlamaIndex can find it.

The Goal: Verify that the embedding model and chunk size can successfully
retrieve the exact chunk containing the unique fact.
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


# Test configuration - unique facts to hide in documents
NEEDLE_FACTS = [
    {
        "fact": "The secret password for the breakroom is 'Blue-Giraffe-42'",
        "question": "What is the secret password for the breakroom?",
        "expected_answer": "Blue-Giraffe-42",
    },
    {
        "fact": "The project deadline is September 15th, 2026",
        "question": "When is the project deadline?",
        "expected_answer": "September 15th, 2026",
    },
    {
        "fact": "The CEO's personal email is john.doe@company.com",
        "question": "What is the CEO's personal email address?",
        "expected_answer": "john.doe@company.com",
    },
    {
        "fact": "The security code to enter the server room is 7789",
        "question": "What is the security code for the server room?",
        "expected_answer": "7789",
    },
    {
        "fact": "The隐藏密码是龙卷风2026",  # Chinese: "The hidden password is tornado2026"
        "question": "What is the hidden password?",
        "expected_answer": "龙卷风2026",
    },
]

# Random distractor documents
DISTRACTOR_DOCS = [
    (
        "meeting_notes.txt",
        """Weekly team meeting notes from March 2024.

Attendees: Alice, Bob, Charlie, David

Topics discussed:
- Q1 financial results exceeded expectations
- New marketing campaign launch scheduled for May
- HR updated the remote work policy
- Office renovation will start in June
- Team building event planned for July

Action items:
- Bob to finalize budget by Friday
- Alice to review vendor contracts
- Charlie to update project timeline
- David to schedule security audit
""",
    ),
    (
        "project_specs.txt",
        """Project Specification Document

Project Name: Cloud Migration Initiative
Duration: 6 months
Budget: $500,000

Requirements:
1. Migrate 100+ servers to cloud infrastructure
2. Implement disaster recovery solution
3. Setup monitoring and alerting system
4. Train staff on new systems

Technology Stack:
- AWS as primary cloud provider
- Kubernetes for container orchestration
- Terraform for infrastructure as code
- Prometheus for monitoring

Milestones:
- Phase 1: Assessment and planning (Month 1-2)
- Phase 2: Infrastructure setup (Month 3-4)
- Phase 3: Migration (Month 4-5)
- Phase 4: Testing and optimization (Month 6)
""",
    ),
    (
        "faq.txt",
        """Frequently Asked Questions

Q: What are the office hours?
A: The office is open from 9 AM to 6 PM, Monday through Friday.

Q: How do I request time off?
A: Submit your request through the HR portal at least 2 weeks in advance.

Q: Where is the printer located?
A: The printer is on the 2nd floor, next to the break room.

Q: How do I reset my password?
A: Visit the IT helpdesk or use the self-service password reset portal.

Q: What is the dress code?
A: Business casual Monday through Thursday, casual on Fridays.
""",
    ),
    (
        "technical_notes.txt",
        """Technical Architecture Notes

System Components:
1. Frontend - React SPA hosted on S3
2. API Gateway - Kong running on EC2
3. Application Servers - Auto-scaling group behind ALB
4. Database - PostgreSQL RDS with read replicas
5. Cache - Redis ElastiCache cluster
6. Message Queue - RabbitMQ for async processing

Security Measures:
- All traffic encrypted with TLS 1.3
- JWT tokens for authentication
- Rate limiting on public endpoints
- WAF protection via CloudFront
- Regular security patches applied

Monitoring:
- CloudWatch for metrics and logs
- Datadog for APM
- PagerDuty for alerting
- SLO tracking with Error Budget
""",
    ),
    (
        "policy.txt",
        """Employee Handbook - Key Policies

Code of Conduct:
- Treat all colleagues with respect
- Maintain professional behavior at all times
- Report any violations to HR

Work Hours:
- Standard: 40 hours per week
- Flexible hours available with manager approval
- Remote work: Up to 2 days per week

Benefits:
- Health insurance (medical, dental, vision)
- 401(k) with 4% matching
- 15 days paid time off
- 10 paid holidays
- Professional development budget: $2000/year

Performance Reviews:
- Conducted quarterly
- Self-assessment + manager review
- Goal setting for next quarter
""",
    ),
    (
        "recipe.txt",
        """Chocolate Chip Cookie Recipe

Ingredients:
- 2 1/4 cups all-purpose flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter (softened)
- 3/4 cup sugar
- 3/4 cup brown sugar
- 2 large eggs
- 1 tsp vanilla extract
- 2 cups chocolate chips

Instructions:
1. Preheat oven to 375°F
2. Mix flour, baking soda, and salt in a bowl
3. Beat butter and sugars until creamy
4. Add eggs and vanilla to butter mixture
5. Gradually blend in flour mixture
6. Stir in chocolate chips
7. Drop rounded tablespoons onto baking sheet
8. Bake 9-11 minutes until golden brown
9. Cool on baking sheet for 2 minutes
""",
    ),
    (
        "travel_guide.txt",
        """Paris Travel Guide

Best Time to Visit:
- April to June (spring)
- September to November (fall)

Must-See Attractions:
- Eiffel Tower
- Louvre Museum
- Notre-Dame Cathedral
- Champs-Élysées
- Montmartre and Sacré-Cœur
- Seine River cruise

Transportation:
- Metro: Most efficient way to get around
- Bus: Good for scenic routes
- Taxi: Available but expensive
- Bike: Vélib' bike sharing program

Dining:
- Breakfast: Croissants and café
- Lunch: Boulangerie sandwiches
- Dinner: Traditional French cuisine
- Budget: €15-30 per meal

Costs:
- Accommodation: €100-200/night
- Meals: €30-60/day
- Attractions: €10-20 each
""",
    ),
    (
        "meeting_schedule.txt",
        """Team Meeting Schedule - Q2 2024

Weekly Sync (All Teams):
- Mondays at 10:00 AM - Zoom

Engineering Team:
- Tuesdays at 2:00 PM - Conference Room A
- Thursdays at 11:00 PM - Zoom

Product Team:
- Wednesdays at 3:00 PM - Conference Room B
- Fridays at 1:00 PM - Zoom

Design Team:
- Mondays at 4:00 PM - Creative Studio
- Thursdays at 10:00 AM - Zoom

One-on-Ones:
- Manager to direct reports: Weekly, 30 min
- Skip-level: Bi-weekly, 45 min

All-hands:
- Last Friday of each month at 11:00 AM
""",
    ),
]


def create_test_documents(temp_dir: str, needle_index: int) -> List[str]:
    """Create test documents with needle embedded in one."""
    doc_paths = []
    needle_info = NEEDLE_FACTS[needle_index]

    # Create distractor documents
    for i, (filename, content) in enumerate(DISTRACTOR_DOCS):
        path = os.path.join(temp_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        doc_paths.append(path)

    # Create needle document (insert fact naturally)
    needle_doc_path = os.path.join(temp_dir, "secret_doc.txt")
    needle_content = f"""Confidential Document - Internal Use Only

This document contains important information for authorized personnel only.

The following is a summary of recent security updates and access protocols:

{needle_info["fact"]}

For additional information, please contact the security team.

Previous security updates covered topics like badge access, visitor management,
and emergency procedures. All employees must complete the annual security
training module by the end of the month.

Remember: Security is everyone's responsibility. Report any suspicious
activities to security@company.com immediately.
"""
    with open(needle_doc_path, "w", encoding="utf-8") as f:
        f.write(needle_content)
    doc_paths.append(needle_doc_path)

    return doc_paths, needle_info


def run_needle_test(indexer, query_engine, needle_index: int, top_k: int = 3) -> Dict[str, Any]:
    """Run a single needle test."""
    temp_dir = tempfile.mkdtemp()
    needle_info = NEEDLE_FACTS[needle_index]

    try:
        # Create documents with needle
        doc_paths, _ = create_test_documents(temp_dir, needle_index)

        # Index all documents
        print(f"\n  Indexing {len(doc_paths)} documents...")
        for doc_path in doc_paths:
            indexer.index_document(doc_path)

        # Query for the needle
        question = needle_info["question"]
        print(f"  Question: {question}")

        start_time = time.time()
        result = query_engine.query(question)
        query_time = time.time() - start_time

        response_text = result.get("response", "")

        # Check if retrieved sources contain the needle
        retrieved_texts = []
        for source in result.get("sources", []):
            retrieved_texts.append(source.get("text", ""))

        needle_found_in_sources = any(
            needle_info["expected_answer"] in text for text in retrieved_texts
        )

        # Check if answer contains the fact
        answer_contains_fact = needle_info["expected_answer"] in response_text

        return {
            "success": True,
            "question": question,
            "expected_fact": needle_info["fact"],
            "expected_answer": needle_info["expected_answer"],
            "response": response_text[:500],
            "query_time": query_time,
            "needle_in_sources": needle_found_in_sources,
            "fact_in_response": answer_contains_fact,
            "retrieved_sources_count": len(retrieved_texts),
            "retrieved_texts": retrieved_texts,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_needle_tests(
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "llama3.2:1b",
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
        )

        indexer = DocumentIndexer(session_id="test_needle")
        query_engine = QueryEngine(
            session_id="test_needle",
            model=llm_model,
            _skip_ollama_check=False,
        )

        results = []
        passed = 0

        print(f"\nRunning Needle-in-Haystack Tests")
        print(f"=" * 60)
        print(f"Configuration:")
        print(f"  Chunk Size: {chunk_size}")
        print(f"  Chunk Overlap: {chunk_overlap}")
        print(f"  Embedding Model: {embedding_model}")
        print(f"  Top-K: {top_k}")
        print(f"  LLM: {llm_model}")
        print(f"=" * 60)

        for i in range(len(NEEDLE_FACTS)):
            print(f"\nTest {i + 1}/{len(NEEDLE_FACTS)}:")
            result = run_needle_test(indexer, query_engine, i, top_k)

            if result.get("success"):
                retrieval_ok = result.get("needle_in_sources", False)
                answer_ok = result.get("fact_in_response", False)

                status = "✓ PASS" if (retrieval_ok and answer_ok) else "✗ FAIL"
                if retrieval_ok and answer_ok:
                    passed += 1

                print(f"  {status}")
                print(f"  Retrieval found needle: {retrieval_ok}")
                print(f"  Answer contains fact: {answer_ok}")
                print(f"  Query time: {result.get('query_time', 0):.3f}s")

            results.append(result)

        return {
            "total_tests": len(NEEDLE_FACTS),
            "passed": passed,
            "failed": len(NEEDLE_FACTS) - passed,
            "pass_rate": f"{100 * passed / len(NEEDLE_FACTS):.1f}%",
            "config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "llm_model": llm_model,
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
        f.write(f"=== BitRAG Needle-in-Haystack Test Results ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Tests: {results['total_tests']}\n")
        f.write(f"Passed: {results['passed']}\n")
        f.write(f"Failed: {results['failed']}\n")
        f.write(f"Pass Rate: {results['pass_rate']}\n\n")

        f.write(f"Configuration:\n")
        for key, value in results["config"].items():
            f.write(f"  {key}: {value}\n")

        f.write(f"\nDetailed Results:\n")
        f.write("-" * 60 + "\n")

        for i, result in enumerate(results["results"], 1):
            f.write(f"\nTest {i}:\n")
            f.write(f"  Question: {result.get('question', 'N/A')}\n")
            f.write(f"  Expected Answer: {result.get('expected_answer', 'N/A')}\n")
            f.write(f"  Retrieval found needle: {result.get('needle_in_sources', False)}\n")
            f.write(f"  Fact in response: {result.get('fact_in_response', False)}\n")
            f.write(f"  Query time: {result.get('query_time', 0):.3f}s\n")
            if result.get("error"):
                f.write(f"  Error: {result.get('error')}\n")

        f.write(f"\n\n--- JSON Data ---\n")
        f.write(json.dumps(results, indent=2))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG Needle-in-Haystack Test")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    parser.add_argument(
        "--model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model"
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument("--llm-model", default="llama3.2:1b", help="LLM model")
    parser.add_argument("--output", default="needle_test_results.txt", help="Output file")

    args = parser.parse_args()

    print("Starting Needle-in-Haystack Tests...")

    results = run_all_needle_tests(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.model,
        top_k=args.top_k,
        llm_model=args.llm_model,
    )

    save_results(results, args.output)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Pass Rate: {results['pass_rate']}")
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
