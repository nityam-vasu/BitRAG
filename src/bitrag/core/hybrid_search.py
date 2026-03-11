"""
BitRAG Hybrid Search

Combines vector similarity search with BM25 keyword search using
Reciprocal Rank Fusion (RRF) for improved document retrieval.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import numpy as np

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    raise ImportError("rank-bm25 is required. Install with: pip install rank-bm25")

import chromadb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class HybridSearch:
    """
    Hybrid search combining vector similarity with BM25 keyword search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    """

    def __init__(
        self,
        session_id: str,
        chroma_dir: str,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        alpha: float = 0.5,
        rrf_k: int = 60,
    ):
        """
        Initialize hybrid search.

        Args:
            session_id: Session ID for isolation
            chroma_dir: Path to ChromaDB directory
            embedding_model: HuggingFace embedding model name
            alpha: Weight for vector search (0=keyword, 1=vector, 0.5=balanced)
            rrf_k: Constant for RRF formula (default 60)
        """
        self.session_id = session_id
        self.chroma_dir = chroma_dir
        self.embedding_model_name = embedding_model
        self.alpha = alpha
        self.rrf_k = rrf_k

        # Paths
        self.bm25_dir = Path(chroma_dir).parent / "bm25_index"
        self.bm25_file = self.bm25_dir / "bm25_index.pkl"

        # Initialize ChromaDB
        self._init_chroma()

        # Initialize embedding model
        self._init_embedding()

        # BM25 index
        self._bm25: Optional[BM25Okapi] = None
        self._doc_map: Dict[int, str] = {}  # index -> doc_id
        self._id_to_doc: Dict[str, str] = {}  # doc_id -> text

        # Load existing BM25 index if available
        self._load_bm25_index()

    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)

        collection_name = f"bitrag_{self.session_id}"
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"session_id": self.session_id}
        )

    def _init_embedding(self):
        """Initialize embedding model"""
        self.embedding_model = HuggingFaceEmbedding(model_name=self.embedding_model_name)

    def _load_bm25_index(self):
        """Load existing BM25 index from disk"""
        if self.bm25_file.exists():
            try:
                with open(self.bm25_file, "rb") as f:
                    data = pickle.load(f)
                    self._bm25 = data["bm25"]
                    self._doc_map = data["doc_map"]
                    self._id_to_doc = data["id_to_doc"]
            except Exception as e:
                print(f"Failed to load BM25 index: {e}")
                self._build_bm25_index()
        else:
            # Build index from existing ChromaDB documents
            self._build_bm25_index()

    def _save_bm25_index(self):
        """Save BM25 index to disk"""
        os.makedirs(self.bm25_dir, exist_ok=True)

        data = {
            "bm25": self._bm25,
            "doc_map": self._doc_map,
            "id_to_doc": self._id_to_doc,
        }

        with open(self.bm25_file, "wb") as f:
            pickle.dump(data, f)

    def _build_bm25_index(self):
        """Build BM25 index from ChromaDB documents"""
        results = self.collection.get()

        if not results.get("ids"):
            self._bm25 = None
            return

        # Build document list and mappings
        documents = []
        self._doc_map = {}
        self._id_to_doc = {}

        for i, doc_id in enumerate(results["ids"]):
            text = results["documents"][i]
            if text:  # Only add non-empty documents
                documents.append(text)
                self._doc_map[len(documents) - 1] = doc_id
                self._id_to_doc[doc_id] = text

        if documents:
            # Tokenize documents (simple whitespace tokenization)
            tokenized_docs = [doc.split() for doc in documents]
            self._bm25 = BM25Okapi(tokenized_docs)
            self._save_bm25_index()
        else:
            self._bm25 = None

    def rebuild_index(self):
        """Rebuild BM25 index from ChromaDB"""
        self._build_bm25_index()

    def vector_search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Perform vector similarity search.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (doc_id, score) tuples
        """
        # Get query embedding
        query_embedding = self.embedding_model.get_text_embedding(query)

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k * 2,  # Get more for fusion
        )

        # Convert distances to similarities (lower distance = higher similarity)
        vector_results = []
        if results.get("ids") and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if "distances" in results else 0
                # Convert distance to similarity score (1 - distance)
                score = 1 - distance if distance is not None else 1.0
                vector_results.append((doc_id, score))

        return vector_results

    def keyword_search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Perform BM25 keyword search.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (doc_id, score) tuples
        """
        if self._bm25 is None:
            self._build_bm25_index()

        if self._bm25 is None:
            return []

        # Tokenize query
        tokenized_query = query.split()

        # Get BM25 scores
        scores = self._bm25.get_scores(tokenized_query)

        # Get top-k results
        top_indices = np.argsort(scores)[::-1][: k * 2]

        keyword_results = []
        for idx in top_indices:
            if scores[idx] > 0 and idx in self._doc_map:
                doc_id = self._doc_map[idx]
                keyword_results.append((doc_id, float(scores[idx])))

        return keyword_results

    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: float = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and keyword search.

        Args:
            query: Search query
            k: Number of results to return
            alpha: Override alpha parameter (uses instance default if None)

        Returns:
            List of dicts with id, text, metadata, and score
        """
        if alpha is None:
            alpha = self.alpha

        # Get results from both methods
        vector_results = self.vector_search(query, k * 2)
        keyword_results = self.keyword_search(query, k * 2)

        # Apply RRF fusion
        fused_results = self._reciprocal_rank_fusion(vector_results, keyword_results, alpha=alpha)

        # Get document contents for top-k
        final_results = []
        for doc_id, score in fused_results[:k]:
            doc = self.collection.get(ids=[doc_id])
            if doc["documents"]:
                final_results.append(
                    {
                        "id": doc_id,
                        "text": doc["documents"][0],
                        "metadata": doc["metadatas"][0] if doc["metadatas"] else {},
                        "score": score,
                        "rank": len(final_results) + 1,
                    }
                )

        return final_results

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Tuple[str, float]],
        keyword_results: List[Tuple[str, float]],
        alpha: float = 0.5,
    ) -> List[Tuple[str, float]]:
        """
        Combine results using Reciprocal Rank Fusion with alpha weighting.

        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            alpha: Weight for vector search (0=keyword only, 1=vector only)

        Returns:
            Combined and sorted list of (doc_id, fused_score)
        """
        rrf_scores = {}

        # Process vector results
        for rank, (doc_id, score) in enumerate(vector_results, 1):
            rrf_score = alpha * (1 / (self.rrf_k + rank))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + rrf_score

        # Process keyword results
        for rank, (doc_id, score) in enumerate(keyword_results, 1):
            rrf_score = (1 - alpha) * (1 / (self.rrf_k + rank))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + rrf_score

        # Sort by fused score descending
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_results

    def set_alpha(self, alpha: float):
        """Set alpha parameter for hybrid search"""
        self.alpha = max(0, min(1, alpha))

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        return {
            "total_documents": self.collection.count(),
            "bm25_indexed": len(self._doc_map),
            "alpha": self.alpha,
            "rrf_k": self.rrf_k,
        }


def create_hybrid_search(
    session_id: str,
    chroma_dir: str,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
    alpha: float = 0.5,
) -> HybridSearch:
    """
    Factory function to create a HybridSearch instance.

    Args:
        session_id: Session ID
        chroma_dir: ChromaDB directory path
        embedding_model: Embedding model name
        alpha: Hybrid search alpha parameter

    Returns:
        HybridSearch instance
    """
    return HybridSearch(
        session_id=session_id,
        chroma_dir=chroma_dir,
        embedding_model=embedding_model,
        alpha=alpha,
    )
