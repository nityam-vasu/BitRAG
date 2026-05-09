#!/usr/bin/env python3
"""
BitRAG Test Runner

Runs all tests from CSV parameter files automatically.

================================================================================
INDEXING PARAMETERS (test_indexing_params.csv)
================================================================================

test_type         : Type of test (indexing/inference)
output_file       : Output filename to save results
input_file        : Path to file to index (PDF, TXT, etc.)
chunk_size        : Number of characters per chunk (default: 512)
                   - Smaller = more chunks, more precision
                   - Larger = fewer chunks, more context
chunk_overlap     : Overlap between chunks in characters (default: 50)
                   - Helps maintain context between chunks
embedding_model   : Model for generating embeddings
                   Options:
                   - sentence-transformers/all-MiniLM-L6-v2 (fast, 384dim)
                   - sentence-transformers/all-mpnet-base-v2 (accurate, 768dim)
                   - BAAI/bge-small-en-v1.5 (balanced, 384dim)
                   - BAAI/bge-base-en-v1.5 (accurate, 768dim)

================================================================================
INFERENCE PARAMETERS (test_inference_params.csv)
================================================================================

test_type         : Type of test (indexing/inference)
output_file       : Output filename to save results
model             : Ollama LLM model for inference
                   Options:
                   - llama3.2:1b, llama3.2 (fast, small)
                   - mistral (balanced)
                   - phi3:14b (reasoning)
                   - codellama:7b (code)
query             : User query/question to ask the model
system_prompt     : System prompt for the LLM (default: "You are a helpful assistant.")
top_k             : Number of similar chunks to retrieve (default: 3)
                   - Higher = more context, slower
                   - Lower = less context, faster
temperature       : Sampling temperature (default: 0.1)
                   - 0.0 = deterministic, focused
                   - 0.7 = balanced
                   - 1.0+ = creative, random
top_p             : Nucleus sampling threshold (default: 0.9)
                   - Higher = more diverse output
                   - Lower = more focused
top_k_ollama      : Ollama top-k sampling (default: 40)
                   - Number of tokens to consider
ctx               : Context window size in tokens (default: 2048)
                   - Maximum context the model can use
repeat_penalty    : Repetition penalty (default: 1.1)
                   - Higher = less repetition
                   - 1.0 = no penalty
seed             : Random seed (default: -1 for random)
                   - Set specific value for reproducibility
gpu_layers        : GPU layers to offload (default: -1 for all)
                   - -1 = all layers to GPU
                   - 0 = CPU only
threads           : CPU threads (default: -1 for auto)
batch             : Batch size for prompt processing (default: 512)
mmap              : Use memory mapping (default: true)
                   - true = memory map the model
                   - false = load into RAM
numa              : NUMA binding (default: true)
                   - true = use NUMA for memory
                   - false = ignore NUMA
format            : Output format (default: json)
                   - json = JSON format
                   - beauty = formatted text
embedding_model   : Model used for embedding documents
chunk_size        : Chunk size used when indexing
chunk_overlap     : Chunk overlap used when indexing

================================================================================
USAGE EXAMPLES
================================================================================

# Run all tests (dry run first to see what will run)
python run_all_tests.py --dry-run

# Run all tests for real
python run_all_tests.py

# Run only indexing tests
python run_all_tests.py --indexing

# Run only inference tests
python run_all_tests.py --inference

# Run specific test type
python run_all_tests.py --indexing --dry-run
python run_all_tests.py --inference --dry-run

================================================================================
OUTPUT
================================================================================

Results are saved to:
- testing/results_<timestamp>/ directory
- Individual output files as specified in CSV

Each output file contains:
- System Information (CPU, RAM, GPU)
- Configuration (models, parameters)
- Performance Metrics (timing, memory)
- Response and Sources

================================================================================
"""

import os
import sys
import csv
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root is parent directory (where test_indexing.py is)
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_SRC_PATH = os.path.join(_PROJECT_ROOT, 'src')
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

# Get Python path
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
    env.pop('PYTHONPATH', None)
    env["PYTHONPATH"] = _SRC_PATH
    env["CUDA_VISIBLE_DEVICES"] = ""
    return env

_PYTHON_PATH = get_python_path()


def run_indexing_test(params):
    """Run a single indexing test."""
    cmd = [
        _PYTHON_PATH, "test_indexing.py",
        "--input", params.get("input_file", "test_PDF/Test_Story.pdf"),
        "--output", params.get("output_file", "indexing_results.txt"),
        "--chunk-size", str(params.get("chunk_size", 512)),
        "--chunk-overlap", str(params.get("chunk_overlap", 50)),
        "--model", params.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
    ]
    
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PROJECT_ROOT, env=get_python_env())
    
    if result.returncode != 0:
        print(f"  ❌ FAILED: {result.stderr}")
        return False
    else:
        print(f"  ✅ SUCCESS")
        return True


