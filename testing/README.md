# BitRAG Testing Suite

A comprehensive testing suite designed for low-resource, CPU-only RAG systems with small models (1B-1.5B parameters).

## What's New (v2.2)

### 🧠 Thinking Mode Support
- **Enable/Disable** - `--thinking` / `--no-thinking` flags
- **Per-Model Control** - Control thinking per model in batch tests
- **Thinking Capture** - Store reasoning process in results

### 📊 CSV Combination Testing
- **test_needle_combinations.csv** - Predefined parameter combinations
- **run_needle_combinations.py** - Run all CSV combinations
- **Analysis Output** - CSV + Markdown report generation
- **Parallel Execution** - `--parallel 4` for faster testing

### 🔗 Embedding Model Support
- **BAAI/bge-small-en-v1.5** - Better Chinese/English quality
- **BAAI/bge-base-en-v1.5** - Higher accuracy
- **Custom Models** - Any sentence-transformers model

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Test Types](#test-types)
4. [Quick Start](#quick-start)
5. [Enhanced Metrics](#enhanced-metrics)
6. [Run Commands](#run-commands)
7. [Needle-in-Haystack Test (20 Files)](#needle-in-haystack-test-20-files)
8. [RAGAS-Lite Test](#ragas-lite-test)
9. [Test Prompts & Expected Answers](#test-prompts--expected-answers)
10. [Interpreting Results](#interpreting-results)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This testing suite validates your RAG system across four key dimensions:

| Test | Purpose | Target Metrics |
|------|---------|----------------|
| **Needle-in-Haystack** | Retrieval accuracy with expanded docs | >80% file retrieval, >85% precision |
| **RAGAS-Lite** | Quality assessment | >0.7 overall score |
| **Faithfulness** | Hallucination detection | <10% hallucination rate |
| **Latency** | Performance benchmarking | 5-10 TPS for 1B models |

### What's New (v2.0)

- **Expanded Documents**: needle_docs now contain ~1000 lines (was ~40 lines)
- **Chunk Size**: 1500 (was 512)
- **Chunk Overlap**: 100 (was 50)
- **New Metrics**: Source citation, hallucination detection, confidence scores

### What's New (v2.1)

- **Thinking Mode Support** - New flags for reasoning models
- **Timeout Control** - Per-model timeout settings
- **Thinking Results** - Store reasoning in JSON output

---

## Directory Structure

```
testing/
├── README.md                          # This file
├── run_all_tests.py                   # Original test runner (CSV-based)
├── test_indexing.py                   # Indexing performance test
├── test_inference.py                  # Inference performance test
├── test_gui.py                        # GUI for running tests
│
├── test_needle_combinations.csv      # CSV parameter combinations
├── run_needle_combinations.py       # Run all CSV combinations
│
├── needle_docs/                       # 20 expanded documents for retrieval test
│   ├── 01_server_password.txt       (~34 lines)
│   ├── 02_ceo_mobile.txt             (~30 lines)
│   ├── ...
│   └── 20_report_id.txt             (~66 lines)
│
├── test_needle_20.py                  # Needle-in-haystack test (20 files)
├── test_needle_haystack.py            # Original needle test (embedded facts)
├── test_faithfulness.py               # Hallucination detection test
├── test_latency_benchmark.py          # Performance benchmark
├── test_ragas_lite.py                 # Quality assessment (expanded doc)
├── test_comprehensive.py              # Run all tests together
│
├── test_comprehensive_params.csv      # Parameter variations
├── test_indexing_params.csv           # Indexing test params
├── test_inference_params.csv          # Inference test params
│
└── comprehensive_results_*/         # Saved test results (auto-generated)
```

## Results Directory

Test results are saved to the `results/` directory at the project root. Use the `--results-dir` or `-r` flag to customize the output location:

```bash
# Default: saves to results/
python test_indexing.py -i test.pdf -o my_results.txt

# Custom directory
python test_indexing.py -i test.pdf -o results.txt -r my_results
python test_needle_20.py -r benchmark_results
python test_ragas_lite.py -r quality_tests
```

**Results Directory Structure:**
```
results/
├── SUMMARY.md              # Test results overview
├── benchmarks/             # Performance benchmarks
│   ├── indexing_results.txt
│   ├── inference_results.txt
│   └── needle_20_results.txt
├── comprehensive/          # Detailed test results
│   ├── ragas_results.txt
│   ├── hallucination_results.txt
│   └── needle_results.txt
└── raw/                    # Raw JSON data
    └── needle_20_all_models_*.json
```

---

## Test Types

### 1. Needle-in-Haystack (Retrieval Accuracy)
Tests if ChromaDB can find specific information from 20 **expanded** documents (~50 lines each).

**Location**: `testing/needle_docs/` (20 txt files)

**What it tests**:
- Embedding model quality with **expanded content**
- Chunk size effectiveness (1500 vs previous 512)
- Top-k retrieval accuracy
- **Context precision** - are retrieved chunks relevant?
- **Source citation** - does answer cite retrieved info?
- **Hallucination** - is answer consistent with sources?

### 2. RAGAS-Lite (Quality Assessment)
Tests quality using an expanded ~200-line corporate document.

**Location**: Built into `test_ragas_lite.py` (SAMPLE_DOCUMENT)

**What it tests**:
- **Faithfulness**: Are claims in answer from sources?
- **Answer Relevance**: Does answer address the question?
- **Context Precision**: Are top-k chunks actually useful?
- **Source Citation**: Does model cite retrieved context?
- **Hallucination**: Does model hallucinate info not in sources?

### 3. Latency & Resource Benchmark
Measures performance on CPU-only systems.

**What it tests**:
- Total query time
- Tokens per second (TPS)
- Memory usage

### 4. Faithfulness & Hallucination
Tests if the model acknowledges when it cannot find an answer.

**What it tests**:
- System prompt effectiveness
- Model honesty when context is insufficient

---

## Quick Start

```bash
cd testing

# Run all tests
python test_comprehensive.py --all

# Run needle-in-haystack test only
python test_needle_20.py

# Run RAGAS-lite test only
python test_ragas_lite.py
```

### With Custom Results Directory

All test scripts support the `--results-dir` / `-r` flag to specify where results are saved:

```bash
# Run indexing test with custom results directory
python test_indexing.py -i ../test_PDF/Test_Story.pdf -o my_indexing.txt -r ../results

# Run inference test
python test_inference.py -m llama3.2:1b -q "Summarize this" -o my_inference.txt -r results

# Run needle test with custom output
python test_needle_20.py -o needle_benchmark.txt -r ../results/benchmarks
```

---

## Enhanced Metrics

### Needle-in-Haystack Test Metrics

| Metric | Description | Threshold |
|--------|-------------|------------|
| **Files Retrieved** | Correct file in top-k | ≥50% |
| **Keywords Matched** | Keywords found in chunks | ≥50% |
| **Answers Correct** | Answer contains expected info | ≥50% |
| **Retrieval Precision** | % of retrieved chunks with keywords | ≥50% |
| **Source Citation** | Answer cites info from sources | ≥50% |
| **Hallucination** | Answer has info NOT in sources | <10% |
| **Avg Confidence** | Mean similarity score | ≥0.7 |

### RAGAS-Lite Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| **Faithfulness** | 40% | Claims from sources? |
| **Relevance** | 40% | Answers question? |
| **Precision** | 20% | Chunks useful? |
| **Source Citation** | - | Cites retrieved context? |
| **Hallucination** | - | HALLUCINATED info? |
| **Confidence** | - | Similarity score |

---

## Run Commands

### Needle-in-Haystack Test

```bash
# Default (chunk_size=1500, overlap=100)
python test_needle_20.py

# Custom configuration
python test_needle_20.py \
  --chunk-size 1500 \
  --chunk-overlap 100 \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --top-k 3 \
  --llm-model llama3.2:1b \
  --output results_needle.txt
```

### RAGAS-Lite Test

```bash
# Default (chunk_size=1500, overlap=100)
python test_ragas_lite.py

# Custom configuration
python test_ragas_lite.py \
  --chunk-size 1500 \
  --chunk-overlap 100 \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --top-k 3 \
  --llm-model llama3.2:1b \
  --output results_ragas.txt
```

### Comprehensive Test

```bash
# Run all tests
python test_comprehensive.py --all

# Run specific tests
python test_comprehensive.py --needle
python test_comprehensive.py --ragas
python test_comprehensive.py --hallucination
python test_comprehensive.py --latency
```

### CSV Test Runner

```bash
# Run indexing parameter tests
python run_csv_tests.py test_indexing_params.csv

# Run inference parameter tests
python run_csv_tests.py test_inference_params.csv
```

---

## Needle-in-Haystack Test (20 Files)

### Document Structure

Each document is now expanded with realistic corporate context (~30-70 lines):

| # | Filename | Key Information | Line Count |
|---|----------|----------------|------------|
| 1 | `01_server_password.txt` | Server room password: **QUANTUM-2026-X7** | 34 |
| 2 | `02_ceo_mobile.txt` | CEO mobile: **+1-555-0127-8944** | 30 |
| 3 | `03_deadline.txt` | Project deadline: **November 15th, 2026 5:00 PM EST** | 41 |
| 4 | `04_hidden_password.txt` | Hidden password: **龙卷风2026** | 39 |
| 5 | `05_usb_label.txt` | USB label: **KEY-SILVER-773** | 40 |
| 6 | `06_budget.txt` | AI budget: **$2,847,500** | 46 |
| 7 | `07_building_code.txt` | Building code: **4921** | 51 |
| 8 | `08_wifi_password.txt` | Guest WiFi: **WelcomeGuest2026!** | 51 |
| 9 | `09_meeting_code.txt` | Meeting code: **MTG-ROOM-ALPHA-77** | 52 |
| 10 | `10_api_endpoint.txt` | API URL: **api.company.com/v2/prod** | 61 |
| 11 | `11_db_password.txt` | Database password: **PostgresSecure#2026!** | 70 |
| 12 | `12_license_code.txt` | License code: **ACTIV-8F3D-2026-X** | 66 |
| 13 | `13_emergency_contact.txt` | Emergency: **+1-555-0199-SUPPORT** | 61 |
| 14 | `14_vault_combo.txt` | Vault combo: **34-7-19-42** | 55 |
| 15 | `15_satellite_phone.txt` | Satellite: **+1-555-8823-MARS** | 68 |
| 16 | `16_launch_date.txt` | Launch date: **June 1st, 2026** | 53 |
| 17 | `17_bonus_q1.txt` | Q1 bonus: **15%** (April 15th) | 49 |
| 18 | `18_ssh_key.txt` | SSH fingerprint: **SHA256:A1B2C3D4E5F6G7H8I9J0** | 60 |
| 19 | `19_vpn_code.txt` | VPN code: **VPN-SPLIT-TUNNEL-442** | 62 |
| 20 | `20_report_id.txt` | Report ID: **RPT-2026-ALPHA-OMEGA-X** | 66 |

---

## RAGAS-Lite Test

### Sample Document (SAMPLE_DOCUMENT)

The RAGAS test uses an expanded ~200-line corporate document covering:
- Executive summary
- Key features (6 features with detailed descriptions)
- Technical stack (frontend, backend, database, cloud)
- Team members and responsibilities
- Timeline and milestones
- Budget allocation and expenditure
- Risks and mitigation strategies
- Success metrics and KPIs

### Test Questions

| # | Question | Category |
|---|----------|----------|
| 1 | What is the project name? | entity_extraction |
| 2 | What programming languages are used? | list_extraction |
| 3 | Who are the team members? | list_extraction |
| 4 | What is the budget information? | fact_extraction |
| 5 | When was the project launched? | date_extraction |
| 6 | What are the success metrics? | list_extraction |
| 7 | What are the identified risks? | list_extraction |
| 8 | What cloud provider is used? | entity_extraction |

---

## Test Prompts & Expected Answers

### Query Examples (Needle Test)

| # | Prompt | Expected Answer |
|---|-------|----------------|
| 1 | "What is the server room password?" | QUANTUM-2026-X7 |
| 2 | "What is the CEO's personal mobile number?" | +1-555-0127-8944 |
| 3 | "When is the project deadline?" | November 15th, 2026 at 5:00 PM EST |
| 4 | "What is the hidden password for backup system?" | 龙卷风2026 (tornado2026) |
| 5 | "What is the label on the USB drive with encryption key?" | KEY-SILVER-773 |
| 6 | "What is the annual AI research budget?" | $2,847,500 |
| 7 | "What is the security code for the main building?" | 4921 |
| 8 | "What is the guest WiFi password?" | WelcomeGuest2026! |
| 9 | "What is the booking code for client meeting room?" | MTG-ROOM-ALPHA-77 |
| 10 | "What is the production API endpoint URL?" | https://api.company.com/v2/prod |

---

## Interpreting Results

### Needle Test Results

```
ENHANCED METRICS SUMMARY
============================================================
Total Tests: 20
Files Retrieved: 18 (90.0%)
Keywords Matched: 19 (95.0%)
Answers Correct: 17 (85.0%)
Retrieval Precision: 85.0%
Source Citations Verified: 80.0%
Hallucination Rate: 5.0%
Avg Confidence Score: 0.823
```

| Score | Rating | Action |
|-------|--------|--------|
| >90% | Excellent | System is highly accurate |
| 80-90% | Good | Minor tuning needed |
| 60-80% | Fair | Check embedding model, chunk size |
| <60% | Poor | Major issues - review configuration |

### RAGAS-Lite Results

```
SCORES
============================================================
faithfulness: 0.875
relevance: 0.913
precision: 0.950
source_citations_verified: 0.875
hallucination_rate: 0.125
avg_confidence: 0.834
overall: 0.912
```

| Score | Rating |
|-------|--------|
| >0.8 | Excellent |
| 0.7-0.8 | Good |
| 0.5-0.7 | Fair |
| <0.5 | Poor |

### Latency Results

```
Average Total Time: 3.5s
Average TPS: 8.2
Peak Memory: 450 MB
```

| TPS (1B model) | Rating | Notes |
|----------------|--------|-------|
| >15 | Excellent | Fast for CPU |
| 8-15 | Good | Acceptable |
| 5-8 | Fair | Consider reducing top-k |
| <5 | Poor | May need optimization |

---

## Troubleshooting

### Issue: Low Retrieval Accuracy

**Symptoms**: Files retrieved < 60%

**Solutions**:
1. Try a different embedding model (BAAI/bge-small-en-v1.5)
2. Increase chunk size (2000 instead of 1500)
3. Increase top-k (4 or 5)
4. Check if documents are being indexed correctly

### Issue: High Hallucination Rate

**Symptoms**: Hallucination > 20%

**Solutions**:
1. Update system prompt to explicitly say "Use only information from context"
2. Increase retrieval precision by adjusting chunk_size
3. Reduce top-k to provide less context
4. Enable source citation verification

### Issue: Low Source Citation

**Symptoms**: Source citation < 50%

**Solutions**:
1. Verify chunk_size captures full relevant context
2. Check embedding model captures semantic meaning
3. Review if keywords are being properly matched

### Issue: Slow Performance

**Symptoms**: TPS < 5, total time > 10s

**Solutions**:
1. Reduce top-k (2 instead of 3)
2. Use smaller chunk sizes
3. Use smaller embedding model (MiniLM instead of mpnet)
4. Consider using quantized LLM

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'bitrag'`

**Solutions**:
```bash
# Ensure you're running from project root
cd /path/to/BitRAG

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## Common Commands Reference

```bash
# Index a single document
python -c "from src.bitrag.core.indexer import DocumentIndexer; i = DocumentIndexer('test'); i.index_document('path/to/file.pdf')"

# Query the database
python -c "from src.bitrag.core.query import QueryEngine; q = QueryEngine('test', 'llama3.2:1b'); print(q.query('your question'))"

# Test with different embeddings
python testing/test_needle_20.py --model BAAI/bge-small-en-v1.5

# Run multiple parameter variations
python testing/test_comprehensive.py --all --llm-model llama3.2:1b
```

---

## Running Tests with All Models

### Using run_all_models.py

Run comprehensive tests across all available Ollama models:

```bash
# Run with all models (default: llama3.2:1b, qwen3:0.6b, qwen3:1.7b, tinyllama, gemma3, granite3.1, falcon3)
cd testing
python run_all_models.py

# Run specific models only
python run_all_models.py --models llama3.2:1b,qwen3:0.6b

# Run specific tests
python run_all_models.py --needle
python run_all_models.py --ragas
python run_all_models.py --latency
python run_all_models.py --faith

# Custom chunk settings
python run_all_models.py --chunk-size 1500 --chunk-overlap 100

# Custom output directory
python run_all_models.py --output results/custom

# Include/exclude models
python run_all_models.py --include llama3,qwen3
python run_all_models.py --exclude tinyllama

# Thinking mode (for qwen3, deepseek-r1 models)
python run_all_models.py --thinking              # Enable thinking
python run_all_models.py --no-thinking           # Disable thinking (faster)

# Set timeout per model (default: 300s)
python run_all_models.py --timeout 180
```

### CSV Combination Testing

Run all parameter combinations from CSV file:

```bash
# Run all combinations from CSV
python run_needle_combinations.py --input test_needle_combinations.csv

# Parallel execution
python run_needle_combinations.py --input test_needle_combinations.csv --parallel 4

# Generate CSV analysis output
python run_needle_combinations.py --csv

# Generate Markdown report
python run_needle_combinations.py --report
```

**CSV Format:**
```csv
combo_id,chunk_size,chunk_overlap,embedding_model,top_k,llm_model
1,1500,100,sentence-transformers/all-MiniLM-L6-v2,3,qwen3.5:0.8b
2,1500,100,BAAI/bge-small-en-v1.5,3,qwen3.5:0.8b
3,1500,100,BAAI/bge-base-en-v1.5,3,qwen3.5:0.8b
```

**Available Embedding Models:**
| Model | Dimensions | Notes |
|-------|------------|-------|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Default, fast |
| `BAAI/bge-small-en-v1.5` | 384 | Best quality/speed |
| `BAAI/bge-base-en-v1.5` | 768 | Higher accuracy |
| `BAAI/bge-large-en-v1.5` | 1024 | Best, slower |

**Output Files:**
- `analysis.csv` - All metrics in CSV format
- `report.md` - Markdown analysis report
- `results_*.json` - Individual test results

### Using CSV Parameter Files

```bash
# Run indexing parameter tests
python run_csv_tests.py test_indexing_params.csv

# Run inference parameter tests
python run_csv_tests.py test_inference_params.csv
```

### Test Outputs

Results are saved to:
- `results/all_models_results.json` - Full results in JSON
- `results/all_models_summary.txt` - Human-readable summary

### CSV Test Customization

Edit the CSV files to add your own parameter combinations:

**test_indexing_params.csv format:**
```csv
test_type,output_file,input_file,chunk_size,chunk_overlap,embedding_model
indexing,my_results.txt,needle_docs,1500,100,sentence-transformers/all-MiniLM-L6-v2
```

**test_inference_params.csv format:**
```csv
test_type,output_file,model,query,system_prompt,top_k,temperature,top_p,embedding_model,chunk_size,chunk_overlap
inference,my_results.txt,llama3.2:1b,What is the server password?,You are helpful.,3,0.1,0.9,sentence-transformers/all-MiniLM-L6-v2,1500,100
```

---

## Performance Tips for CPU-Only

1. **Reduce top-k**: Use 2 instead of 3 for 30% faster inference
2. **Smaller chunks**: 1024 chars instead of 1500 means less context to process
3. **Smaller embedding**: MiniLM (384dim) is faster than mpnet (768dim)
4. **Quantized models**: Use 1B models like llama3.2:1b or qwen2.5:1.5b
5. **Batch requests**: If possible, batch queries to warm up the model once

---

## Contact

For issues or questions about this testing suite, check the main BitRAG documentation or open an issue on GitHub.