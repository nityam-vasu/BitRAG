#!/usr/bin/env python3
"""
BitRAG CSV Test Runner

Runs indexing or inference tests based on CSV configuration file.
Outputs results to both text files and CSV for data analysis.

Usage:
    python run_csv_tests.py test_indexing_params.csv
    python run_csv_tests.py test_inference_params.csv
    python run_csv_tests.py test_indexing_params.csv --parallel
"""

import argparse
import csv
import os
import re
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
TEST_DIR = SCRIPT_DIR


def get_venv_python() -> str:
    """Get Python path from venv or .venv."""
    if (PROJECT_ROOT / ".venv/bin/python").exists():
        return str((PROJECT_ROOT / ".venv/bin/python").resolve())
    elif (PROJECT_ROOT / "venv/bin/python").exists():
        return str((PROJECT_ROOT / "venv/bin/python").resolve())
    return sys.executable


def read_csv(csv_path: str) -> List[Dict[str, str]]:
    """Read and parse CSV file."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def parse_value(text: str, pattern: str) -> Optional[str]:
    """Extract value from text using regex pattern."""
    try:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except:
        pass
    return None


def parse_indexing_output(output_file: Path) -> Dict[str, Any]:
    """Parse indexing test output file to extract metrics."""
    metrics = {
        'total_indexing_time_seconds': '',
        'embedding_generation_time_seconds': '',
        'vector_storage_time_seconds': '',
        'memory_used_mb': '',
        'peak_memory_mb': '',
        'cpu_usage_percent': '',
        'total_chunks': '',
        'document_type': '',
        'file_size_mb': '',
        'total_characters': '',
        'success': '',
        'error': '',
    }
    
    if not output_file.exists():
        return metrics
    
    content = output_file.read_text(encoding='utf-8')
    
    # Extract metrics using regex patterns
    patterns = {
        'total_indexing_time_seconds': r'total_indexing_time_seconds:\s*([\d.]+)',
        'embedding_generation_time_seconds': r'embedding_generation_time_seconds:\s*([\d.]+)',
        'vector_storage_time_seconds': r'vector_storage_time_seconds:\s*([\d.]+)',
        'memory_used_mb': r'memory_used_mb:\s*([\d.]+)',
        'peak_memory_mb': r'peak_memory_mb:\s*([\d.]+)',
        'cpu_usage_percent': r'cpu_usage_percent:\s*([\d.]+)',
        'total_chunks': r'total_chunks:\s*(\d+)',
        'document_type': r'document_type:\s*(\w+)',
        'file_size_mb': r'file_size_mb:\s*([\d.]+)',
        'total_characters': r'total_characters:\s*(\d+)',
        'success': r'indexed:\s*(True|False)',
        'error': r'error:\s*(.+)',
    }
    
    for key, pattern in patterns.items():
        metrics[key] = parse_value(content, pattern) or ''
    
    return metrics


def parse_inference_output(output_file: Path) -> Dict[str, Any]:
    """Parse inference test output file to extract metrics."""
    metrics = {
        'total_inference_time_seconds': '',
        'retrieval_time_seconds': '',
        'llm_generation_time_seconds': '',
        'time_to_first_token_seconds': '',
        'time_per_token_seconds': '',
        'tokens_generated': '',
        'tokens_per_second': '',
        'memory_used_mb': '',
        'peak_memory_mb': '',
        'cpu_usage_percent': '',
        'retrieved_chunks': '',
        'prompt_tokens': '',
        'completion_tokens': '',
        'total_tokens': '',
        'support_reasoning': '',
        'response_length_chars': '',
        'response_length_words': '',
        'success': '',
        'error': '',
    }
    
    if not output_file.exists():
        return metrics
    
    content = output_file.read_text(encoding='utf-8')
    
    # Extract metrics using regex patterns
    patterns = {
        'total_inference_time_seconds': r'total_inference_time_seconds:\s*([\d.]+)',
        'retrieval_time_seconds': r'retrieval_time_seconds:\s*([\d.]+)',
        'llm_generation_time_seconds': r'llm_generation_time_seconds:\s*([\d.]+)',
        'time_to_first_token_seconds': r'time_to_first_token_seconds:\s*([\d.]+)',
        'time_per_token_seconds': r'time_per_token_seconds:\s*([\d.]+)',
        'tokens_generated': r'tokens_generated:\s*(\d+)',
        'tokens_per_second': r'tokens_per_second:\s*([\d.]+)',
        'memory_used_mb': r'memory_used_mb:\s*([\d.]+)',
        'peak_memory_mb': r'peak_memory_mb:\s*([\d.]+)',
        'cpu_usage_percent': r'cpu_usage_percent:\s*([\d.]+)',
        'retrieved_chunks': r'retrieved_chunks:\s*(\d+)',
        'prompt_tokens': r'prompt_tokens:\s*(\d+)',
        'completion_tokens': r'completion_tokens:\s*(\d+)',
        'total_tokens': r'total_tokens:\s*(\d+)',
        'support_reasoning': r'support_reasoning:\s*(\d+)',
        'response_length_chars': r'response_length_chars:\s*(\d+)',
        'response_length_words': r'response_length_words:\s*(\d+)',
        'success': r'success:\s*(True|False)',
        'error': r'error:\s*(.+)',
    }
    
    for key, pattern in patterns.items():
        metrics[key] = parse_value(content, pattern) or ''
    
    return metrics


def run_indexing_test(row: Dict[str, str], results_dir: Path) -> Dict[str, Any]:
    """Run a single indexing test."""
    output_file = row.get('output_file', 'indexing_results.txt')
    input_file = row.get('input_file', '')
    chunk_size = row.get('chunk_size', '512')
    chunk_overlap = row.get('chunk_overlap', '50')
    embedding_model = row.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # Build command
    python = get_venv_python()
    cmd = [
        python,
        str(TEST_DIR / 'test_indexing.py'),
        '--input', input_file,
        '--output', str(results_dir / output_file),
        '--chunk-size', chunk_size,
        '--chunk-overlap', chunk_overlap,
        '--model', embedding_model,
    ]
    
    print(f"  Running: {' '.join(cmd)}")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start
    
    # Parse output file to get metrics
    metrics = parse_indexing_output(results_dir / output_file)
    
    return {
        'success': result.returncode == 0,
        'duration': duration,
        'output': result.stdout,
        'error': result.stderr if result.returncode != 0 else None,
        'metrics': metrics,
        'input_params': {
            'input_file': input_file,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'embedding_model': embedding_model,
        }
    }


def run_inference_test(row: Dict[str, str], results_dir: Path) -> Dict[str, Any]:
    """Run a single inference test."""
    output_file = row.get('output_file', 'inference_results.txt')
    model = row.get('model', 'llama3.2:1b')
    query = row.get('query', '')
    system_prompt = row.get('system_prompt', 'You are a helpful assistant.')
    top_k = row.get('top_k', '3')
    temperature = row.get('temperature', '0.1')
    top_p = row.get('top_p', '0.9')
    top_k_ollama = row.get('top_k_ollama', '40')
    ctx = row.get('ctx', '2048')
    repeat_penalty = row.get('repeat_penalty', '1.1')
    seed = row.get('seed', '-1')
    gpu_layers = row.get('gpu_layers', '-1')
    threads = row.get('threads', '-1')
    batch = row.get('batch', '512')
    mmap = row.get('mmap', 'true').lower() == 'true'
    numa = row.get('numa', 'true').lower() == 'true'
    fmt = row.get('format', 'json')
    embedding_model = row.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
    chunk_size = row.get('chunk_size', '512')
    chunk_overlap = row.get('chunk_overlap', '50')
    
    # Build command
    python = get_venv_python()
    cmd = [
        python,
        str(TEST_DIR / 'test_inference.py'),
        '--model', model,
        '--query', query,
        '--output', str(results_dir / output_file),
        '--system-prompt', system_prompt,
        '--top-k', top_k,
        '--temperature', temperature,
        '--top-p', top_p,
        '--ollama-top-k', top_k_ollama,
        '--ctx', ctx,
        '--repeat-penalty', repeat_penalty,
        '--seed', seed,
        '--num-gpu-layers', gpu_layers,
        '--threads', threads,
        '--batch', batch,
        '--format', fmt,
        '--embedding-model', embedding_model,
        '--chunk-size', chunk_size,
        '--chunk-overlap', chunk_overlap,
    ]
    
    if not mmap:
        cmd.append('--no-mmap')
    if not numa:
        cmd.append('--no-numa')
    
    print(f"  Running: {' '.join(cmd)}")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start
    
    # Parse output file to get metrics
    metrics = parse_inference_output(results_dir / output_file)
    
    return {
        'success': result.returncode == 0,
        'duration': duration,
        'output': result.stdout,
        'error': result.stderr if result.returncode != 0 else None,
        'metrics': metrics,
        'input_params': {
            'model': model,
            'query': query,
            'system_prompt': system_prompt,
            'top_k': top_k,
            'temperature': temperature,
            'top_p': top_p,
            'top_k_ollama': top_k_ollama,
            'ctx': ctx,
            'repeat_penalty': repeat_penalty,
            'seed': seed,
            'gpu_layers': gpu_layers,
            'threads': threads,
            'batch': batch,
            'mmap': str(mmap),
            'numa': str(numa),
            'format': fmt,
            'embedding_model': embedding_model,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
        }
    }


def save_results_csv(results: List[Dict[str, Any]], test_type: str, results_dir: Path, csv_path: str) -> None:
    """Save test results to CSV for data analysis."""
    csv_file = Path(csv_path)
    
    if test_type == 'indexing':
        # CSV columns for indexing tests
        fieldnames = [
            'test_id', 'output_file', 'success', 'duration_seconds',
            'input_file', 'chunk_size', 'chunk_overlap', 'embedding_model',
            'total_indexing_time_seconds', 'embedding_generation_time_seconds',
            'vector_storage_time_seconds', 'memory_used_mb', 'peak_memory_mb',
            'cpu_usage_percent', 'total_chunks', 'document_type', 'file_size_mb',
            'total_characters', 'error'
        ]
    else:
        # CSV columns for inference tests
        fieldnames = [
            'test_id', 'output_file', 'success', 'duration_seconds',
            'model', 'query', 'system_prompt', 'top_k', 'temperature', 'top_p',
            'top_k_ollama', 'ctx', 'repeat_penalty', 'seed', 'gpu_layers',
            'threads', 'batch', 'mmap', 'numa', 'format',
            'embedding_model', 'chunk_size', 'chunk_overlap',
            'total_inference_time_seconds', 'retrieval_time_seconds',
            'llm_generation_time_seconds', 'time_to_first_token_seconds',
            'time_per_token_seconds', 'tokens_generated', 'tokens_per_second',
            'memory_used_mb', 'peak_memory_mb', 'cpu_usage_percent',
            'retrieved_chunks', 'prompt_tokens', 'completion_tokens',
            'total_tokens', 'support_reasoning', 'response_length_chars',
            'response_length_words', 'error'
        ]
    
    output_csv = results_dir / f'results_{csv_file.stem}.csv'
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            row_data = {
                'test_id': r['row'],
                'output_file': r['output_file'],
                'success': r['success'],
                'duration_seconds': f"{r['duration']:.4f}",
            }
            
            # Add input params
            if 'input_params' in r:
                for k, v in r['input_params'].items():
                    row_data[k] = v
            
            # Add metrics
            if 'metrics' in r:
                for k, v in r['metrics'].items():
                    row_data[k] = v
            
            # Add error
            if r.get('error'):
                row_data['error'] = r['error'][:500]  # Limit error length
            
            writer.writerow(row_data)
    
    print(f"CSV results saved to: {output_csv}")


def run_tests(csv_path: str, parallel: bool = False) -> None:
    """Run all tests from CSV file."""
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Read CSV
    rows = read_csv(csv_path)
    
    if not rows:
        print("No test rows found in CSV.")
        sys.exit(1)
    
    # Get test type from first row
    test_type = rows[0].get('test_type', '').lower()
    
    if not test_type:
        print("Error: test_type not found in CSV.")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"BitRAG CSV Test Runner")
    print(f"{'='*60}")
    print(f"CSV file: {csv_path}")
    print(f"Test type: {test_type}")
    print(f"Total tests: {len(rows)}")
    print(f"Parallel: {parallel}")
    print(f"{'='*60}\n")
    
    # Create results directory
    results_dir = TEST_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Determine which script to use
    if 'indexing' in test_type:
        run_func = run_indexing_test
    elif 'inference' in test_type:
        run_func = run_inference_test
    else:
        print(f"Error: Unknown test_type: {test_type}")
        sys.exit(1)
    
    # Run tests
    results = []
    success_count = 0
    fail_count = 0
    
    for i, row in enumerate(rows, 1):
        output_file = row.get('output_file', f'test_{i}.txt')
        print(f"\n[{i}/{len(rows)}] Running: {output_file}")
        
        result = run_func(row, results_dir)
        results.append({
            'row': i,
            'output_file': output_file,
            **result
        })
        
        if result['success']:
            success_count += 1
            print(f"  ✓ Success ({result['duration']:.2f}s)")
        else:
            fail_count += 1
            print(f"  ✗ Failed ({result['duration']:.2f}s)")
            if result['error']:
                print(f"    Error: {result['error'][:200]}")
        
        # Small delay between tests
        if not parallel:
            time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {len(rows)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Success rate: {success_count/len(rows)*100:.1f}%")
    print(f"{'='*60}\n")
    
    # Save summary text
    summary_file = results_dir / f'summary_{csv_file.stem}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"BitRAG CSV Test Summary\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"CSV file: {csv_path}\n")
        f.write(f"Test type: {test_type}\n")
        f.write(f"Total tests: {len(rows)}\n")
        f.write(f"Successful: {success_count}\n")
        f.write(f"Failed: {fail_count}\n")
        f.write(f"\nDetails:\n")
        for r in results:
            status = "SUCCESS" if r['success'] else "FAILED"
            f.write(f"  [{r['row']}] {r['output_file']}: {status} ({r['duration']:.2f}s)\n")
    
    print(f"Summary saved to: {summary_file}")
    
    # Save results as CSV for data analysis
    save_results_csv(results, test_type, results_dir, csv_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run BitRAG tests from CSV configuration file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "csv_file",
        help="Path to CSV configuration file"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel (may cause issues)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    run_tests(args.csv_file, args.parallel)


if __name__ == "__main__":
    main()