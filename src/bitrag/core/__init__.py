"""
BitRAG Core Module

Core functionality for document indexing, querying, and graph building.
"""

from .config import Config, get_config, set_config
from .indexer import DocumentIndexer, create_session_indexer
from .query import QueryEngine, create_query_engine, OllamaService, get_ollama_service
from .summary_generator import SummaryGenerator, get_summary_generator, reset_summary_generator
from .tag_extractor import TagExtractor, get_tag_extractor, reset_tag_extractor
from .graph_builder import (
    GraphBuilder,
    GraphData,
    GraphNode,
    GraphLink,
    DocumentMetadata,
    get_graph_builder,
    reset_graph_builder,
)

__all__ = [
    # Config
    "Config",
    "get_config",
    "set_config",
    # Indexer
    "DocumentIndexer",
    "create_session_indexer",
    # Query
    "QueryEngine",
    "create_query_engine",
    "OllamaService",
    "get_ollama_service",
    # Summary
    "SummaryGenerator",
    "get_summary_generator",
    "reset_summary_generator",
    # Tag
    "TagExtractor",
    "get_tag_extractor",
    "reset_tag_extractor",
    # Graph
    "GraphBuilder",
    "GraphData",
    "GraphNode",
    "GraphLink",
    "DocumentMetadata",
    "get_graph_builder",
    "reset_graph_builder",
]
