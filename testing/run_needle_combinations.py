#!/usr/bin/env python3
"""
BitRAG Needle Test - Run All CSV Combinations

Reads combinations from CSV and runs needle tests for each.
Outputs comprehensive metrics to CSV for analysis.

Usage:
    python run_needle_combinations.py --input test_needle_combinations.csv
    python run_needle_combinations.py --input test_needle_combinations.csv --parallel 4
"""

import os
import sys
import csv
import json
import time
import shutil
import tempfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_NEEDLE_DOCS_DIR = os.path.join(_PROJECT_ROOT, "testing", "needle_docs")

# Force CPU-only mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""

sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

# Test cases
NEEDLE_TESTS = [
    {"file": "01_server_password.txt", "query": "What is the server room password?", "expected_keywords": ["QUANTUM-2026-X7", "server room"]},
    {"file": "02_ceo_mobile.txt", "query": "What is the CEO's personal mobile number?", "expected_keywords": ["+1-555-0127-8944", "CEO"]},
    {"file": "03_deadline.txt", "query": "When is the project deadline?", "expected_keywords": ["November 15th", "2026", "5:00 PM EST"]},
    {"file": "04_hidden_password.txt", "query": "What is the hidden password for backup system?", "expected_keywords": ["龙卷风2026", "tornado2026"]},
    {"file": "05_usb_label.txt", "query": "What is the label on the USB drive with encryption key?", "expected_keywords": ["KEY-SILVER-773", "USB"]},
    {"file": "06_budget.txt", "query": "What is the annual AI research budget?", "expected_keywords": ["$2,847,500", "AI research"]},
    {"file": "07_building_code.txt", "query": "What is the security code for the main building?", "expected_keywords": ["4921", "north entrance"]},
    {"file": "08_wifi_password.txt", "query": "What is the guest WiFi password?", "expected_keywords": ["WelcomeGuest2026", "Corp-Guest"]},
    {"file": "09_meeting_code.txt", "query": "What is the booking code for client meeting room?", "expected_keywords": ["MTG-ROOM-ALPHA-77"]},
    {"file": "10_api_endpoint.txt", "query": "What is the production API endpoint URL?", "expected_keywords": ["api.company.com", "v2", "prod"]},
    {"file": "11_db_password.txt", "query": "What is the main database password?", "expected_keywords": ["PostgresSecure#2026"]},
    {"file": "12_license_code.txt", "query": "What is the software activation code?", "expected_keywords": ["ACTIV-8F3D-2026-X"]},
    {"file": "13_emergency_contact.txt", "query": "What is the emergency contact number for after-hours?", "expected_keywords": ["+1-555-0199", "SUPPORT", "24/7"]},
    {"file": "14_vault_combo.txt", "query": "What is the vault combination?", "expected_keywords": ["34-7-19-42", "CFO"]},
    {"file": "15_satellite_phone.txt", "query": "What is the satellite phone number?", "expected_keywords": ["+1-555-8823", "MARS"]},
    {"file": "16_launch_date.txt", "query": "When is the product launch date?", "expected_keywords": ["June 1st", "2026"]},
    {"file": "17_bonus_q1.txt", "query": "What is the Q1 2026 quarterly bonus percentage?", "expected_keywords": ["15%", "April 15th"]},
    {"file": "18_ssh_key.txt", "query": "What is the admin SSH key fingerprint?", "expected_keywords": ["SHA256:A1B2C3D4E5F6G7H8I9J0"]},
    {"file": "19_vpn_code.txt", "query": "What is the VPN access code?", "expected_keywords": ["VPN-SPLIT-TUNNEL-442"]},
    {"file": "20_report_id.txt", "query": "What is the confidential report ID?", "expected_keywords": ["RPT-2026-ALPHA-OMEGA-X", "Top Secret"]},
]

DISTRACTOR_CONTENT = """
General Company Information. Founded 2010. 500+ employees. 
Technology sector. Software development focus. 
San Francisco, California office.
Monday-Friday 9AM-6PM.
"""


def load_combinations(csv_file: str) -> List[Dict[str, str]]:
    """Load test combinations from CSV."""
    combinations = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combinations.append(row)
    return combinations


