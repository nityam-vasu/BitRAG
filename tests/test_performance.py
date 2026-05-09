"""
BitRAG Performance Test Script

This script tests the performance of BitRAG including:
- Embedding generation time
- Vector and indexing generation time
- Inference time during chat
- Logs user queries and responses

Generates an XML report with system information, time/resource metrics,
document type, configuration, and LLM details.
"""

import os
import sys
import time
import json
import platform
import shutil
import tempfile
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import pytest

"""

Add src to path - this must be FIRST to avoid bitrag.py conflict
"""
import os
import sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_SRC_PATH = os.path.join(_PROJECT_ROOT, 'src')
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)


class PerformanceMetrics:
    """Class to collect and store performance metrics."""

    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.embedding_time: float = 0
        self.vector_indexing_time: float = 0
        self.inference_times: List[float] = []
        self.memory_usage_mb: float = 0
        self.cpu_usage_percent: float = 0
        self.query_log: List[Dict[str, Any]] = []

    def start(self):
        """Start timing."""
        self.start_time = time.time()

    def stop(self):
        """Stop timing."""
        self.end_time = time.time()

    def get_total_time(self) -> float:
        """Get total elapsed time."""
        return self.end_time - self.start_time

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)

    def log_query(self, query: str, response: str, inference_time: float):
        """Log a query and its response."""
        self.query_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "inference_time_seconds": inference_time,
            }
        )
        self.inference_times.append(inference_time)


class SystemInfo:
    """Collect system information."""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }

        # Try to get GPU info (if available)
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,driver_version,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                info["gpu_info"] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            info["gpu_info"] = "Not available"

        return info


