#!/usr/bin/env python3
"""
BitRAG RAGAS-Lite (Manual RAG Assessment)

A simplified version of RAGAS metrics for CPU-only, small model setups.
Instead of using a big "Judge" LLM, this performs manual assessment
by checking retrieved sources against the response.

Metrics:
1. Faithfulness - Are claims in the answer actually in the sources?
2. Answer Relevance - Does the answer address the question?
3. Context Precision - How many of top-k chunks are useful?
"""

import os
import sys
import tempfile
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

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


# Test cases with known good answers
RAGAS_TEST_CASES = [
    {
        "question": "What is the project name?",
        "expected_keywords": ["Project Alpha", "Alpha"],
        "category": "entity_extraction",
    },
    {
        "question": "What programming languages are used?",
        "expected_keywords": ["React", "TypeScript", "Node.js", "JavaScript", "PostgreSQL"],
        "category": "list_extraction",
    },
    {
        "question": "Who are the team members?",
        "expected_keywords": ["Alice", "Bob", "Carol", "Dave", "Eve"],
        "category": "list_extraction",
    },
    {
        "question": "What is the budget information?",
        "expected_keywords": ["$150,000", "120,000", "30,000", "budget"],
        "category": "fact_extraction",
    },
    {
        "question": "When was the project launched?",
        "expected_keywords": ["July 2024", "July", "2024"],
        "category": "date_extraction",
    },
    {
        "question": "What are the success metrics?",
        "expected_keywords": ["99.9%", "200ms", "1000", "users", "uptime", "response time"],
        "category": "list_extraction",
    },
    {
        "question": "What are the identified risks?",
        "expected_keywords": ["deadline", "testing", "API", "risks"],
        "category": "list_extraction",
    },
    {
        "question": "What cloud provider is used?",
        "expected_keywords": ["AWS", "Amazon", "EC2", "RDS", "S3"],
        "category": "entity_extraction",
    },
]

