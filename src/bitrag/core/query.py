"""
BitRAG Query Engine

Handles RAG queries using Ollama LLM with model selection support.
Includes proper Ollama availability checking and model validation.
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import CustomLLM
from llama_index.core.llms import CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import Any, Dict, Optional
import subprocess
import json
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core import Document
import chromadb

from .config import get_config


class OllamaService:
    """
    Ollama service class for managing Ollama connections and model validation.
    Based on the working implementation from OLLAMA_INTEGRATION.md
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self._available_models: Optional[List[str]] = None

    def is_available(self) -> bool:
        """
        Check if Ollama server is available.
        Uses GET /api/tags endpoint (same as OLLAMA_INTEGRATION.md)
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.ok
        except (requests.ConnectionError, requests.Timeout):
            return False

    def list_models(self) -> List[str]:
        """
        Get list of available models from Ollama.
        Returns cached list if available.
        """
        if self._available_models is not None:
            return self._available_models

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.ok:
                data = response.json()
                self._available_models = [m.get("name", "") for m in data.get("models", [])]
                return self._available_models
        except (requests.ConnectionError, requests.Timeout):
            pass

        return []

    def model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists on the Ollama server."""
        available = self.list_models()
        return model_name in available

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.ok:
                data = response.json()
                for m in data.get("models", []):
                    if m.get("name") == model_name:
                        return m
        except (requests.ConnectionError, requests.Timeout):
            pass
        return None

    def pull_model(self, model_name: str, timeout: int = 300) -> bool:
        """
        Pull a model from Ollama registry.
        Note: This is a non-blocking check - actual pulling happens in background.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/pull", json={"name": model_name}, timeout=timeout, stream=True
            )
            return response.ok
        except (requests.ConnectionError, requests.Timeout):
            return False

    def invalidate_cache(self):
        """Invalidate the cached model list."""
        self._available_models = None


# Global Ollama service instance
_ollama_service: Optional[OllamaService] = None


def get_ollama_service(base_url: str = None) -> OllamaService:
    """Get or create the global Ollama service instance."""
    global _ollama_service
    if _ollama_service is None:
        config = get_config()
        url = base_url or config.ollama_base_url
        _ollama_service = OllamaService(base_url=url)
    return _ollama_service


class BitNetCppLLM(CustomLLM):
    """Custom LLM class for BitNet.cpp integration"""

    model_name: str = "bitnet-b1.58-2B-4T"
    max_tokens: int = 512
    temperature: float = 0.1
    bitnet_cpp_path: str = "/bitnet"

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata"""
        return LLMMetadata(
            context_window=4096,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt using BitNet.cpp"""
        try:
            # Prepare the prompt file
            with open("/tmp/bitnet_prompt.txt", "w") as f:
                f.write(prompt)

            # Run BitNet.cpp inference
            cmd = [
                "make",
                "run",
                f"MODEL={self.bitnet_cpp_path}/models/placeholder.gguf",  # This would need to be updated with actual model
                f"PROMPT={prompt}",
                f"TEMP={self.temperature}",
                f"N_THREADS=4",
            ]

            # Note: This is a simplified version - actual BitNet.cpp usage may vary
            # The actual implementation would depend on the specific BitNet.cpp API

            # For now, let's use a placeholder approach that calls the binary directly
            # This assumes the BitNet.cpp build creates a binary we can call
            result = subprocess.run(
                [
                    f"{self.bitnet_cpp_path}/main",  # Adjust path based on actual BitNet.cpp build output
                    "-m",
                    f"{self.bitnet_cpp_path}/models/placeholder.gguf",  # Placeholder - actual model path
                    "-p",
                    prompt,
                    "-n",
                    str(self.max_tokens),
                    "--temp",
                    str(self.temperature),
                ],
                capture_output=True,
                text=True,
                cwd=self.bitnet_cpp_path,
            )

            if result.returncode == 0:
                response_text = result.stdout.strip()
            else:
                # Fallback to a simple response if BitNet.cpp fails
                response_text = (
                    f"BitNet.cpp execution failed: {result.stderr}. Using fallback response."
                )

        except Exception as e:
            response_text = f"Error calling BitNet.cpp: {str(e)}. Using fallback response."

        return CompletionResponse(text=response_text, additional_kwargs={})


# Default RAG prompt template
DEFAULT_RAG_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Be concise and clear
- Use the context to provide specific answers

Answer:"""


class QueryEngine:
    """RAG query engine with model selection support and Ollama integration"""

    def __init__(
        self,
        session_id: str,
        model: Optional[str] = None,
        llm_type: Optional[str] = None,
        _skip_ollama_check: bool = False,
    ):
        """
        Initialize the query engine.

        Args:
            session_id: Session ID for document isolation
            model: Model name (e.g., "bitnet-b1.58-2B-4T", "llama3.2:1b")
            llm_type: "bitnet" or "ollama" (auto-detected from model if not provided)
            _skip_ollama_check: Skip Ollama availability check (for testing)
        """
        self.config = get_config()
        self.session_id = session_id

        # Set model
        self.model = model or self.config.default_model
        self.llm_type = llm_type or self._detect_llm_type(self.model)

        # Set up paths
        self.session_dir = self.config.get_session_dir(session_id)
        self.chroma_dir = self.config.get_session_chroma_dir(session_id)

        # Ollama service for availability checking and model validation
        self._ollama = get_ollama_service(self.config.ollama_base_url)

        # Check Ollama availability and model validity (unless skipped)
        if not _skip_ollama_check:
            self._validate_ollama_setup()

        # Initialize components
        self._init_chroma()
        self._init_embedding()
        self._init_retriever()
        self._init_llm()
        self._init_synthesizer()

    def _validate_ollama_setup(self):
        """Validate Ollama is available and the model exists"""
        if self.llm_type != "ollama":
            return

        # Check if Ollama is running
        if not self._ollama.is_available():
            print(f"[WARN] Ollama not available at {self._ollama.base_url}")
            print(f"[WARN] Make sure Ollama is running: ollama serve")
            return

        # Check if the model exists
        if not self._ollama.model_exists(self.model):
            print(f"[WARN] Model '{self.model}' not found on Ollama server")
            available = self._ollama.list_models()
            if available:
                print(f"[INFO] Available models: {', '.join(available)}")
            else:
                print(f"[INFO] Run 'ollama pull {self.model}' to download the model")

    def _detect_llm_type(self, model: str) -> str:
        """Detect LLM type from model name"""
        if "bitnet" in model.lower():
            return "bitnet"
        return "ollama"

    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))

        # Get collection for this session
        collection_name = f"{self.config.collection_name}_{self.session_id}"
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"session_id": self.session_id}
        )

    def _init_embedding(self):
        """Initialize embedding model"""
        self.embedding_model = HuggingFaceEmbedding(model_name=self.config.embedding_model)

    def _init_retriever(self):
        """Initialize retriever"""
        from llama_index.vector_stores.chroma import ChromaVectorStore

        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

        # Create index (from vector store)
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store, embed_model=self.embedding_model
        )

        # Create retriever
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.config.top_k,
        )

    def _init_llm(self):
        """Initialize Ollama LLM"""
        self.llm = Ollama(
            model=self.model,
            base_url=self.config.ollama_base_url,
            temperature=0.1,
            request_timeout=120,  # 2 minute timeout for generation
        )

    def _init_synthesizer(self):
        """Initialize response synthesizer"""
        self.synthesizer = get_response_synthesizer(
            llm=self.llm,
            text_qa_template=self._get_rag_prompt(),
        )

    def _get_rag_prompt(self) -> str:
        """Get RAG prompt template"""
        # Use default prompt
        return DEFAULT_RAG_PROMPT

    def set_model(self, model_name: str, validate: bool = True) -> bool:
        """
        Switch to a different model.

        Args:
            model_name: Name of the model to use
            validate: Whether to validate the model exists on Ollama

        Returns:
            True if model was set successfully, False if validation failed
        """
        # Validate model exists if using Ollama
        if validate and self.llm_type == "ollama":
            self._ollama.invalidate_cache()  # Refresh model list
            if not self._ollama.is_available():
                print(f"[WARN] Ollama not available at {self._ollama.base_url}")
                print(f"[WARN] Cannot validate model. Proceeding anyway...")
            elif not self._ollama.model_exists(model_name):
                print(f"[WARN] Model '{model_name}' not found on Ollama server")
                available = self._ollama.list_models()
                if available:
                    print(f"[INFO] Available models: {', '.join(available)}")
                return False

        self.model = model_name
        self.llm_type = self._detect_llm_type(model_name)
        self._init_llm()
        self._init_synthesizer()
        return True

    def get_current_model(self) -> Dict[str, str]:
        """
        Get current model information.

        Returns:
            Dictionary with model info
        """
        return {
            "model": self.model,
            "llm_type": self.llm_type,
            "base_url": self.config.ollama_base_url,
        }

    def get_ollama_status(self) -> Dict[str, Any]:
        """
        Get Ollama connection status.

        Returns:
            Dictionary with status information
        """
        if self.llm_type != "ollama":
            return {
                "available": False,
                "reason": "Not using Ollama",
                "model": self.model,
            }

        is_available = self._ollama.is_available()
        model_exists = self._ollama.model_exists(self.model) if is_available else False
        available_models = self._ollama.list_models() if is_available else []

        return {
            "available": is_available,
            "model_exists": model_exists,
            "model": self.model,
            "base_url": self._ollama.base_url,
            "available_models": available_models,
        }

    def refresh_ollama_models(self):
        """Refresh the cached list of available Ollama models."""
        self._ollama.invalidate_cache()

    def get_retrieved_context(self, question: str) -> List[Dict[str, Any]]:
        """
        Retrieve context chunks without generating a response.

        Args:
            question: Query question

        Returns:
            List of retrieved chunks with metadata
        """
        # Retrieve nodes
        retrieved_nodes = self.retriever.retrieve(question)

        results = []
        for i, node in enumerate(retrieved_nodes):
            results.append(
                {
                    "rank": i + 1,
                    "text": node.node.get_content(),
                    "score": node.score,
                    "metadata": node.metadata,
                }
            )

        return results

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system with a single question.

        Args:
            question: Question to ask

        Returns:
            Dictionary with response and sources
        """
        # Retrieve context
        retrieved_context = self.get_retrieved_context(question)

        if not retrieved_context:
            return {
                "question": question,
                "response": "No documents found in the index. Please upload documents first.",
                "sources": [],
            }

        # Build context from retrieved chunks
        context_parts = []
        for item in retrieved_context:
            context_parts.append(item["text"])

        context = "\n\n---\n\n".join(context_parts)

        # Generate response using LLM directly
        prompt = DEFAULT_RAG_PROMPT.format(context=context, question=question)

        # Generate response
        response = self.llm.complete(prompt)

        return {
            "question": question,
            "response": response.text,
            "sources": retrieved_context,
            "model": self.model,
            "llm_type": self.llm_type,
        }

    def query_streaming(self, question: str) -> Generator[Dict[str, Any], None, None]:
        """
        Query the RAG system with streaming response.

        Args:
            question: Question to ask

        Yields:
            Dictionary with response chunks and sources
        """
        # Retrieve context (first yield)
        retrieved_context = self.get_retrieved_context(question)

        if not retrieved_context:
            yield {
                "type": "error",
                "message": "No documents found in the index. Please upload documents first.",
            }
            return

        yield {
            "type": "sources",
            "sources": retrieved_context,
        }

        # Build context
        context_parts = []
        for item in retrieved_context:
            context_parts.append(item["text"])

        context = "\n\n---\n\n".join(context_parts)

        # Generate prompt
        prompt = DEFAULT_RAG_PROMPT.format(context=context, question=question)

        # Stream response
        response_text = ""
        for chunk in self.llm.stream_complete(prompt):
            response_text += chunk.delta
            yield {
                "type": "chunk",
                "text": chunk.delta,
                "full_text": response_text,
            }

        yield {
            "type": "done",
            "response": response_text,
            "model": self.model,
        }

    def get_document_count(self) -> int:
        """Get number of indexed documents"""
        return self.collection.count()

    def has_documents(self) -> bool:
        """Check if there are any indexed documents"""
        return self.get_document_count() > 0


def create_query_engine(
    session_id: str,
    model: Optional[str] = None,
    llm_type: Optional[str] = None,
) -> QueryEngine:
    """
    Create a QueryEngine for a specific session.

    Args:
        session_id: Session ID
        model: Model name
        llm_type: LLM type ("bitnet" or "ollama")

    Returns:
        QueryEngine instance
    """
    return QueryEngine(session_id, model, llm_type)
