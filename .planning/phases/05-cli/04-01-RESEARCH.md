# Phase 05: CLI Enhancement - RESEARCH.md

## Summary

This phase focuses on enhancing the CLI to opencode-style while using Ollama with smaller LLMs that don't require high GPU.

**Current recommendation:** Use Ollama with smaller models (llama3.2:1b, qwen2.5:0.5b, phi3:3.8b)

---

## Ollama with Smaller LLMs

### Why Ollama?
- Works now, no setup issues
- Smaller models run on CPU/minimal GPU
- Easy model switching
- Good for development/testing

### Recommended Smaller Models

| Model | Size | GPU Required | Notes |
|-------|------|--------------|-------|
| llama3.2:1b | ~1GB | Minimal | Best overall |
| qwen2.5:0.5b | ~350MB | Very minimal | Chinese support |
| phi3:3.8b | ~2.5GB | 4GB+ | Microsoft |
| gemma3:4b | ~4GB | 6GB+ | Currently using |

### Install New Models
```bash
ollama pull llama3.2:1b
ollama pull qwen2.5:0.5b
ollama pull phi3:3.8b
```

### List Available Models
```bash
ollama list
```

---

## CLI Style: opencode-like

### opencode CLI Features
- Slash commands: `/command`
- Interactive prompts
- Subcommand groups
- Rich output with colors

### Recommended Structure
```
bitrag/
├── /upload <file>     # Upload and index PDF
├── /query <text>      # Query documents  
├── /chat              # Interactive chat mode
├── /model             # Model management
│   ├── /model list   # List available models
│   ├── /model use <name>  # Switch model
│   └── /model status # Current model
├── /session           # Session management
│   ├── /session list
│   └── /session new
└── /help             # Show help
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| LLM runtime | Custom server | Ollama |
| CLI framework | argparse from scratch | Click |
| PDF parsing | Custom parser | pypdf + LlamaIndex |

---

## Future Options

### BitNet.cpp (Future)
- True 1-bit LLM
- Requires Docker setup (pending)
- Provides 1.37x-6.17x speedup
- 55%-82% energy reduction

---

## Sources

- https://ollama.ai - Ollama website
- https://github.com/microsoft/BitNet - BitNet (future option)