# Sample document for testing
SAMPLE_DOCUMENT = """INTERNAL CONFIDENTIAL - PROJECT ALPHA TECHNICAL DOCUMENTATION

Document Version: 2.4
Last Updated: December 15, 2025
Classification: Internal Use Only

EXECUTIVE SUMMARY
Project Alpha is a comprehensive web-based application designed for managing customer relationships across enterprise environments. The system was developed by a team of 5 senior engineers over a 6-month development cycle, with an additional 2 months allocated for testing and quality assurance. The project represents a strategic initiative to modernize our customer relationship management capabilities and replace the legacy CRM system that had been in operation since 2018.

PROJECT OBJECTIVES
The primary objectives of Project Alpha include: establishing a unified platform for customer data management, enabling real-time analytics and reporting capabilities, improving team collaboration through integrated communication tools, and providing a scalable foundation for future enhancement. The system is designed to handle up to 10,000 concurrent users with sub-200ms response times for critical operations.

KEY FEATURES
1. User Authentication - Comprehensive OAuth2 and JWT support with multi-factor authentication, role-based access control, and session management. Supports SSO integration with corporate identity providers including Okta, Azure AD, and custom SAML implementations.

2. Dashboard - Real-time metrics and analytics engine providing customizable widgets, automated reporting, and business intelligence capabilities. Includes pre-built templates for sales pipelines, customer engagement metrics, and team performance dashboards.

3. Contact Management - Full CRUD operations for customer data with automated data enrichment, duplicate detection, and merge functionality. Supports custom fields, contact tagging, and automated workflow triggers.

4. Email Integration - Send automated follow-ups through SMTP and API-based email services. Includes email template management, tracking, and analytics for open rates and click-through metrics.

5. Reporting - Generate PDF and CSV reports with scheduled delivery. Supports custom report builder with drag-and-drop interface, saved report templates, and export to multiple formats.

6. API Gateway - RESTful API with rate limiting, request validation, and comprehensive documentation. API version 2 includes GraphQL support and webhook integrations.

TECHNICAL STACK
- Frontend: React 18 with TypeScript, Redux for state management, and Material-UI component library
- Backend: Node.js with Express, TypeScript, and TypeORM for database operations
- Database: PostgreSQL 14 with read replicas for performance scaling
- Cache: Redis 7 for session management and real-time caching
- Message Queue: RabbitMQ for asynchronous processing
- Cloud: AWS (EC2, RDS, S3, ElastiCache, CloudFront)
- Container: Docker with Kubernetes orchestration
- CI/CD: GitHub Actions with automated testing and deployment

INFRASTRUCTURE SPECIFICATIONS
Production environment runs on AWS with the following components:
- Application Servers: 3x t3.xlarge EC2 instances in auto-scaling group
- Database: RDS PostgreSQL db.r5.large with Multi-AZ deployment
- Cache: ElastiCache Redis cluster with 2 nodes
- Storage: S3 bucket with lifecycle policies
- CDN: CloudFront distribution for static assets
- Load Balancer: Application Load Balancer with SSL termination
- Monitoring: CloudWatch with custom dashboards and alerts

TEAM MEMBERS AND RESPONSIBILITIES
- Alice - Project Lead: Overall project coordination, stakeholder management, and technical decision-making
- Bob - Backend Developer: API development, database architecture, and integration services
- Carol - Frontend Developer: UI/UX implementation, component library, and responsive design
- Dave - DevOps Engineer: Infrastructure management, CI/CD pipelines, and monitoring
- Eve - QA Engineer: Test automation, quality assurance, and performance testing

Additional team members contributing to specific phases include Frank (Security Architect) for security review, Grace (Database Administrator) for performance optimization, and Henry (Technical Writer) for documentation.

PROJECT TIMELINE
- Phase 1 - Planning: January 2024 (completed)
- Phase 2 - Development: February - May 2024 (completed)
- Phase 3 - Testing: June 2024 (completed)
- Phase 4 - User Acceptance Testing: Early July 2024 (completed)
- Phase 5 - Launch: July 2024 (completed)
- Phase 6 - Post-Launch Support: On-going

Key milestones achieved:
- MVP delivery: March 15, 2024
- Alpha testing completion: April 30, 2024
- Beta testing completion: May 31, 2024
- Production launch: July 1, 2024
- 100-day stability milestone: October 9, 2024

BUDGET ALLOCATION AND EXPENDITURE
Total Approved Budget: $150,000

Expenditure Breakdown:
- Personnel costs: $95,000 (5 engineers x 6 months x average rate)
- Cloud infrastructure setup: $18,000
- Software licenses and tools: $12,000
- Training and documentation: $5,000
- Contingency reserve: $20,000

Actual Spending:
- Total Spent: $120,000
- Remaining Budget: $30,000

Variance Analysis:
- Personnel: Under budget by $5,000 due to efficient team utilization
- Infrastructure: Over budget by $3,000 due to enhanced security requirements
- Licenses: On budget
- Training: Under budget by $2,000 due to virtual training options
- Contingency: $13,000 utilized for emergency security patches

IDENTIFIED RISKS AND MITIGATION
Risk 1: Tight deadline
- Probability: High
- Impact: Medium
- Mitigation: Implemented agile methodology with bi-weekly sprints, daily stand-ups, and prioritized feature list. Core features delivered first with optional enhancements deferred.

Risk 2: Limited testing resources  
- Probability: Medium
- Impact: High
- Mitigation: Implemented automated testing suite covering 85% of codebase. Enlisted external QA consultants for UAT phase. Established bug triage process with severity classification.

Risk 3: Dependency on third-party API
- Probability: Medium
- Impact: High
- Mitigation: Implemented abstraction layer for API calls. Established fallback mechanisms and retry logic. Created comprehensive error handling and logging. API contract versioning implemented.

Risk 4: Data migration complexity
- Probability: Low
- Impact: High
- Mitigation: Developed migration scripts with rollback capability. Performed dry-run migrations in staging. Implemented data validation checks.

Risk 5: User adoption challenges
- Probability: Medium
- Impact: Medium
- Mitigation: Created comprehensive training materials. Implemented in-app guidance and tooltips. Established champion program for peer training.

SUCCESS METRICS AND KPIs
Production Targets Achieved:
- System Uptime: 99.9% (Target: 99.9%) - Exceeded in first month
- Response Time: < 200ms for 95th percentile (Target: < 200ms) - Achieved
- Concurrent Users: Support for 1000+ simultaneous users (Target: 1000+) - Current peak: 847
- Critical Bugs: Zero critical bugs at launch (Target: Zero) - Achieved
- User Satisfaction: 4.2/5.0 average rating (Target: 4.0+) - Exceeded

Additional Metrics:
- Daily Active Users: 2,500+
- API Response Time: Average 45ms
- Email Deliverability: 99.8%
- Report Generation: Average 3.2 seconds
- Data Sync Frequency: Every 15 minutes
- Backup Success Rate: 100%
- Security Incidents: Zero critical incidents

INTEGRATION REQUIREMENTS
External integrations implemented:
- Salesforce CRM: Bi-directional sync with conflict resolution
- Slack: Real-time notifications and command integration
- Zoom: Meeting scheduling and recording integration
- Stripe: Payment processing
- Twilio: SMS notifications and 2FA

SECURITY IMPLEMENTATIONS
- SSL/TLS encryption for all data in transit
- AES-256 encryption for data at rest
- Multi-factor authentication required for all admin access
- Regular security audits conducted monthly
- Penetration testing performed quarterly
- Security incident response plan documented

SUPPORT AND MAINTENANCE
Post-launch support structure:
- Tier 1 Support: helpdesk@projectalpha.com (24/7)
- Tier 2 Support: engineering team (business hours)
- Tier 3 Support: Escalation to development leads
- Maintenance Windows: Sunday 2 AM - 6 AM EST
- Hotfix Process: Emergency deployment capability

CONTACT INFORMATION
Project Lead: Alice Johnson (alice.johnson@projectalpha.com)
Technical Lead: Bob Smith (bob.smith@projectalpha.com)
General Inquiries: team@projectalpha.com
Emergency: +1-555-0199 (24/7 hotline)

Documentation maintained at: https://docs.projectalpha.internal
Issue Tracker: https://jira.projectalpha.internal
"""


