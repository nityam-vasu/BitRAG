# BitRAG Testing Results Summary

## Overview

This directory contains comprehensive test results and benchmarks for the BitRAG system.

---

## 📊 Test Results Summary

### 1. RAGAS-Lite Quality Assessment

| Metric | Score | Description |
|--------|-------|-------------|
| **Faithfulness** | 0.988 | Are claims in answer from sources? |
| **Relevance** | 0.562 | Does answer address the question? |
| **Precision** | 0.875 | Are top-k chunks actually useful? |
| **Source Citations** | 0.750 | Does answer cite info from sources? |
| **Hallucination Rate** | 0.000 | Answer mentions info NOT in sources? |
| **Overall Score** | **0.795** | Composite score |

**Configuration:**
- Chunk Size: 512
- Chunk Overlap: 50
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
- Top-K: 3
- LLM Model: llama3.2:1b

---

### 2. Faithfulness & Hallucination Test

| Metric | Value |
|--------|-------|
| Total Tests | 10 |
| Appropriate Responses | 8 |
| Hallucination Responses | 2 |
| **Pass Rate** | **80.0%** |

---

### 3. Needle-in-Haystack (20 Files)

| Metric | Score |
|--------|-------|
| Files Retrieved | 19/20 (95.0%) |
| Keywords Matched | 19/20 (95.0%) |
| Answers Correct | 20/20 (100.0%) |
| Retrieval Precision | 95.0% |
| Avg Confidence Score | 0.601 |

**Configuration:**
- Chunk Size: 1500
- Chunk Overlap: 100
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2
- Top-K: 3
- LLM Model: gemma3n:e2b

---

### 4. Indexing Performance

| Metric | Value |
|--------|-------|
| Total Indexing Time | 5.07 seconds |
| Embedding Generation | 0.37 seconds |
| Vector Storage | 0.00 seconds |
| Memory Used | 0.00 MB |

---

### 5. Inference Performance

| Metric | Value |
|--------|-------|
| LLM Model | granite3.1-moe:1b |
| Temperature | 0.1 |
| Top-P | 0.9 |
| Context Size | 2048 |

---

## 📁 Directory Structure

```
results/
├── SUMMARY.md              # This file
├── test_output.txt         # Basic test output
├── comprehensive/         # Detailed comprehensive test results
│   ├── ragas_results.txt
│   ├── hallucination_results.txt
│   └── needle_results.txt
├── benchmarks/            # Performance benchmarks
│   ├── needle_20_results.txt
│   ├── indexing_results.txt
│   └── inference_results.txt
└── raw/                  # Raw JSON data
    └── needle_20_all_models_20260412_221705.json
```

---

## 🔧 Usage

Results are automatically saved to this directory when running tests. To modify the output directory, update the `RESULTS_DIR` variable in the testing scripts.

---

## 📅 Test Dates

- Comprehensive Tests: 2026-04-12
- Needle-20 Tests: 2026-04-12
- Indexing Tests: 2026-04-06
- Inference Tests: 2026-04-06