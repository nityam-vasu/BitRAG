"""
BitRAG Summary Generator Module

Provides LLM-powered summary generation for documents.
Features:
- Abstractive summarization using Ollama
- Extractive fallback if LLM fails
- Configurable summary length
- Timeout handling
"""

import time
from typing import Optional, Dict, Any
from llama_index.llms.ollama import Ollama
from llama_index.core import PromptTemplate

from .config import get_config


# Default summary prompt template
DEFAULT_SUMMARY_PROMPT = """You are a document summarization assistant. Provide a brief summary of the document.

Requirements:
- 2-3 sentences maximum
- Focus on the main topic and key points
- Be concise and clear
- Do not add preamble like "This document is about..."

Document:
{document_text}

Summary:"""


class SummaryGenerator:
    """
    LLM-powered document summary generator.

    Features:
    - Uses Ollama for abstractive summarization
    - Falls back to extractive (first N chars) if LLM fails
    - Configurable max length and truncation
    - Timeout handling for LLM calls

    Usage:
        generator = SummaryGenerator()
        summary = generator.generate("Long document text...")
    """

    def __init__(
        self,
        model: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        max_length: int = 200,
        timeout: int = 30,
    ):
        """
        Initialize the summary generator.

        Args:
            model: Ollama model name (default: from config)
            ollama_base_url: Ollama server URL (default: from config)
            max_length: Maximum summary length in characters
            timeout: LLM call timeout in seconds
        """
        config = get_config()

        self.model = model or config.default_model
        self.ollama_base_url = ollama_base_url or config.ollama_base_url
        self.max_length = max_length
        self.timeout = timeout
        self.truncation_length = 3000  # Truncate input to this many chars

        # Initialize LLM lazily
        self._llm: Optional[Ollama] = None

    @property
    def llm(self) -> Ollama:
        """Lazy initialization of LLM."""
        if self._llm is None:
            self._llm = Ollama(
                model=self.model,
                base_url=self.ollama_base_url,
                temperature=0.1,
                request_timeout=self.timeout,
            )
        return self._llm

    def generate(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate a summary for the given text.

        Args:
            text: Document text to summarize
            max_length: Override max summary length (uses default if None)

        Returns:
            Generated summary string
        """
        if not text or not text.strip():
            return ""

        # Truncate text if too long
        truncated_text = self._truncate_text(text)

        # Try LLM-based summary first
        try:
            summary = self._generate_llm_summary(truncated_text)
            if summary:
                return self._truncate_summary(summary, max_length)
        except Exception as e:
            print(f"[SummaryGenerator] LLM summary failed: {e}")

        # Fallback to extractive summary
        return self._generate_extractive_summary(text, max_length)

    def _truncate_text(self, text: str) -> str:
        """Truncate text to prevent LLM timeout."""
        if len(text) > self.truncation_length:
            return text[: self.truncation_length]
        return text

    def _generate_llm_summary(self, text: str) -> Optional[str]:
        """
        Generate summary using LLM.

        Returns:
            Summary string or None if failed
        """
        prompt = DEFAULT_SUMMARY_PROMPT.format(document_text=text)

        start_time = time.time()
        response = self.llm.complete(prompt)
        elapsed = time.time() - start_time

        print(f"[SummaryGenerator] LLM summary generated in {elapsed:.1f}s")

        if response and response.text:
            return response.text.strip()

        return None

    def _generate_extractive_summary(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate extractive summary (first N characters).

        This is a fallback when LLM summarization fails.

        Args:
            text: Document text
            max_length: Maximum length

        Returns:
            First N characters of text
        """
        length = max_length or self.max_length

        # Clean up the text
        clean_text = text.replace("\n", " ").replace("\r", " ").strip()

        if len(clean_text) <= length:
            return clean_text

        # Try to end at a sentence boundary
        truncated = clean_text[:length]
        last_period = truncated.rfind(".")

        if last_period > length * 0.5:  # If period is in last half
            return truncated[: last_period + 1]

        # Otherwise, cut at last space
        last_space = truncated.rfind(" ")
        if last_space > 0:
            return truncated[:last_space] + "..."

        return truncated + "..."

    def _truncate_summary(self, summary: str, max_length: Optional[int] = None) -> str:
        """Truncate summary to max length."""
        length = max_length or self.max_length

        if len(summary) <= length:
            return summary

        truncated = summary[:length]
        last_space = truncated.rfind(" ")

        if last_space > length * 0.7:
            return truncated[:last_space] + "..."

        return truncated + "..."

    def set_model(self, model: str) -> None:
        """Change the LLM model."""
        self.model = model
        self._llm = None  # Reset LLM to use new model

    def get_info(self) -> Dict[str, Any]:
        """Get generator info."""
        return {
            "model": self.model,
            "ollama_base_url": self.ollama_base_url,
            "max_length": self.max_length,
            "timeout": self.timeout,
            "truncation_length": self.truncation_length,
        }


# Global instance (lazy)
_summary_generator: Optional[SummaryGenerator] = None


def get_summary_generator(
    model: Optional[str] = None, ollama_base_url: Optional[str] = None, **kwargs
) -> SummaryGenerator:
    """
    Get or create the global SummaryGenerator instance.

    Args:
        model: Override default model
        ollama_base_url: Override Ollama URL
        **kwargs: Additional arguments for SummaryGenerator

    Returns:
        SummaryGenerator instance
    """
    global _summary_generator

    if _summary_generator is None:
        _summary_generator = SummaryGenerator(
            model=model, ollama_base_url=ollama_base_url, **kwargs
        )

    return _summary_generator


def reset_summary_generator() -> None:
    """Reset the global generator instance."""
    global _summary_generator
    _summary_generator = None
