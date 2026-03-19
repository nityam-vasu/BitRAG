---
status: resolved
updated: 2026-03-18T00:00:00Z
---

## Current Focus

hypothesis: "Embedding model is loaded ON EVERY QUERY, causing memory accumulation until CUDA OOM"
test: "Check metrics.py query loop and QueryEngine initialization"
expecting: "Find code that loads embedding model per-query instead of once"
next_action: "Read metrics.py and query.py to find the model loading pattern"

## Symptoms

expected: "100 queries should complete without running out of GPU memory"
actual: "CUDA out of memory at query 19/100. GPU has 3.68 GiB, process used 2.85 GiB, only 16.81 MiB free when failed"
errors: "torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB. GPU 0 has a total capacity of 3.68 GiB of which 16.81 MiB is free."
reproduction: "Run metrics.py with -v flag on Unknown.pdf with 100 queries"
started: "First time running this benchmark"

## Evidence

- timestamp: 2026-03-18
  checked: "The log output"
  found: "For EVERY query (1 through 18), the BertModel is loaded fresh: 'Loading weights: 100%|...| 103/103 ... BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2'"
  implication: "Model is being loaded 18+ times, each loading consumes GPU memory. Memory is not being freed between queries."

- timestamp: 2026-03-18
  checked: "Stack trace at failure"
  found: "Traceback shows: query.py line 171 in _init_embedding -> HuggingFaceEmbedding -> SentenceTransformer -> self.to(device)"
  implication: "Failure happens when QueryEngine.__init__ calls _init_embedding()"

- timestamp: 2026-03-18
  checked: "metrics.py line 316"
  found: "run_benchmark calls run_query_vector for each query"
  implication: "Each query creates a new QueryEngine instance"

## Eliminated

## Resolution

root_cause: "metrics.py calls run_query_vector() for EACH query, which creates a new QueryEngine instance per query. QueryEngine.__init__ loads HuggingFaceEmbedding (sentence-transformers/all-MiniLM-L6-v2) fresh every time, consuming GPU memory each time. After 18+ queries, GPU memory is exhausted (2.85 GiB used out of 3.68 GiB). The model is never unloaded between queries."

fix: "Option 1 (Quick): Pass device='cpu' to HuggingFaceEmbedding to avoid GPU for embeddings (embeddings are lightweight, CPU is fine). Option 2 (Proper): Create QueryEngine once outside the query loop in metrics.py and reuse it for all queries."

verification: ""
files_changed: []
