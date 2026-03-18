---
status: fixing
updated: 2026-03-18T16:30:00Z
trigger: "hybrid mode returns 'No results found' for all queries"
---

## Current Focus

hypothesis: "Collection name mismatch between DocumentIndexer and HybridSearch"
test: "Compare collection_name generation in both files"
expecting: "Find different naming patterns"
next_action: "Fix hybrid_search.py to use same collection naming as indexer.py"

## Symptoms

expected: "Hybrid search should return documents from indexed PDF"
actual: "All queries return 'No results found' - zero documents retrieved"
errors: "N/A - silent failure, empty results"
reproduction: "Run metrics.py with --method hybrid"
started: "This is the first hybrid mode run"

## Evidence

- timestamp: 2026-03-18
  checked: "metrics.py CSV output"
  found: "All 100 queries show 'answer_returned: No results found', with 0 input/output tokens"
  implication: "Hybrid search returns empty results, not inference failure"

- timestamp: 2026-03-18
  checked: "ChromaDB sessions/metrics_session/chroma_db/"
  found: "Data exists: chroma.sqlite3, data_level0.bin - documents ARE indexed"
  implication: "Documents exist, but hybrid_search can't find them"

- timestamp: 2026-03-18
  checked: "collection_name generation in indexer.py vs hybrid_search.py"
  found: "indexer.py: bitrag_documents_{session_id}, hybrid_search.py: bitrag_{session_id}"
  implication: "MISMATCH - they're looking in different collections!"

## Eliminated

## Resolution

root_cause: "HybridSearch uses 'bitrag_{session_id}' as collection name, but DocumentIndexer uses '{config.collection_name}_{session_id}' = 'bitrag_documents_{session_id}'. The documents are indexed in the wrong collection from HybridSearch's perspective."

fix: "Updated hybrid_search.py line 77 from 'bitrag_{self.session_id}' to 'bitrag_documents_{self.session_id}' to match indexer.py"

verification: "Verified with direct test - hybrid search now returns 3 results instead of 0. Query 'What is the name of the village where Dr. Aisha Sharma returns?' returned relevant documents about Kodalipur Station."
files_changed: ["src/bitrag/core/hybrid_search.py"]
