# Phase 2: Graph Module Reimagined - Research

**Researched:** 2026-04-02
**Domain:** Graph visualization + LLM-powered document processing
**Confidence:** HIGH

## Summary

Phase 2 transforms the graph module from simple keyword frequency extraction to AI-powered document relationship visualization. The key changes involve:

1. **Summary Generation** - Use small LLM models to generate meaningful document summaries
2. **Tag Extraction** - Use LLM to extract 5-10 semantic tags per document
3. **Enhanced Graph** - Use tags for node linking with weighted edges and dynamic sizing
4. **Fix Visualization** - Debug and enhance the force-graph implementation

**Primary recommendation:** Create modular Python classes for summary and tag generation, then integrate into the graph endpoint. Keep existing keyword extraction as fallback.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| force-graph | 1.51.2 | Graph visualization | Most popular, 296K weekly downloads |
| react-force-graph | Latest | React bindings | Official bindings for force-graph |
| LlamaIndex | Latest | LLM integration | Already in use |
| Ollama | Latest | Local LLM | Already in use |

### Recommended Models for Summary/Tag
| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| llama3.2:1b | ~1.3GB | Very Fast | Quick summaries, single docs |
| qwen2.5:3b | ~2GB | Fast | Better quality, multilingual |
| phi3:3.8b | ~2.2GB | Medium | Good reasoning |

## Architecture Patterns

### Pattern 1: Summary Generator Service
**What:** Dedicated class for LLM-based summary generation
**When to use:** When document summarization needed
**Example:**
```python
class SummaryGenerator:
    def __init__(self, model: str, ollama_base_url: str):
        self.llm = Ollama(model=model, base_url=ollama_base_url)
    
    def generate(self, text: str, max_length: int = 200) -> str:
        prompt = f"""Provide a brief 2-3 sentence summary of this document.
Do not exceed {max_length} characters.

Document:
{text[:3000]}

Summary:"""
        # Use streaming to get response
```

### Pattern 2: Tag Extractor Service
**What:** LLM-based tag extraction with guaranteed count
**When to use:** When semantic tagging needed
**Example:**
```python
class TagExtractor:
    def __init__(self, model: str, ollama_base_url: str):
        self.llm = Ollama(model=model, base_url=ollama_base_url)
    
    def extract_tags(self, text: str, min_tags: int = 5, max_tags: int = 10) -> List[str]:
        prompt = f"""Extract {min_tags}-{max_tags} relevant tags from this document.
Tags should be: topics, entities, concepts, or key themes.
Return ONLY a JSON array of strings, nothing else.

Document:
{text[:3000]}

Tags (JSON array):"""
        # Parse JSON response
```

### Pattern 3: Graph Builder with Caching
**What:** Build graph data with cached summaries/tags
**When to use:** Expensive LLM operations
**Example:**
```python
class GraphBuilder:
    def __init__(self, summary_gen: SummaryGenerator, tag_extractor: TagExtractor):
        self.summary_gen = summary_gen
        self.tag_extractor = tag_extractor
        self.cache = {}
    
    def get_document_metadata(self, doc_id: str, text: str) -> Dict:
        if doc_id not in self.cache:
            self.cache[doc_id] = {
                "summary": self.summary_gen.generate(text),
                "tags": self.tag_extractor.extract_tags(text),
            }
        return self.cache[doc_id]
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Graph rendering | Custom canvas drawing | force-graph | Handles physics, zoom, pan |
| LLM calls | Raw requests | LlamaIndex Ollama | Handles streaming, timeouts |
| Tag parsing | String splitting | JSON parsing | More reliable |

**Key insight:** The existing web_app.py graph endpoint needs refactoring into separate modules, not rewriting from scratch.

## Common Pitfalls

### Pitfall 1: LLM Timeout on Large Documents
**What goes wrong:** Summary/tag generation times out on long PDFs
**Why it happens:** Single LLM call for entire document
**How to avoid:** Truncate to first 3000-5000 characters, use chunked processing
**Warning signs:** Requests hang for >30 seconds

### Pitfall 2: Tag Quality Varies by Model
**What goes wrong:** Some models return inconsistent JSON
**Why it happens:** Not all models follow instructions well
**How to avoid:** Validate response, fallback to keyword extraction if parsing fails
**Warning signs:** JSON parsing errors in logs

### Pitfall 3: Force-Graph Memory with Many Nodes
**What goes wrong:** Browser becomes slow with 100+ nodes
**Why it happens:** Force simulation is O(n²)
**How to avoid:** Limit visible nodes, add clustering, use 3D version
**Warning signs:** Browser lag, high CPU usage

### Pitfall 4: Node ID Mismatch
**What goes wrong:** Graph links don't connect to nodes
**Why it happens:** ChromaDB IDs used as node IDs but links use different format
**How to avoid:** Consistent ID mapping, validate graph data before return
**Warning signs:** "Node not found" in console, missing edges

## Code Examples

### force-graph Basic Usage (vanilla JS)
```javascript
// Source: https://github.com/vasturiano/force-graph
const Graph = ForceGraph()(document.getElementById('graph'))
  .nodeId('id')
  .nodeLabel('name')
  .nodeVal('val')  // Node size
  .nodeColor('group')
  .linkSource('source')
  .linkTarget('target')
  .linkValue('value')  // Edge thickness
  .linkLabel('label')
  .graphData(data);