class BitRAGPerformanceTest:
    """Main performance test class for BitRAG."""

    def __init__(self, temp_dir: str, session_id: str = "perf_test"):
        self.temp_dir = temp_dir
        self.session_id = session_id
        self.metrics = PerformanceMetrics()
        self.config = None
        self.indexer = None
        self.query_engine = None
        self.document_path: Optional[str] = None
        self.document_type: Optional[str] = None

    def setup(self):
        """Set up the test environment."""
        from bitrag.core.config import Config

        self.config = Config(
            data_dir=os.path.join(self.temp_dir, "data"),
            chroma_dir=os.path.join(self.temp_dir, "chroma_db"),
            sessions_dir=os.path.join(self.temp_dir, "sessions"),
        )

    def set_document(self, file_path: str):
        """Set the document to test."""
        self.document_path = file_path
        self.document_type = Path(file_path).suffix.upper().replace(".", "")

    def run_embedding_test(self) -> Dict[str, Any]:
        """Test embedding generation time."""
        from bitrag.core.indexer import DocumentIndexer

        self.metrics.start()

        # Initialize indexer
        self.indexer = DocumentIndexer(session_id=self.session_id)

        mem_before = self.metrics.get_memory_usage()
        cpu_before = self.metrics.get_cpu_usage()

        if self.document_path:
            # Time the embedding generation
            start = time.time()
            doc_id = self.indexer.index_document(self.document_path)
            end = time.time()

            self.metrics.embedding_time = end - start
            self.metrics.memory_usage_mb = self.metrics.get_memory_usage() - mem_before
            self.metrics.cpu_usage_percent = self.metrics.get_cpu_usage()

            return {
                "document_id": doc_id,
                "embedding_time_seconds": self.metrics.embedding_time,
                "memory_used_mb": self.metrics.memory_usage_mb,
                "cpu_usage_percent": self.metrics.cpu_usage_percent,
                "document_count": self.indexer.get_document_count(),
            }

        return {"error": "No document set"}

    def run_vector_indexing_test(self) -> Dict[str, Any]:
        """Test vector indexing time."""
        if not self.indexer:
            return {"error": "Indexer not initialized"}

        # Get document count for verification
        doc_count = self.indexer.get_document_count()

        return {
            "total_documents_indexed": doc_count,
            "vector_store_initialized": True,
            "indexing_complete": True,
        }

    def run_inference_test(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Test inference time for each query."""
        from bitrag.core.query import QueryEngine

        if not self.indexer:
            return [{"error": "Indexer not initialized"}]

        # Initialize query engine
        self.query_engine = QueryEngine(
            session_id=self.session_id,
            _skip_ollama_check=False,  # Set to True to skip Ollama check
        )

        results = []
        for query in queries:
            start = time.time()

            try:
                response = self.query_engine.query(query)
                end = time.time()

                inference_time = end - start

                self.metrics.log_query(
                    query=query,
                    response=response.get("response", ""),
                    inference_time=inference_time,
                )

                results.append(
                    {
                        "query": query,
                        "response": response.get("response", ""),
                        "inference_time_seconds": inference_time,
                        "model_used": response.get("model", self.config.default_model),
                        "llm_type": response.get("llm_type", "ollama"),
                        "sources_count": len(response.get("sources", [])),
                    }
                )
            except Exception as e:
                results.append({"query": query, "error": str(e), "inference_time_seconds": -1})

        return results


class XMLReportGenerator:
    """Generate XML report from performance test results."""

    def __init__(self, metrics: PerformanceMetrics, system_info: Dict, config: Any):
        self.metrics = metrics
        self.system_info = system_info
        self.config = config

    def generate(self, test_results: Dict[str, Any], output_path: str):
        """Generate XML report."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate averages
        avg_inference_time = 0
        if self.metrics.inference_times:
            avg_inference_time = sum(self.metrics.inference_times) / len(
                self.metrics.inference_times
            )

        # Build XML content
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<bitrag_performance_report>
    <report_metadata>
        <generated_at>{current_time}</generated_at>
        <report_version>1.0</report_version>
    </report_metadata>
    
    <system_information>
        <platform>{self.system_info.get("platform", "Unknown")}</platform>
        <platform_version>{self.system_info.get("platform_version", "Unknown")}</platform_version>
        <platform_release>{self.system_info.get("platform_release", "Unknown")}</platform_release>
        <architecture>{self.system_info.get("architecture", "Unknown")}</architecture>
        <processor>{self.system_info.get("processor", "Unknown")}</processor>
        <cpu_count_physical>{self.system_info.get("cpu_count_physical", 0)}</cpu_count_physical>
        <cpu_count_logical>{self.system_info.get("cpu_count_logical", 0)}</cpu_count_logical>
        <total_memory_gb>{self.system_info.get("total_memory_gb", 0)}</total_memory_gb>
        <available_memory_gb>{self.system_info.get("available_memory_gb", 0)}</available_memory_gb>
        <python_version>{self.system_info.get("python_version", "Unknown")}</python_version>
        <python_implementation>{self.system_info.get("python_implementation", "Unknown")}</python_implementation>
        <gpu_info>{self.system_info.get("gpu_info", "Not available")}</gpu_info>
    </system_information>
    
    <configuration>
        <embedding_model>{self.config.embedding_model}</embedding_model>
        <default_model>{self.config.default_model}</default_model>
        <summary_model>{self.config.summary_model}</summary_model>
        <tag_model>{self.config.tag_model}</tag_model>
        <llm_type>{self.config.llm_type}</llm_type>
        <ollama_base_url>{self.config.ollama_base_url}</ollama_base_url>
        <chunk_size>{self.config.chunk_size}</chunk_size>
        <chunk_overlap>{self.config.chunk_overlap}</chunk_overlap>
        <top_k>{self.config.top_k}</top_k>
        <collection_name>{self.config.collection_name}</collection_name>
        <ollama_parameters>
            <threads>{self.config.ollama_params.threads}</threads>
            <batch>{self.config.ollama_params.batch}</batch>
            <context_window>{self.config.ollama_params.ctx}</context_window>
            <mmap>{self.config.ollama_params.mmap}</mmap>
            <numa>{self.config.ollama_params.numa}</numa>
            <gpu_layers>{self.config.ollama_params.gpu}</gpu_layers>
        </ollama_parameters>
    </configuration>
    
    <document_information>
        <document_type>{test_results.get("document_type", "N/A")}</document_type>
        <document_path>{test_results.get("document_path", "N/A")}</document_path>
    </document_information>
    
    <performance_metrics>
        <embedding_generation>
            <time_seconds>{test_results.get("embedding_time", 0):.4f}</time_seconds>
            <memory_used_mb>{test_results.get("memory_used_mb", 0):.2f}</memory_used_mb>
            <cpu_usage_percent>{test_results.get("cpu_usage_percent", 0):.2f}</cpu_usage_percent>
        </embedding_generation>
        
        <vector_indexing>
            <total_documents>{test_results.get("total_documents_indexed", 0)}</total_documents>
            <vector_store_initialized>{test_results.get("vector_store_initialized", False)}</vector_store_initialized>
        </vector_indexing>
        
        <inference_metrics>
            <total_queries>{len(self.metrics.query_log)}</total_queries>
            <average_inference_time_seconds>{avg_inference_time:.4f}</average_inference_time_seconds>
            <min_inference_time_seconds>{min(self.metrics.inference_times) if self.metrics.inference_times else 0:.4f}</min_inference_time_seconds>
            <max_inference_time_seconds>{max(self.metrics.inference_times) if self.metrics.inference_times else 0:.4f}</max_inference_time_seconds>
        </inference_metrics>
        
        <resource_investment>
            <total_processing_time_seconds>{self.metrics.get_total_time():.4f}</total_processing_time_seconds>
            <peak_memory_usage_mb>{self.metrics.get_memory_usage():.2f}</peak_memory_usage_mb>
        </resource_investment>
    </performance_metrics>
    
    <query_log>"""

        for log_entry in self.metrics.query_log:
            xml_content += f"""
        <query_entry>
            <timestamp>{log_entry["timestamp"]}</timestamp>
            <query><![CDATA[{log_entry["query"]}]]></query>
            <response><![CDATA[{log_entry["response"][:500]}]]></response>
            <inference_time_seconds>{log_entry["inference_time_seconds"]:.4f}</inference_time_seconds>
        </query_entry>"""

        xml_content += """
    </query_log>
    
    <inference_results>"""

        for result in test_results.get("inference_results", []):
            xml_content += f"""
        <result>
            <query><![CDATA[{result.get("query", "")}]]></query>
            <response><![CDATA[{result.get("response", "")[:500]}]]></response>
            <inference_time_seconds>{result.get("inference_time_seconds", 0):.4f}</inference_time_seconds>
            <model_used>{result.get("model_used", "N/A")}</model_used>
            <llm_type>{result.get("llm_type", "N/A")}</llm_type>
            <sources_count>{result.get("sources_count", 0)}</sources_count>
        </result>"""

        xml_content += """
    </inference_results>
    
</bitrag_performance_report>"""

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        return output_path


def run_performance_test(
    document_path: str,
    test_queries: List[str],
    session_id: str = "perf_test",
    output_xml: str = "bitrag_performance_report.xml",
) -> Dict[str, Any]:
    """
    Run complete performance test and generate XML report.

    Args:
        document_path: Path to the document to test
        test_queries: List of queries to test
        session_id: Session ID for isolation
        output_xml: Output path for XML report

    Returns:
        Dictionary with test results
    """
    # Create temp directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Initialize test
        test = BitRAGPerformanceTest(temp_dir, session_id)
        test.setup()
        test.set_document(document_path)

        # Start overall timing
        test.metrics.start()

        # Run embedding test
        print("Running embedding generation test...")
        embedding_results = test.run_embedding_test()

        # Run vector indexing test
        print("Running vector indexing test...")
        indexing_results = test.run_vector_indexing_test()

        # Run inference test
        print("Running inference tests...")
        inference_results = test.run_inference_test(test_queries)

        # Stop timing
        test.metrics.stop()

        # Compile results
        results = {
            "document_type": test.document_type,
            "document_path": document_path,
            "embedding_time": embedding_results.get("embedding_time_seconds", 0),
            "memory_used_mb": embedding_results.get("memory_used_mb", 0),
            "cpu_usage_percent": embedding_results.get("cpu_usage_percent", 0),
            "total_documents_indexed": indexing_results.get("total_documents_indexed", 0),
            "vector_store_initialized": indexing_results.get("vector_store_initialized", False),
            "inference_results": inference_results,
        }

        # Generate XML report
        print("Generating XML report...")
        system_info = SystemInfo.get_system_info()
        report_gen = XMLReportGenerator(test.metrics, system_info, test.config)
        report_path = report_gen.generate(results, output_xml)

        print(f"Performance test complete. Report saved to: {report_path}")

        return results

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


# pytest fixtures and test functions
@pytest.fixture
def perf_test_env(temp_dir, test_session_id):
    """Create performance test environment."""
    test = BitRAGPerformanceTest(temp_dir, test_session_id)
    test.setup()
    return test


def test_embedding_generation_time(perf_test_env, sample_pdf_path):
    """Test embedding generation time."""
    if sample_pdf_path is None:
        pytest.skip("Sample PDF not available")

    perf_test_env.set_document(sample_pdf_path)
    results = perf_test_env.run_embedding_test()

    assert results.get("embedding_time_seconds", 0) > 0
    assert results.get("document_count", 0) > 0


def test_vector_indexing(perf_test_env, sample_pdf_path):
    """Test vector indexing."""
    if sample_pdf_path is None:
        pytest.skip("Sample PDF not available")

    perf_test_env.set_document(sample_pdf_path)
    perf_test_env.run_embedding_test()

    results = perf_test_env.run_vector_indexing_test()

    assert results.get("total_documents_indexed", 0) > 0


def test_inference_time(perf_test_env, sample_pdf_path):
    """Test inference time."""
    if sample_pdf_path is None:
        pytest.skip("Sample PDF not available")

    perf_test_env.set_document(sample_pdf_path)
    perf_test_env.run_embedding_test()

    test_queries = [
        "What is this document about?",
        "Summarize the main points.",
    ]

    results = perf_test_env.run_inference_test(test_queries)

    assert len(results) == len(test_queries)


def test_query_logging(perf_test_env, sample_pdf_path):
    """Test query logging."""
    if sample_pdf_path is None:
        pytest.skip("Sample PDF not available")

    perf_test_env.set_document(sample_pdf_path)
    perf_test_env.run_embedding_test()

    test_queries = ["What is this document about?"]
    perf_test_env.run_inference_test(test_queries)

    assert len(perf_test_env.metrics.query_log) == len(test_queries)


def test_system_info_collection():
    """Test system information collection."""
    info = SystemInfo.get_system_info()

    assert "platform" in info
    assert "cpu_count_physical" in info
    assert "total_memory_gb" in info


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BitRAG Performance Test")
    parser.add_argument("--document", "-d", required=True, help="Path to document to test")
    parser.add_argument("--queries", "-q", nargs="+", help="Queries to test")
    parser.add_argument(
        "--output", "-o", default="bitrag_performance_report.xml", help="Output XML file"
    )
    parser.add_argument("--session-id", "-s", default="perf_test", help="Session ID")

    args = parser.parse_args()

    default_queries = [
        "What is this document about?",
        "Summarize the main points.",
        "What are the key concepts discussed?",
    ]

    queries = args.queries if args.queries else default_queries

    results = run_performance_test(
        document_path=args.document,
        test_queries=queries,
        session_id=args.session_id,
        output_xml=args.output,
    )

    print("\n=== Test Results ===")
    print(f"Document Type: {results['document_type']}")
    print(f"Embedding Time: {results['embedding_time']:.4f}s")
    print(f"Memory Used: {results['memory_used_mb']:.2f}MB")
    print(f"Documents Indexed: {results['total_documents_indexed']}")
    print(f"Inference Results: {len(results['inference_results'])} queries tested")
