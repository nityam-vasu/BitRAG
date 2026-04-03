# BitRAG Configuration Guide

This document explains all configuration options in `config.json`.

## Model Configuration

### `default_model`
- **Description**: Default AI model for chat queries
- **Default**: `"llama3.2:1b"`
- **Available Models**: falcon3:1b, tinyllama:1.1b, gemma3:1b, gemma3n:e2b, deepseek-r1:1.5b, qwen3:1.7b, granite3.1-moe:1b, llama3.2:1b, qwen3:0.6b
- **Usage**: The main LLM used when you ask questions in the chat

### `summary_model`
- **Description**: Model used for generating document summaries
- **Default**: `"llama3.2:1b"`
- **Usage**: When viewing documents in the Knowledge Graph, each document gets an AI-generated summary

### `tag_model`
- **Description**: Model used for extracting tags from documents
- **Default**: `"llama3.2:1b"`
- **Usage**: Tags help organize and connect related documents in the Knowledge Graph

---

## Ollama Configuration

### `ollama_port`
- **Description**: Port where Ollama server is running
- **Default**: `"11434"`
- **Usage**: Connects to local Ollama instance for AI model inference

### `ollama_base_url`
- **Description**: Full base URL for Ollama API
- **Default**: `"http://localhost:11434"`
- **Usage**: Alternative URL if Ollama is on a different host

---

## Embedding Model Configuration

### `embedding_model`
- **Description**: Model used to convert text into vector embeddings for search
- **Default**: `"BAAI/bge-small-en-v1.5"`
- **Options**: BAAI/bge-small-en-v1.5, BAAI/bge-base-en-v1.5, BAAI/bge-large-en-v1.5
- **Usage**: Enables semantic search - finds documents by meaning, not just keywords

---

## Search Configuration

### `top_k`
- **Description**: Number of top results to retrieve from vector search
- **Default**: `5`
- **Range**: 1-20
- **Usage**: How many document chunks to use as context for each answer

### `hybrid_search_ratio`
- **Description**: Balance between keyword and semantic search
- **Default**: `50`
- **Range**: 0-100
- **Usage**: 
  - 0 = keyword-only search
  - 100 = semantic-only search
  - 50 = balanced (recommended)

---

## Document Processing

### `chunk_size`
- **Description**: Size of text chunks when splitting documents
- **Default**: `512`
- **Range**: 256-4096
- **Usage**: Smaller chunks = more precise answers, larger chunks = more context

### `chunk_overlap`
- **Description**: Overlap between consecutive chunks
- **Default**: `128`
- **Range**: 0-512
- **Usage**: Ensures important context isn't lost at chunk boundaries

---

## Dual Model Mode

### `dual_mode`
- **Description**: Enable using two models for enhanced reasoning
- **Default**: `false`
- **Usage**: Some models (like deepseek-r1) excel at reasoning but are slow

### `dual_model1`
- **Description**: First model in dual mode (usually a fast model)
- **Default**: `"llama3.2:1b"`

### `dual_model2`
- **Description**: Second model in dual mode (usually a reasoning model)
- **Default**: `"llama3.2:3b"`

---

## Ollama Runtime Parameters

These affect how Ollama runs the model:

### `threads`
- **Description**: CPU threads to use (0 = auto)
- **Default**: `0`
- **Usage**: Set based on your CPU cores for optimal performance

### `batch`
- **Description**: Batch size for processing
- **Default**: `512`
- **Range**: 1-8192
- **Usage**: Higher = faster but more memory

### `ctx`
- **Description**: Context window size (max tokens)
- **Default**: `4096`
- **Range**: 512-131072
- **Usage**: How many tokens the model can "remember" in a conversation

### `gpu`
- **Description**: GPU layers to use
- **Default**: `0` (CPU only)
- **Usage**: -1 = all layers, 0 = CPU only, N = N layers on GPU

### `mmap`
- **Description**: Memory mapping mode
- **Default**: `1`
- **Options**: 0 = load in RAM (faster), 1 = stream from disk (less RAM)

### `numa`
- **Description**: Enable NUMA awareness
- **Default**: `false`
- **Usage**: Only for multi-socket servers

---

## UI Preferences

### `dark_mode`
- **Description**: Enable dark theme
- **Default**: `true`

### `show_system_info`
- **Description**: Show system information panel in settings
- **Default**: `true`

### `auto_save_sessions`
- **Description**: Automatically save chat sessions
- **Default**: `true`

### `max_messages_memory`
- **Description**: Number of messages to keep in memory
- **Default**: `100`
- **Usage**: Older messages are discarded to save memory

---

## Example Config

```json
{
  "default_model": "llama3.2:1b",
  "summary_model": "llama3.2:1b",
  "tag_model": "llama3.2:1b",
  "ollama_port": "11434",
  "ollama_base_url": "http://localhost:11434",
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "top_k": 5,
  "hybrid_search_ratio": 50,
  "chunk_size": 512,
  "chunk_overlap": 128,
  "dual_mode": false,
  "dual_model1": "llama3.2:1b",
  "dual_model2": "llama3.2:3b",
  "threads": 0,
  "batch": 512,
  "ctx": 4096,
  "gpu": 0,
  "mmap": 1,
  "numa": false,
  "dark_mode": true,
  "show_system_info": true,
  "auto_save_sessions": true,
  "max_messages_memory": 100
}
```