def check_faithfulness(response: str, sources: List[str]) -> Tuple[float, List[str]]:
    """
    Faithfulness: Are claims in the response actually in the sources?

    Returns a score (0-1) and list of unverified claims.
    This is a simplified check - looks for key phrases from response
    that should be in sources.
    """
    # Extract potential claims (simplified - split by sentences/clauses)
    # In a real implementation, you'd use NER and fact extraction

    # Simple heuristic: Check if key information from response exists in sources
    # Combine all source text
    combined_sources = " ".join(sources).lower()
    response_lower = response.lower()

    # Check for numbers and specific terms
    number_pattern = r"\$[\d,]+|\d+\.\d+%?|\d+[\d,]*"
    response_numbers = set(re.findall(number_pattern, response_lower))
    source_numbers = set(re.findall(number_pattern, combined_sources))

    # Check for names/entities
    name_pattern = r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*"
    response_names = set(re.findall(name_pattern, response_lower))
    source_names = set(re.findall(name_pattern, combined_sources))

    # Calculate overlap
    if not response_numbers and not response_names:
        return 1.0, []  # Nothing specific to check

    number_match = (
        len(response_numbers & source_numbers) / len(response_numbers) if response_numbers else 1.0
    )
    name_match = len(response_names & source_names) / len(response_names) if response_names else 1.0

    faithfulness = (number_match + name_match) / 2

    # Find missing items
    missing_numbers = response_numbers - source_numbers
    missing_names = response_names - source_names

    unverified = list(missing_numbers) + list(missing_names)[:5]  # Limit to 5

    return faithfulness, unverified


def check_answer_relevance(question: str, response: str) -> float:
    """
    Answer Relevance: Does the response actually address the question?

    Simple heuristic: Check if question keywords appear in response
    in a meaningful way (not just as part of other words).
    """
    question_lower = question.lower()
    response_lower = response.lower()

    # Extract key terms from question (remove stop words)
    stop_words = {
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "the",
        "a",
        "an",
        "do",
        "does",
        "can",
        "could",
        "would",
        "should",
        "will",
        "be",
        "been",
        "being",
    }

    question_words = set(question_lower.split()) - stop_words

    if not question_words:
        return 1.0

    # Check how many question keywords appear in response
    matches = sum(1 for word in question_words if word in response_lower)

    relevance = matches / len(question_words)

    return relevance


def check_context_precision(sources: List[str], expected_keywords: List[str]) -> float:
    """
    Context Precision: Out of top-k chunks, how many were actually useful?

    Checks if retrieved sources contain expected keywords.
    """
    if not sources:
        return 0.0

    useful_chunks = 0

    for source in sources:
        source_lower = source.lower()
        # Check if any expected keyword appears in this source
        if any(kw.lower() in source_lower for kw in expected_keywords):
            useful_chunks += 1

    precision = useful_chunks / len(sources)

    return precision


