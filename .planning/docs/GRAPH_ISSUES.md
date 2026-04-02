# BitRAG Graph Issues Documentation

**Document:** GRAPH_ISSUES.md
**Version:** 1.0
**Date:** 2026-04-02

---

## Executive Summary

The graph visualization is reported as "broken". This document investigates the issue and identifies potential causes.

**Status:** Investigation in progress
**Severity:** MEDIUM (visualization issue, core functionality works)

---

## Issue Description

**Reported Issue:** Graph visualization is broken
**Expected Behavior:** Documents displayed as interactive force-directed graph
**Actual Behavior:** Unknown (needs live testing)

---

## Investigation

### 1. Backend API Analysis

The `/api/graph` endpoint (web_app.py lines 784-988) appears functional:

**Data Structure Returned:**
```json
{
  "nodes": [
    {
      "id": "node_id",
      "name": "filename.pdf",
      "val": 3,
      "group": 1,
      "keywords": ["kw1", "kw2"],
      "summary": "Document summary..."
    }
  ],
  "links": [
    {
      "source": "node_id_1",
      "target": "node_id_2",
      "value": 2,
      "label": "shared, keywords"
    }
  ]
}
```

**Code Path:**
1. `ensure_initialized()` - Check initialization
2. `indexer.list_documents()` - Get all documents
3. For each document:
   - `indexer.get_document(filename)` - Get content
   - Extract keywords (word frequency)
   - Generate summary (LLM or truncate)
4. Create nodes array
5. Create links based on shared keywords
6. Return JSON

**Findings:**
- ✅ Endpoint exists and returns valid JSON
- ✅ Node structure looks correct
- ✅ Link structure looks correct
- ⚠️ `val` (node size) is hardcoded to 3

---

### 2. Frontend Analysis

**Frontend Files:**
```
frontend/
├── index.html
└── assets/
    ├── index-C7WuB4gw.js    # Bundled React app
    └── index-GYeDh-gI.css
```

**Note:** Frontend SOURCE CODE not available - only bundled assets.

**Likely Library:** force-graph (based on CSS comments found)

**Potential Issues:**

1. **Missing Node IDs**
   - Nodes use `doc.node_id` from ChromaDB
   - Links use document IDs
   - Mismatch could cause missing edges

2. **Invalid Data Types**
   - `val` should be number
   - `group` should be number
   - Validation might fail silently

3. **Empty Graph**
   - No documents = empty nodes array
   - Graph renders but shows nothing

4. **Library Compatibility**
   - force-graph version mismatch
   - API changes between versions

---

### 3. Common Force-Graph Issues

Based on force-graph documentation:

| Issue | Symptom | Cause |
|-------|---------|-------|
| Empty graph | No nodes visible | Data not loaded or empty |
| No edges | Nodes visible but no links | ID mismatch between source/target |
| Crash on load | Console errors | Invalid data format |
| Performance | Slow rendering | Too many nodes (>1000) |
| Static positions | Nodes don't move | D3 simulation not started |

---

## Root Cause Hypotheses

### Hypothesis 1: Frontend Source Missing (HIGH PROBABILITY)

**Theory:** Frontend source code is missing, preventing proper debugging/fixing.

**Evidence:**
- `frontend/src/` directory does not exist
- Only bundled JS/CSS in `frontend/assets/`
- Cannot modify frontend without source

**Fix Required:**
1. Recover frontend source from git history, OR
2. Set up new frontend project, OR
3. Modify bundled assets directly (not recommended)

---

### Hypothesis 2: Data ID Mismatch (MEDIUM PROBABILITY)

**Theory:** Node IDs and Link source/target IDs don't match.

**Current Code:**
```python
# Node creation (web_app.py:937)
nodes.append({
    "id": doc.get("id", ""),  # From indexer.list_documents()
    ...
})

# Link creation (web_app.py:970)
link_map[link_key] = {
    "source": doc1_id,  # From docs loop
    "target": doc2_id,   # From docs loop
    ...
}
```

**Issue:** `indexer.list_documents()` returns:
```python
{
    "id": doc.get("id", ""),  # This is chunk/node ID
    "file_name": "doc.pdf"
}
```

But the loop iterates over docs, not using the returned IDs consistently.

**Fix Required:** Ensure consistent ID usage throughout.

---

### Hypothesis 3: Empty Data (LOW PROBABILITY)