def run_single_needle_test(indexer, query_engine, test_case: Dict, top_k: int) -> Dict[str, Any]:
    """Run a single needle test with full metrics."""
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

        # Index the needle document
        needle_path = os.path.join(_NEEDLE_DOCS_DIR, test_case["file"])
        if os.path.exists(needle_path):
            indexer.index_document(needle_path)
        else:
            return {"success": False, "error": f"Needle file not found"}

        # Query
        question = test_case["query"]
        start_time = time.time()
        result = query_engine.query(question)
        query_time = time.time() - start_time

        # Extract metrics
        source_files = []
        source_scores = []
        for source in result.get("sources", []):
            file_name = source.get("file_name") or source.get("metadata", {}).get("file_name", "")
            source_files.append(file_name)
            score = source.get("score", source.get("similarity_score", 0.0))
            source_scores.append(score)

        # Check if needle was in top-k
        needle_file_retrieved = any(test_case["file"] in f for f in source_files)
        
        # Check answer
        answer_text = result.get("response", "")
        expected_keywords = test_case.get("expected_keywords", [])
        
        # Exact keyword match
        answer_contains_info = any(kw.lower() in answer_text.lower() for kw in expected_keywords)
        
        # Keyword in sources
        src_text = " ".join([s.get("text", "") for s in result.get("sources", [])])
        keywords_in_sources = [kw for kw in expected_keywords if kw.lower() in src_text.lower()]
        
        # Precision: what % of retrieved is relevant
        relevant_count = sum(1 for s in result.get("sources", []) 
                         if any(kw.lower() in s.get("text", "").lower() for kw in expected_keywords))
        precision = relevant_count / len(result.get("sources", [1])) if result.get("sources") else 0
        
        # Recall: what % of keywords found
        recall = len(keywords_in_sources) / len(expected_keywords) if expected_keywords else 0
        
        # Avg confidence
        avg_confidence = sum(source_scores) / len(source_scores) if source_scores else 0
        
        # F1 score
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "success": True,
            "file": test_case["file"],
            "needle_file_retrieved": needle_file_retrieved,
            "answer_contains_info": answer_contains_info,
            "keywords_in_sources": keywords_in_sources,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "query_time": query_time,
            "avg_confidence": avg_confidence,
        }

    except Exception as e:
        return {"success": False, "file": test_case["file"], "error": str(e)}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_needle_tests(
    chunk_size: int = 1500,
    chunk_overlap: int = 100,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
    llm_model: str = "qwen3.5:0.8b",
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
            top_k=top_k,
        )

        indexer = DocumentIndexer(session_id="test_needle")
        query_engine = QueryEngine(
            session_id="test_needle",
            model=llm_model,
            _skip_ollama_check=False,
        )

        # Run each test case
        all_results = []
        files_retrieved = 0
        answers_correct = 0
        precision_scores = []
        recall_scores = []
        f1_scores = []
        confidence_scores = []
        query_times = []

        for test_case in NEEDLE_TESTS:
            result = run_single_needle_test(indexer, query_engine, test_case, top_k)
            
            if result.get("success"):
                if result.get("needle_file_retrieved"):
                    files_retrieved += 1
                if result.get("answer_contains_info"):
                    answers_correct += 1
                precision_scores.append(result.get("precision", 0))
                recall_scores.append(result.get("recall", 0))
                f1_scores.append(result.get("f1", 0))
                confidence_scores.append(result.get("avg_confidence", 0))
                query_times.append(result.get("query_time", 0))
            
            all_results.append(result)

        total = len(NEEDLE_TESTS)
        
        return {
            "total_tests": total,
            "files_retrieved": files_retrieved,
            "answers_correct": answers_correct,
            "retrieval_accuracy": 100 * files_retrieved / total,
            "answer_accuracy": 100 * answers_correct / total,
            "avg_precision": sum(precision_scores) / len(precision_scores) if precision_scores else 0,
            "avg_recall": sum(recall_scores) / len(recall_scores) if recall_scores else 0,
            "avg_f1": sum(f1_scores) / len(f1_scores) if f1_scores else 0,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "avg_query_time": sum(query_times) / len(query_times) if query_times else 0,
            "config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "llm_model": llm_model,
            },
            "test_results": all_results,
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_combination(combo: Dict[str, str], output_dir: str, combo_idx: int) -> Tuple[Dict, int, str]:
    """Run a single combination."""
    chunk_size = int(combo.get("chunk_size", 1500))
    chunk_overlap = int(combo.get("chunk_overlap", 100))
    embedding_model = combo.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
    top_k = int(combo.get("top_k", 3))
    llm_model = combo.get("llm_model", "qwen3.5:0.8b")
    combo_id = combo.get("combo_id", str(combo_idx))
    
    combo_name = f"c{combo_id}_{chunk_size}_{chunk_overlap}_{embedding_model.split('/')[-1]}_{top_k}_{llm_model.replace(':', '-')}"
    
    print(f"\n[{combo_idx}] Running: {combo_name}")
    
    start_time = time.time()
    results = run_all_needle_tests(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model=embedding_model,
        top_k=top_k,
        llm_model=llm_model,
    )
    elapsed = time.time() - start_time
    
    results["elapsed_time"] = elapsed
    results["combination_name"] = combo_name
    results["combo_id"] = combo_id
    
    return results, combo_idx, combo_name


