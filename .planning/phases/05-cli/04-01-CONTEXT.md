# Phase 05: CLI Enhancement - Context

## Phase Overview
Build opencode-style CLI and proceed with Ollama for smaller LLMs (no high GPU required).

## Current Focus
- **LLM Runtime**: Ollama (works now, no high GPU needed)
- **Smaller Models Available**:
  - llama3.2:1b (~1GB, minimal GPU)
  - qwen2.5:0.5b (very small)
  - phi3:3.8b (Microsoft)
  - gemma3:4b (currently using)

## Future Options (Open)
- **BitNet.cpp**: True 1-bit LLM (when Docker setup works)
- Keep options open for future integration

## Key Information
- Ollama is running and working
- Query pipeline is functional with gemma3:4b
- CLI needs enhancement to opencode-style

## Decisions
1. Use Ollama as primary LLM (works now)
2. Keep BitNet.cpp as future option
3. Enhance CLI to opencode-style
4. Keep LlamaIndex for indexing (not changing)
5. Keep ChromaDB for vector storage (not changing)

## Out of Scope
- Django frontend (deferred)
- BitNet.cpp for now (future option)