**Theory:** No documents uploaded, so graph is empty.

**Fix Required:** Upload test documents and verify.

---

### Hypothesis 4: Library/API Changes (MEDIUM PROBABILITY)

**Theory:** force-graph API changed, bundled JS uses old API.

**Evidence:**
- force-graph v1.51.2 (current)
- Bundled JS may be older version

**Fix Required:** Update bundled assets or force-graph usage.

---

## Recommendations

### Immediate Actions

1. **Test Backend API**
   ```bash
   curl http://localhost:5000/api/graph | python -m json.tool
   ```

2. **Verify Documents Exist**
   ```bash
   curl http://localhost:5000/api/documents | python -m json.tool
   ```

3. **Check Browser Console**
   - Open browser DevTools
   - Check for JavaScript errors
   - Check network tab for failed requests

### Long-term Fixes (Phase 2)

1. **Recover/Recreate Frontend**
   - Check git history for frontend source
   - If not found, create new React project
   - Integrate with existing API

2. **Fix Graph Endpoint**
   - Ensure consistent ID usage
   - Add dynamic node sizing
   - Improve keyword extraction (LLM-based tags)

3. **Enhance Visualization**
   - Add node click handlers
   - Add zoom/pan controls
   - Add tag filtering
   - Add search functionality

---

## Testing Protocol

### Step 1: Verify Backend
```bash
# 1. Check if server is running
curl http://localhost:5000/api/status

# 2. List documents
curl http://localhost:5000/api/documents

# 3. Get graph data
curl http://localhost:5000/api/graph | python -m json.tool
```

**Expected:** Valid JSON with nodes/links arrays

### Step 2: Verify Data Structure
```javascript
// In browser console
fetch('/api/graph')
  .then(r => r.json())
  .then(data => {
    console.log('Nodes:', data.nodes.length);
    console.log('Links:', data.links.length);
    console.log('Sample node:', data.nodes[0]);
  });
```

**Expected:**
- nodes > 0 (if documents exist)
- Links with valid source/target IDs
- Node IDs match link source/target

### Step 3: Check Force-Graph Config
Inspect bundled JS for force-graph initialization:

```javascript
// Expected pattern
const Graph = ForceGraph()
  .nodeId('id')
  .nodeLabel('name')
  .nodeVal('val')
  .nodeColor('group')
  .linkSource('source')
  .linkTarget('target')
  .graphData(data);
```

---

## Code Review Findings

### web_app.py: Graph Endpoint Issues

**Issue 1: Inconsistent ID Source (Line 937)**
```python
# Line 937 - uses doc.get("id", "")
nodes.append({
    "id": doc.get("id", ""),
    ...
})

# But doc comes from indexer.list_documents()
# which returns {"id": ..., "file_name": ...}
```

**Issue 2: Hardcoded Node Size (Line 945)**
```python
"val": 3,  # Always 3, should be dynamic
```

**Issue 3: Keyword-Based Only (Lines 867-925)**
```python
# Uses word frequency, not semantic understanding
# No LLM-based tag extraction
```

---

## Conclusion

**Most Likely Cause:** Frontend source missing prevents proper debugging and fixing

**Recommended Approach:**
1. **Phase 1 (Now):** Document findings, verify backend works
2. **Phase 2:** Recreate or recover frontend, fix graph endpoint
3. **Phase 2:** Add LLM-based summary and tag generation
4. **Phase 2:** Enhance graph with dynamic sizing and interactions

**Priority for Phase 2:**
1. Recover/create frontend source
2. Fix graph endpoint data consistency
3. Add dynamic node sizing
4. Add tag-based linking (LLM extraction)
5. Add interactive features (zoom, pan, click, filter)

---

## Appendix: Force-Graph Basic Setup

```javascript
// Minimal force-graph setup
import ForceGraph from 'force-graph';

const graphContainer = document.getElementById('graph');
const graph = ForceGraph()(graphContainer)
  .graphData({nodes: [], links: []})
  .nodeId('id')
  .nodeLabel('name')
  .nodeVal('val')
  .nodeColor(d => d.group)
  .linkSource('source')
  .linkTarget('target')
  .linkValue('value')
  .linkLabel('label')
  .onNodeClick(node => {
    // Handle node click
    console.log('Clicked:', node);
  });

// Load data
fetch('/api/graph')
  .then(r => r.json())
  .then(data => graph.graphData(data));
```