def write_csv_output(all_results: List[Dict], output_file: str):
    """Write CSV output for analysis."""
    fieldnames = [
        "combo_id", "chunk_size", "chunk_overlap", "embedding_model", "top_k", "llm_model",
        "retrieval_accuracy", "answer_accuracy", "precision", "recall", "f1", 
        "avg_confidence", "avg_query_time", "elapsed_time",
        "embedding_short", "llm_short"
    ]
    
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in all_results:
            config = r.get("config", {})
            emb = config.get("embedding_model", "")
            llm = config.get("llm_model", "")
            
            writer.writerow({
                "combo_id": r.get("combo_id", ""),
                "chunk_size": config.get("chunk_size", ""),
                "chunk_overlap": config.get("chunk_overlap", ""),
                "embedding_model": emb,
                "top_k": config.get("top_k", ""),
                "llm_model": llm,
                "retrieval_accuracy": round(r.get("retrieval_accuracy", 0), 2),
                "answer_accuracy": round(r.get("answer_accuracy", 0), 2),
                "precision": round(r.get("avg_precision", 0), 4),
                "recall": round(r.get("avg_recall", 0), 4),
                "f1": round(r.get("avg_f1", 0), 4),
                "avg_confidence": round(r.get("avg_confidence", 0), 4),
                "avg_query_time": round(r.get("avg_query_time", 0), 3),
                "elapsed_time": round(r.get("elapsed_time", 0), 1),
                "embedding_short": emb.split("/")[-1] if emb else "",
                "llm_short": llm.split(":")[0] if llm else "",
            })


