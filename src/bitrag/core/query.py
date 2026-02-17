"""
BitRAG Query Engine

Handles RAG queries using Ollama LLM with model selection support.
"""

import os
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
import os
import json
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core import Document
import chromadb

from .config import get_config


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
    """RAG query engine with model selection support"""

    def __init__(
        self,
        session_id: str,
        model: Optional[str] = None,
        llm_type: Optional[str] = None,
    ):
        """
        Initialize the query engine.

        Args:
            session_id: Session ID for document isolation
            model: Model name (e.g., "bitnet-b1.58-2B-4T", "llama3.2:1b")
            llm_type: "bitnet" or "ollama" (auto-detected from model if not provided)
        """
        self.config = get_config()
        self.session_id = session_id

        # Set model
        self.model = model or self.config.default_model
        self.llm_type = llm_type or self._detect_llm_type(self.model)

        # Set up paths
        self.session_dir = self.config.get_session_dir(session_id)
        self.chroma_dir = self.config.get_session_chroma_dir(session_id)

        # Initialize components
        self._init_chroma()
        self._init_embedding()
        self._init_retriever()
        self._init_llm()
        self._init_synthesizer()

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

    def set_model(self, model_name: str):
        """
        Switch to a different model.

        Args:
            model_name: Name of the model to use
        """
        self.model = model_name
        self.llm_type = self._detect_llm_type(model_name)
        self._init_llm()
        self._init_synthesizer()

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