def run_inference_test(params):
    """Run a single inference test."""
    cmd = [
        _PYTHON_PATH, "test_inference.py",
        "--model", params.get("model", "llama3.2:1b"),
        "--query", params.get("query", "What is this about?"),
        "--output", params.get("output_file", "inference_results.txt"),
        "--top-k", str(params.get("top_k", 3)),
        "--temperature", str(params.get("temperature", 0.1)),
        "--top-p", str(params.get("top_p", 0.9)),
        "--ollama-top-k", str(params.get("top_k_ollama", 40)),
        "--ctx", str(params.get("ctx", 2048)),
        "--repeat-penalty", str(params.get("repeat_penalty", 1.1)),
        "--seed", str(params.get("seed", -1)),
        "--num-gpu-layers", str(params.get("gpu_layers", -1)),
        "--threads", str(params.get("threads", -1)),
        "--batch", str(params.get("batch", 512)),
        "--embedding-model", params.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
        "--chunk-size", str(params.get("chunk_size", 512)),
        "--chunk-overlap", str(params.get("chunk_overlap", 50)),
    ]
    
    # Add mmap/numa flags
    if params.get("mmap", True):
        cmd.append("--mmap")
    else:
        cmd.append("--no-mmap")
    
    if params.get("numa", True):
        cmd.append("--numa")
    else:
        cmd.append("--no-numa")
    
    # Add format
    cmd.extend(["--format", params.get("format", "json")])
    
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PROJECT_ROOT, env=get_python_env())
    
    if result.returncode != 0:
        print(f"  ❌ FAILED: {result.stderr}")
        return False
    else:
        print(f"  ✅ SUCCESS")
        return True


def load_csv(filepath):
    """Load CSV file and return list of dictionaries."""
    params_list = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string booleans
            for key in row:
                if row[key].lower() == 'true':
                    row[key] = True
                elif row[key].lower() == 'false':
                    row[key] = False
                elif row[key].lower() == 'none' or row[key] == '':
                    row[key] = None
            params_list.append(row)
    return params_list


def run_tests(test_type=None, dry_run=False):
    """Run tests from CSV files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create results directory
    results_dir = Path(_PROJECT_ROOT) / "testing" / f"results_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    total_passed = 0
    total_failed = 0
    
    # Run indexing tests
    if test_type is None or test_type == "indexing":
        indexing_csv = Path(_PROJECT_ROOT) / "testing" / "test_indexing_params.csv"
        if indexing_csv.exists():
            print(f"\n{'='*60}")
            print("Running INDEXING tests...")
            print('='*60)
            
            params_list = load_csv(indexing_csv)
            for i, params in enumerate(params_list, 1):
                print(f"\nTest {i}/{len(params_list)}: {params.get('output_file', 'unknown')}")
                
                if dry_run:
                    print(f"  [DRY RUN] Would run with: {params}")
                    continue
                
                success = run_indexing_test(params)
                if success:
                    total_passed += 1
                else:
                    total_failed += 1
                
                # Small delay between tests
                time.sleep(0.5)
    
    # Run inference tests
    if test_type is None or test_type == "inference":
        inference_csv = Path(_PROJECT_ROOT) / "testing" / "test_inference_params.csv"
        if inference_csv.exists():
            print(f"\n{'='*60}")
            print("Running INFERENCE tests...")
            print('='*60)
            
            params_list = load_csv(inference_csv)
            for i, params in enumerate(params_list, 1):
                print(f"\nTest {i}/{len(params_list)}: {params.get('output_file', 'unknown')}")
                
                if dry_run:
                    print(f"  [DRY RUN] Would run with: {params}")
                    continue
                
                success = run_inference_test(params)
                if success:
                    total_passed += 1
                else:
                    total_failed += 1
                
                # Small delay between tests
                time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Total:  {total_passed + total_failed}")
    print(f"Results saved to: {results_dir}")


def main():
    parser = argparse.ArgumentParser(description="BitRAG Test Runner")
    parser.add_argument("--indexing", action="store_true", help="Run indexing tests only")
    parser.add_argument("--inference", action="store_true", help="Run inference tests only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be run without executing")
    
    args = parser.parse_args()
    
    # Determine test type
    if args.indexing and not args.inference:
        test_type = "indexing"
    elif args.inference and not args.indexing:
        test_type = "inference"
    else:
        test_type = None  # Run both
    
    print(f"BitRAG Test Runner")
    print(f"{'='*60}")
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No tests will be executed")
    print()
    
    run_tests(test_type=test_type, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