def generate_report(all_results: List[Dict], output_dir: str):
    """Generate markdown report."""
    report_file = os.path.join(output_dir, "report.md")
    
    with open(report_file, "w") as f:
        f.write(f"# BitRAG Needle-in-Haystack Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Summary\n\n")
        f.write(f"- Total Combinations: {len(all_results)}\n")
        
        # Find best
        if all_results:
            best_by_retrieval = max(all_results, key=lambda x: x.get("retrieval_accuracy", 0))
            best_by_f1 = max(all_results, key=lambda x: x.get("avg_f1", 0))
            best_by_speed = min(all_results, key=lambda x: x.get("avg_query_time", 999))
            
            f.write(f"## Best Configurations\n\n")
            f.write(f"### Best by Retrieval Accuracy\n")
            f.write(f"```\n{best_by_retrieval.get('config')}\n")
            f.write(f"Retrieval: {best_by_retrieval.get('retrieval_accuracy'):.1f}%\n")
            f.write(f"```\n\n")
            
            f.write(f"### Best by F1 Score\n")
            f.write(f"```\n{best_by_f1.get('config')}\n")
            f.write(f"F1: {best_by_f1.get('avg_f1'):.3f}\n")
            f.write(f"```\n\n")
            
            f.write(f"### Fastest\n")
            f.write(f"```\n{best_by_speed.get('config')}\n")
            f.write(f"Avg Query Time: {best_by_speed.get('avg_query_time'):.2f}s\n")
            f.write(f"```\n\n")
        
        # Analysis by variables
        f.write(f"## Analysis by Variables\n\n")
        
        # Group by chunk_size
        f.write(f"### Effect of Chunk Size\n\n")
        size_groups = {}
        for r in all_results:
            cs = r.get("config", {}).get("chunk_size", "")
            if cs not in size_groups:
                size_groups[cs] = []
            size_groups[cs].append(r.get("retrieval_accuracy", 0))
        
        for cs in sorted(size_groups.keys()):
            accs = size_groups[cs]
            f.write(f"- {cs}: {sum(accs)/len(accs):.1f}% avg (n={len(accs)})\n")
        
        # Group by embedding
        f.write(f"\n### Effect of Embedding Model\n\n")
        emb_groups = {}
        for r in all_results:
            emb = r.get("config", {}).get("embedding_model", "").split("/")[-1]
            if emb not in emb_groups:
                emb_groups[emb] = []
            emb_groups[emb].append(r.get("retrieval_accuracy", 0))
        
        for emb in sorted(emb_groups.keys()):
            accs = emb_groups[emb]
            f.write(f"- {emb}: {sum(accs)/len(accs):.1f}% avg (n={len(accs)})\n")
        
        # Group by top_k
        f.write(f"\n### Effect of Top-K\n\n")
        k_groups = {}
        for r in all_results:
            tk = r.get("config", {}).get("top_k", "")
            if tk not in k_groups:
                k_groups[tk] = []
            k_groups[tk].append(r.get("retrieval_accuracy", 0))
        
        for tk in sorted(k_groups.keys()):
            accs = k_groups[tk]
            f.write(f"- top-{tk}: {sum(accs)/len(accs):.1f}% avg (n={len(accs)})\n")
        
        # Full table
        f.write(f"\n## Complete Results\n\n")
        f.write(f"| # | Chunk | Overlap | Embedding | Top-K | LLM | Retrieval | Precision | Recall | F1 |\n")
        f.write(f"|---|-------|--------|----------|-------|-----|----------|-----------|--------|----|\n")
        
        for i, r in enumerate(all_results, 1):
            cfg = r.get("config", {})
            f.write(f"| {i} | {cfg.get('chunk_size')} | {cfg.get('chunk_overlap')} | "
                  f"{cfg.get('embedding_model','').split('/')[-1][:15]} | "
                  f"{cfg.get('top_k')} | "
                  f"{cfg.get('llm_model','').split(':')[0][:8]} | "
                  f"{r.get('retrieval_accuracy'):.1f}% | "
                  f"{r.get('avg_precision'):.3f} | "
                  f"{r.get('avg_recall'):.3f} | "
                  f"{r.get('avg_f1'):.3f} |\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run needle tests from CSV")
    parser.add_argument("--input", "-i", default="test_needle_combinations.csv")
    parser.add_argument("--output", "-o", default="combination_results")
    parser.add_argument("--parallel", "-p", type=int, default=1)
    parser.add_argument("--csv", action="store_true", help="Output CSV analysis file")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    
    args = parser.parse_args()
    
    # Resolve paths
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = Path(_SCRIPT_DIR) / input_path
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(_SCRIPT_DIR, f"{args.output}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading: {input_path}")
    combinations = load_combinations(str(input_path))
    print(f"Found {len(combinations)} combinations")
    print(f"Output: {output_dir}")
    
    # Run
    all_results = []
    start_time = time.time()
    
    if args.parallel > 1:
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {executor.submit(run_combination, c, output_dir, i): i 
                     for i, c in enumerate(combinations, 1)}
            
            for future in as_completed(futures):
                i = futures[future]
                try:
                    result, idx, name = future.result()
                    all_results.append(result)
                    status = "OK" if result.get("retrieval_accuracy", 0) >= 50 else "LOW"
                    print(f"[{idx}] {name}: {result['retrieval_accuracy']:.1f}% ({status})")
                except Exception as e:
                    print(f"[{i}] ERROR: {e}")
    else:
        for i, combo in enumerate(combinations, 1):
            try:
                result, idx, name = run_combination(combo, output_dir, i)
                all_results.append(result)
                status = "OK" if result.get("retrieval_accuracy", 0) >= 50 else "LOW"
                print(f"[{i}] {name}: {result['retrieval_accuracy']:.1f}% ({status})")
            except Exception as e:
                print(f"[{i}] ERROR: {e}")
    
    total_time = time.time() - start_time
    
    # Sort by retrieval accuracy
    all_results.sort(key=lambda x: x.get("retrieval_accuracy", 0), reverse=True)
    
    # Output options
    if args.csv:
        csv_file = os.path.join(output_dir, "analysis.csv")
        write_csv_output(all_results, csv_file)
        print(f"CSV: {csv_file}")
    
    if args.report:
        generate_report(all_results, output_dir)
        print(f"Report: {os.path.join(output_dir, 'report.md')}")
    
    # Summary table
    print(f"\n{'=' * 90}")
    print(f"{'#':<3} {'Config':<45} {'Retriv':<8} {'Prec':<8} {'Rec':<8} {'F1':<8}")
    print(f"{'-' * 90}")
    
    for i, r in enumerate(all_results, 1):
        cfg = r.get("config", {})
        name = f"{cfg.get('chunk_size')}/{cfg.get('chunk_overlap')}/{cfg.get('embedding_model','').split('/')[-1][:12]}/{cfg.get('top_k')}/{cfg.get('llm_model','').split(':')[0][:8]}"
        retr = f"{r.get('retrieval_accuracy'):.1f}%"
        prec = f"{r.get('avg_precision').:.3f}"
        rec = f"{r.get('avg_recall'):.3f}"
        f1 = f"{r.get('avg_f1'):.3f}"
        print(f"{i:<3} {name:<45} {retr:<8} {prec:<8} {rec:<8} {f1:<8}")
    
    print(f"{'-' * 90}")
    print(f"Total time: {total_time:.1f}s | Results: {output_dir}")


if __name__ == "__main__":
    main()