def run_ragas_test(indexer, query_engine, test_case: Dict, top_k: int) -> Dict[str, Any]:
    """Run a single RAGAS test case with enhanced metrics."""
    temp_dir = tempfile.mkdtemp()

    try:
        # Create and index test document
        doc_path = os.path.join(temp_dir, "test_doc.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_DOCUMENT)

        indexer.index_document(doc_path)

        # Run query
        result = query_engine.query(test_case["question"])

        response_text = result.get("response", "")
        sources = [s.get("text", "") for s in result.get("sources", [])]
        source_scores = [
            s.get("score", s.get("similarity_score", 0.0)) for s in result.get("sources", [])
        ]

        # Calculate metrics
        expected_keywords = test_case.get("expected_keywords", [])

        faithfulness, unverified = check_faithfulness(response_text, sources)
        relevance = check_answer_relevance(test_case["question"], response_text)
        precision = check_context_precision(sources, expected_keywords)

        # ========== ENHANCED METRICS ==========

        # Source Citation: Does answer contain info from sources?
        source_citation_verified = False
        if sources:
            answer_keywords_in_sources = [
                kw for kw in expected_keywords if any(kw.lower() in src.lower() for src in sources)
            ]
            source_citation_verified = (
                len(answer_keywords_in_sources) >= len(expected_keywords) * 0.5
            )

        # Hallucination: Answer mentions info NOT in sources?
        hallucinated = False
        if response_text:
            has_keywords_in_answer = any(
                kw.lower() in response_text.lower() for kw in expected_keywords
            )
            has_keywords_in_sources = any(
                kw.lower() in src.lower() for kw in expected_keywords for src in sources
            )
            if has_keywords_in_answer and not has_keywords_in_sources:
                hallucinated = True

        # Confidence Score
        avg_confidence = sum(source_scores) / len(source_scores) if source_scores else 0.0

        # Calculate overall score (weighted average)
        # Faithfulness: 40%, Relevance: 40%, Precision: 20%
        overall = 0.4 * faithfulness + 0.4 * relevance + 0.2 * precision

        return {
            "success": True,
            "question": test_case["question"],
            "category": test_case["category"],
            "expected_keywords": expected_keywords,
            "faithfulness": faithfulness,
            "relevance": relevance,
            "precision": precision,
            "overall": overall,
            # Enhanced metrics
            "source_citation_verified": source_citation_verified,
            "hallucination_detected": hallucinated,
            "avg_confidence": avg_confidence,
            "unverified_claims": unverified,
            "response": response_text[:300],
            "sources_count": len(sources),
        }

    except Exception as e:
        return {
            "success": False,
            "question": test_case["question"],
            "error": str(e),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_ragas_tests(
    chunk_size: int = 1500,
    chunk_overlap: int = 100,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "llama3.2:1b",
) -> Dict[str, Any]:
    """Run all RAGAS-lite tests."""
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

        indexer = DocumentIndexer(session_id="test_ragas")
        query_engine = QueryEngine(
            session_id="test_ragas",
            model=llm_model,
            _skip_ollama_check=False,
        )

        results = []

        print(f"\nRunning RAGAS-Lite Tests")
        print(f"=" * 60)
        print(f"Configuration:")
        print(f"  Chunk Size: {chunk_size}")
        print(f"  Chunk Overlap: {chunk_overlap}")
        print(f"  Embedding Model: {embedding_model}")
        print(f"  Top-K: {top_k}")
        print(f"  LLM: {llm_model}")
        print(f"=" * 60)

        for i, test_case in enumerate(RAGAS_TEST_CASES, 1):
            print(f"\nTest {i}/{len(RAGAS_TEST_CASES)}: {test_case['question']}")
            result = run_ragas_test(indexer, query_engine, test_case, top_k)

            if result.get("success"):
                print(f"  Faithfulness: {result.get('faithfulness', 0):.2f}")
                print(f"  Relevance: {result.get('relevance', 0):.2f}")
                print(f"  Precision: {result.get('precision', 0):.2f}")
                print(f"  Source Citation: {result.get('source_citation_verified', False)}")
                print(f"  Hallucination: {result.get('hallucination_detected', False)}")
                print(f"  Avg Confidence: {result.get('avg_confidence', 0):.3f}")
                print(f"  Overall: {result.get('overall', 0):.2f}")
            else:
                print(f"  Error: {result.get('error')}")

            results.append(result)

        # Calculate aggregate scores
        total = len([r for r in results if r.get("success")])
        avg_faithfulness = (
            sum(r.get("faithfulness", 0) for r in results if r.get("success")) / total
            if total > 0
            else 0
        )
        avg_relevance = (
            sum(r.get("relevance", 0) for r in results if r.get("success")) / total
            if total > 0
            else 0
        )
        avg_precision = (
            sum(r.get("precision", 0) for r in results if r.get("success")) / total
            if total > 0
            else 0
        )
        avg_overall = (
            sum(r.get("overall", 0) for r in results if r.get("success")) / total
            if total > 0
            else 0
        )

        # Enhanced aggregate metrics
        citations_verified = sum(1 for r in results if r.get("source_citation_verified", False))
        hallucinations = sum(1 for r in results if r.get("hallucination_detected", False))
        confidence_scores = [r.get("avg_confidence", 0) for r in results if r.get("success")]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        )

        return {
            "total_tests": len(RAGAS_TEST_CASES),
            "successful": total,
            "metrics": {
                "faithfulness": {
                    "average": avg_faithfulness,
                    "description": "Are claims in answer from sources?",
                },
                "relevance": {
                    "average": avg_relevance,
                    "description": "Does answer address the question?",
                },
                "precision": {
                    "average": avg_precision,
                    "description": "Are top-k chunks actually useful?",
                },
                "source_citations_verified": {
                    "average": citations_verified / total if total > 0 else 0,
                    "description": "Does answer cite info from sources?",
                },
                "hallucination_rate": {
                    "average": hallucinations / total if total > 0 else 0,
                    "description": "Answer mentions info NOT in sources?",
                },
                "avg_confidence": {
                    "average": avg_confidence,
                    "description": "Mean similarity score from embeddings",
                },
                "overall": {
                    "average": avg_overall,
                    "formula": "0.4*faithfulness + 0.4*relevance + 0.2*precision",
                },
            },
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
    """Save RAGAS results to file."""
    import json
    from datetime import datetime

    output_path = Path(output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== BitRAG RAGAS-Lite Test Results ===\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total Tests: {results['total_tests']}\n")
        f.write(f"Successful: {results['successful']}\n\n")

        f.write(f"--- Aggregate Scores ---\n")
        metrics = results.get("metrics", {})
        for metric, data in metrics.items():
            f.write(f"{metric}: {data.get('average', 0):.3f}\n")
            f.write(f"  Description: {data.get('description', '')}\n")

        f.write(f"\n--- Configuration ---\n")
        for key, value in results.get("config", {}).items():
            f.write(f"  {key}: {value}\n")

        f.write(f"\n--- Per-Test Results ---\n")
        f.write("-" * 60 + "\n")

        for i, r in enumerate(results.get("results", []), 1):
            f.write(f"\nTest {i}: {r.get('question', 'N/A')}\n")
            f.write(f"  Category: {r.get('category', 'N/A')}\n")
            f.write(f"  Faithfulness: {r.get('faithfulness', 0):.3f}\n")
            f.write(f"  Relevance: {r.get('relevance', 0):.3f}\n")
            f.write(f"  Precision: {r.get('precision', 0):.3f}\n")
            # Enhanced metrics
            f.write(f"  Source Citation: {r.get('source_citation_verified', False)}\n")
            f.write(f"  Hallucination: {r.get('hallucination_detected', False)}\n")
            f.write(f"  Confidence: {r.get('avg_confidence', 0):.3f}\n")
            f.write(f"  Overall: {r.get('overall', 0):.3f}\n")
            f.write(f"  Sources: {r.get('sources_count', 0)}\n")
            if r.get("unverified_claims"):
                f.write(f"  Unverified: {r.get('unverified_claims')}\n")

        f.write(f"\n\n--- JSON Data ---\n")
        f.write(json.dumps(results, indent=2))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG RAGAS-Lite Test")
    parser.add_argument("--chunk-size", type=int, default=1500, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Chunk overlap")
    parser.add_argument(
        "--model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model"
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    parser.add_argument("--llm-model", default="llama3.2:1b", help="LLM model")
    parser.add_argument("--output", default="ragas_test_results.txt", help="Output file")
    parser.add_argument(
        "--results-dir", "-r", default="results",
        help="Directory to save results (default: results)"
    )

    args = parser.parse_args()

    print("Starting RAGAS-Lite Tests...")

    results = run_all_ragas_tests(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.model,
        top_k=args.top_k,
        llm_model=args.llm_model,
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
    print(f"Successful: {results['successful']}")
    print(f"\nScores:")
    for metric, data in results.get("metrics", {}).items():
        print(f"  {metric}: {data.get('average', 0):.3f}")
    print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
