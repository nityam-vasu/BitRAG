"""
BitRAG Graph Builder Module

Builds graph data structure for visualization.
Features:
- Integrates summary and tag generation
- Metadata caching to avoid regeneration
- Dynamic node sizing based on connections
- Weighted edge calculation based on shared tags
- ChromaDB integration for document metadata storage
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .config import get_config
from .summary_generator import SummaryGenerator, get_summary_generator
from .tag_extractor import TagExtractor, get_tag_extractor


@dataclass
class DocumentMetadata:
    """Metadata for a single document."""

    doc_id: str
    file_name: str
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)  # Legacy keywords
    category: int = 1  # 1-5 based on file type
    generated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "file_name": self.file_name,
            "summary": self.summary,
            "tags": self.tags,
            "keywords": self.keywords,
            "category": self.category,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        """Create from dictionary."""
        return cls(
            doc_id=data.get("doc_id", ""),
            file_name=data.get("file_name", ""),
            summary=data.get("summary", ""),
            tags=data.get("tags", []),
            keywords=data.get("keywords", []),
            category=data.get("category", 1),
            generated_at=data.get("generated_at"),
        )


@dataclass
class GraphNode:
    """A node in the graph."""

    id: str
    name: str
    val: int = 3  # Node size (dynamic)
    group: int = 1  # Category
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)  # Keep for compatibility

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "val": self.val,
            "group": self.group,
            "summary": self.summary,
            "tags": self.tags,
            "keywords": self.keywords,
        }


@dataclass
class GraphLink:
    """A link/edge in the graph."""

    source: str
    target: str
    value: int = 1  # Edge weight (shared tags count)
    label: str = ""  # Top shared tags

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "value": self.value,
            "label": self.label,
        }


@dataclass
class GraphData:
    """Complete graph data structure."""

    nodes: List[GraphNode] = field(default_factory=list)
    links: List[GraphLink] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "links": [l.to_dict() for l in self.links],
        }


class GraphBuilder:
    """
    Builds graph data for document visualization.

    Features:
    - LLM-powered summary and tag generation
    - Metadata caching to avoid regeneration
    - Dynamic node sizing based on connections
    - Tag-based edge creation with weights

    Usage:
        builder = GraphBuilder(indexer)
        graph_data = builder.build_graph()
    """

    def __init__(
        self,
        indexer: Any,
        summary_generator: Optional[SummaryGenerator] = None,
        tag_extractor: Optional[TagExtractor] = None,
        use_llm: bool = True,
    ):
        """
        Initialize the graph builder.

        Args:
            indexer: DocumentIndexer instance
            summary_generator: Optional SummaryGenerator (creates default if None)
            tag_extractor: Optional TagExtractor (creates default if None)
            use_llm: Whether to use LLM for generation (can disable for testing)
        """
        self.indexer = indexer
        self.summary_generator = summary_generator or get_summary_generator()
        self.tag_extractor = tag_extractor or get_tag_extractor()
        self.use_llm = use_llm

        # Metadata cache: {doc_id: DocumentMetadata}
        self._cache: Dict[str, DocumentMetadata] = {}

    def get_document_text(self, file_name: str) -> str:
        """Get full text content from a document."""
        try:
            doc_details = self.indexer.get_document(file_name)
            chunks = doc_details.get("chunks", [])
            text_parts = [chunk.get("text", "") for chunk in chunks]
            return " ".join(text_parts)
        except Exception as e:
            print(f"[GraphBuilder] Error getting document text: {e}")
            return ""

    def get_document_category(self, file_name: str) -> int:
        """Determine document category based on file extension."""
        if "." not in file_name:
            return 5  # Other

        ext = file_name.split(".")[-1].lower()

        if ext in ["pdf", "doc", "docx"]:
            return 1  # Documents
        elif ext in ["md", "txt"]:
            return 2  # Text files
        elif ext in ["py", "js", "java", "cpp", "ts", "jsx", "tsx"]:
            return 3  # Code
        elif ext in ["jpg", "png", "gif", "svg", "webp"]:
            return 4  # Images
        else:
            return 5  # Other

    def generate_metadata(self, doc_id: str, file_name: str, text: str) -> DocumentMetadata:
        """
        Generate metadata for a document.

        Args:
            doc_id: Document ID
            file_name: Document filename
            text: Full document text

        Returns:
            DocumentMetadata instance
        """
        metadata = DocumentMetadata(
            doc_id=doc_id,
            file_name=file_name,
            category=self.get_document_category(file_name),
            generated_at=datetime.now().isoformat(),
        )

        if not text.strip():
            return metadata

        # Generate summary
        if self.use_llm:
            try:
                metadata.summary = self.summary_generator.generate(text)
            except Exception as e:
                print(f"[GraphBuilder] Summary generation failed: {e}")
                metadata.summary = text[:200].replace("\n", " ") + "..."
        else:
            metadata.summary = text[:200].replace("\n", " ") + "..."

        # Extract tags
        if self.use_llm:
            try:
                metadata.tags = self.tag_extractor.extract_tags(text)
            except Exception as e:
                print(f"[GraphBuilder] Tag extraction failed: {e}")
                metadata.tags = self._extract_keyword_tags(text)
        else:
            metadata.tags = self._extract_keyword_tags(text)

        # Also keep keywords for compatibility
        metadata.keywords = self._extract_keyword_tags(text)

        return metadata

    def _extract_keyword_tags(self, text: str, max_tags: int = 10) -> List[str]:
        """Extract keyword tags using frequency (fallback)."""
        words = text.lower().split()
        word_freq: Dict[str, int] = {}

        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
        }

        for word in words:
            clean = word.strip(".,!?;:()\"'")
            if len(clean) >= 3 and clean.isalpha() and clean not in stopwords:
                word_freq[clean] = word_freq.get(clean, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:max_tags]]

    def get_metadata(
        self, doc_id: str, file_name: str, force_refresh: bool = False
    ) -> DocumentMetadata:
        """
        Get metadata for a document (with caching).

        Args:
            doc_id: Document ID
            file_name: Document filename
            force_refresh: Force regeneration even if cached

        Returns:
            DocumentMetadata instance
        """
        # Return cached if available and not refreshing
        if not force_refresh and doc_id in self._cache:
            return self._cache[doc_id]

        # Generate metadata
        text = self.get_document_text(file_name)
        metadata = self.generate_metadata(doc_id, file_name, text)

        # Cache it
        self._cache[doc_id] = metadata

        return metadata

    def calculate_node_size(self, doc_id: str, all_metadata: Dict[str, DocumentMetadata]) -> int:
        """
        Calculate dynamic node size based on connections.

        More connections = larger node.

        Args:
            doc_id: Document ID
            all_metadata: Metadata for all documents

        Returns:
            Node size (1-10)
        """
        if doc_id not in all_metadata:
            return 3

        doc_tags = set(all_metadata[doc_id].tags)

        # Count connections (documents sharing at least one tag)
        connections = 0
        for other_id, other_meta in all_metadata.items():
            if other_id != doc_id:
                other_tags = set(other_meta.tags)
                if doc_tags & other_tags:  # Intersection
                    connections += 1

        # Scale: 0 connections = 1, 5+ connections = 5, 10+ = 10
        if connections == 0:
            return 2
        elif connections <= 2:
            return 3
        elif connections <= 5:
            return 5
        elif connections <= 10:
            return 7
        else:
            return 10

    def calculate_shared_tags(self, tags1: List[str], tags2: List[str]) -> Tuple[int, List[str]]:
        """
        Calculate shared tags between two documents.

        Returns:
            Tuple of (count, top_shared_tags)
        """
        set1 = set(t.lower() for t in tags1)
        set2 = set(t.lower() for t in tags2)

        shared = set1 & set2
        shared_list = list(shared)[:3]  # Top 3 for label

        return len(shared), shared_list

    def build_graph(self, force_refresh: bool = False) -> GraphData:
        """
        Build complete graph data.

        Args:
            force_refresh: Force regeneration of all metadata

        Returns:
            GraphData instance
        """
        # Get all documents
        docs = self.indexer.list_documents()

        if not docs:
            return GraphData()

        # Generate/load metadata for all documents
        all_metadata: Dict[str, DocumentMetadata] = {}

        for doc in docs:
            doc_id = doc.get("id", "")
            file_name = doc.get("file_name", "")

            if doc_id and file_name:
                metadata = self.get_metadata(doc_id, file_name, force_refresh)
                all_metadata[doc_id] = metadata

        # Create nodes
        nodes: List[GraphNode] = []

        for doc_id, metadata in all_metadata.items():
            node_size = self.calculate_node_size(doc_id, all_metadata)

            node = GraphNode(
                id=doc_id,
                name=metadata.file_name,
                val=node_size,
                group=metadata.category,
                summary=metadata.summary,
                tags=metadata.tags,
                keywords=metadata.keywords,
            )
            nodes.append(node)

        # Create edges based on shared tags
        links: List[GraphLink] = []
        seen_edges: Set[Tuple[str, str]] = set()

        doc_ids = list(all_metadata.keys())

        for i, doc1_id in enumerate(doc_ids):
            for doc2_id in doc_ids[i + 1 :]:
                meta1 = all_metadata[doc1_id]
                meta2 = all_metadata[doc2_id]

                shared_count, shared_tags = self.calculate_shared_tags(meta1.tags, meta2.tags)

                # Create edge if shared tags exist
                if shared_count >= 1:
                    # Normalize edge (smaller ID first)
                    edge = tuple(sorted([doc1_id, doc2_id]))

                    if edge not in seen_edges:
                        seen_edges.add(edge)

                        link = GraphLink(
                            source=doc1_id,
                            target=doc2_id,
                            value=shared_count,
                            label=", ".join(shared_tags),
                        )
                        links.append(link)

        return GraphData(nodes=nodes, links=links)

    def regenerate_document(self, doc_id: str, file_name: str) -> DocumentMetadata:
        """
        Regenerate metadata for a specific document.

        Args:
            doc_id: Document ID
            file_name: Document filename

        Returns:
            New DocumentMetadata
        """
        # Clear from cache
        if doc_id in self._cache:
            del self._cache[doc_id]

        # Generate fresh metadata
        return self.get_metadata(doc_id, file_name, force_refresh=True)

    def clear_cache(self) -> None:
        """Clear the metadata cache."""
        self._cache.clear()
        print("[GraphBuilder] Cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_documents": len(self._cache),
            "use_llm": self.use_llm,
            "summary_generator": self.summary_generator.get_info(),
            "tag_extractor": self.tag_extractor.get_info(),
        }


# Global instance (created on first use)
_graph_builder: Optional[GraphBuilder] = None


def get_graph_builder(indexer: Any, **kwargs) -> GraphBuilder:
    """
    Get or create the global GraphBuilder instance.

    Args:
        indexer: DocumentIndexer instance
        **kwargs: Additional arguments for GraphBuilder

    Returns:
        GraphBuilder instance
    """
    global _graph_builder

    if _graph_builder is None:
        _graph_builder = GraphBuilder(indexer=indexer, **kwargs)

    return _graph_builder


def reset_graph_builder() -> None:
    """Reset the global builder instance."""
    global _graph_builder
    _graph_builder = None