// Configuration for better performance
Graph
  .d3AlphaDecay(0.02)
  .d3VelocityDecay(0.3)
  .cooldownTime(3000);
```

### force-graph Dynamic Node Sizing
```javascript
// Size nodes based on connections
const nodeMap = {};
data.links.forEach(link => {
  nodeMap[link.source] = (nodeMap[link.source] || 0) + 1;
  nodeMap[link.target] = (nodeMap[link.target] || 0) + 1;
});

data.nodes.forEach(node => {
  node.val = nodeMap[node.id] || 1;  // 1 = minimum size
});
```

### Ollama Summary Prompt Template
```
You are a document summarization assistant. Provide a brief 2-3 sentence summary 
that captures the main topic and key points of the document.

Document:
{DOCUMENT_TEXT}

Requirements:
- Maximum 200 characters
- Focus on main topic
- No preamble, just the summary

Summary:
```

### Ollama Tag Extraction Prompt Template
```
Extract 5-10 relevant tags from the following document. Tags should be:
- Topics and subjects
- Named entities (people, places, organizations)
- Key concepts or technologies
- Themes or categories

Return ONLY a valid JSON array of tag strings, nothing else.
Example: ["topic1", "topic2", "entity1"]

Document:
{DOCUMENT_TEXT}

Tags:
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Word frequency keywords | LLM-based tags | Phase 2 | Better semantic relationships |
| Static node size | Connection-based sizing | Phase 2 | Visual importance indication |
| First 200 chars summary | LLM summary | Phase 2 | Meaningful summaries |
| Basic force-graph | Enhanced with controls | Phase 2 | Better UX |

**Deprecated/outdated:**
- Simple keyword extraction (replaced by LLM tags)

## Open Questions

1. **Should summaries/tags be stored or regenerated?**
   - What we know: ChromaDB stores metadata, indexer has document access
   - What's unclear: Performance vs accuracy tradeoff
   - Recommendation: Cache in ChromaDB metadata, regenerate on explicit request

2. **What model should be used by default?**
   - What we know: llama3.2:1b is fast, qwen2.5:3b has better quality
   - What's unclear: User hardware constraints
   - Recommendation: Default to llama3.2:1b, allow selection (Phase 3)

3. **How to handle the broken graph visualization?**
   - What we know: force-graph is used, data structure looks correct
   - What's unclear: Why visualization fails
   - Recommendation: Test with minimal data first, check browser console

## Sources

### Primary (HIGH confidence)
- [force-graph GitHub](https://github.com/vasturiano/force-graph) - Complete API documentation
- [react-force-graph npm](https://www.npmjs.com/package/react-force-graph) - React integration
- [LlamaIndex Ollama](https://docs.llamaindex.ai/en/stable/examples/llm/ollama/) - LLM integration

### Secondary (MEDIUM confidence)
- [Ollama Summarizer Blog](https://www.daltonbly.com/llm-based-content-summarization-and-keyword-tagging-using-ollama-and-localai/) - Example implementation
- [Ollama phi3 summarizer](https://dev.to/vikas2426/ollama-phi3-based-text-summarizer-18i4) - Prompt patterns

### Tertiary (LOW confidence)
- WebSearch results - Need official doc verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Well-documented libraries
- Architecture: HIGH - Based on existing codebase patterns
- Pitfalls: MEDIUM - Based on common issues, need validation

**Research date:** 2026-04-02
**Valid until:** 30 days (stable domain)
