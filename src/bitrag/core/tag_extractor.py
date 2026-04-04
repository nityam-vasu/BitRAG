"""
BitRAG Tag Extractor Module

Provides LLM-powered tag extraction for documents.
Features:
- Abstractive tag extraction using Ollama
- Keyword frequency fallback if LLM fails
- Returns 5-10 diverse tags
- JSON parsing with error handling
"""

import json
import re
from typing import List, Optional, Dict, Any, Set
from llama_index.llms.ollama import Ollama

from .config import get_config


# Default tag extraction prompt template
DEFAULT_TAG_PROMPT = """Extract 5-10 relevant tags from the following document.

Requirements:
- Tags should be: topics, subjects, named entities, key concepts, or themes
- Return ONLY a valid JSON array of strings, nothing else
- Each tag should be 1-3 words maximum
- Tags should be diverse and non-redundant
- Do not include generic words like "document", "file", "text"

Example output format:
["machine learning", "neural networks", "deep learning", "artificial intelligence"]

Document:
{document_text}

Tags (JSON array):"""


# Common words to filter out (beyond typical stopwords)
COMMON_WORDS: Set[str] = {
    "document",
    "file",
    "text",
    "page",
    "chapter",
    "section",
    "content",
    "information",
    "data",
    "number",
    "example",
    "figure",
    "table",
    "list",
    "item",
    "word",
    "term",
    "name",
    "case",
    "way",
    "thing",
    "point",
    "fact",
    "problem",
    "question",
    "answer",
    "result",
    "effect",
    "type",
    "kind",
    "form",
    "part",
    "type",
    "group",
    "class",
    "system",
    "method",
    "process",
    "level",
    "state",
    "case",
    "use",
    "based",
    "following",
    "above",
    "below",
    "shown",
    "described",
    "given",
    "also",
    "may",
    "well",
    "even",
    "new",
    "first",
    "last",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "however",
    "therefore",
    "thus",
    "hence",
    "since",
    "because",
    "through",
    "within",
    "between",
    "among",
    "while",
    "where",
    "when",
    "what",
    "which",
    "how",
    "why",
    "can",
    "will",
    "would",
    "should",
    "could",
    "must",
    "need",
    "make",
    "made",
}

# Stopwords for keyword extraction
STOPWORDS: Set[str] = {
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
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "used",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "me",
    "him",
    "her",
    "us",
    "them",
    "my",
    "your",
    "his",
    "our",
    "their",
    "mine",
    "yours",
    "hers",
    "ours",
    "theirs",
    "not",
    "no",
    "nor",
    "neither",
    "either",
    "both",
    "each",
    "all",
    "any",
    "some",
    "few",
    "more",
    "most",
    "other",
    "another",
    "such",
    "only",
    "own",
    "same",
    "than",
    "too",
    "very",
    "just",
}


class TagExtractor:
    """
    LLM-powered document tag extractor.

    Features:
    - Uses Ollama for abstractive tag extraction
    - Falls back to keyword frequency if LLM fails
    - Returns 5-10 diverse tags
    - JSON parsing with robust error handling

    Usage:
        extractor = TagExtractor()
        tags = extractor.extract_tags("Long document text...")
        # Returns: ["machine learning", "neural networks", ...]
    """

    def __init__(
        self,
        model: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        min_tags: int = 5,
        max_tags: int = 10,
        timeout: int = 30,
    ):
        """
        Initialize the tag extractor.

        Args:
            model: Ollama model name (default: from config)
            ollama_base_url: Ollama server URL (default: from config)
            min_tags: Minimum number of tags to return
            max_tags: Maximum number of tags to return
            timeout: LLM call timeout in seconds
        """
        config = get_config()

        self.model = model or config.default_model
        self.ollama_base_url = ollama_base_url or config.ollama_base_url
        self.min_tags = min_tags
        self.max_tags = max_tags
        self.timeout = timeout
        self.truncation_length = 3000  # Truncate input

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

    def extract_tags(self, text: str) -> List[str]:
        """
        Extract 5-10 relevant tags from the text.

        Args:
            text: Document text to extract tags from

        Returns:
            List of tag strings
        """
        if not text or not text.strip():
            return []

        # Truncate text if too long
        truncated_text = self._truncate_text(text)

        # Try LLM-based extraction first
        try:
            tags = self._extract_llm_tags(truncated_text)
            if tags and len(tags) >= self.min_tags:
                return tags[: self.max_tags]
        except Exception as e:
            print(f"[TagExtractor] LLM extraction failed: {e}")

        # Fallback to keyword frequency
        return self._extract_keyword_tags(text)

    def _truncate_text(self, text: str) -> str:
        """Truncate text to prevent LLM timeout."""
        if len(text) > self.truncation_length:
            return text[: self.truncation_length]
        return text

    def _extract_llm_tags(self, text: str) -> Optional[List[str]]:
        """
        Extract tags using LLM.

        Returns:
            List of tags or None if failed
        """
        prompt = DEFAULT_TAG_PROMPT.format(document_text=text)

        response = self.llm.complete(prompt)

        if not response or not response.text:
            return None

        # Parse JSON response
        tags = self._parse_json_response(response.text)

        if tags:
            print(f"[TagExtractor] LLM extracted {len(tags)} tags")

        return tags

    def _parse_json_response(self, text: str) -> Optional[List[str]]:
        """
        Parse JSON array from LLM response.

        Handles various formats and errors.
        """
        # Clean up the response
        text = text.strip()

        # Try direct JSON parsing first
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [self._clean_tag(t) for t in parsed if self._is_valid_tag(t)]
        except json.JSONDecodeError:
            pass

        # Try to extract JSON array from text
        # Look for [...] pattern
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    return [self._clean_tag(t) for t in parsed if self._is_valid_tag(t)]
            except json.JSONDecodeError:
                pass

        # Try to parse each line as a tag
        lines = text.strip().split("\n")
        tags = []
        for line in lines:
            line = line.strip()
            # Remove quotes and common prefixes
            line = re.sub(r"^[\d\.\-\*]+\s*", "", line)  # Remove "1. ", "- ", etc.
            line = line.strip("\",'[]")
            if self._is_valid_tag(line):
                tags.append(self._clean_tag(line))

        if tags:
            return tags

        return None

    def _clean_tag(self, tag: str) -> str:
        """Clean and normalize a tag string."""
        # Remove extra whitespace
        tag = " ".join(tag.split())

        # Remove leading/trailing punctuation
        tag = tag.strip(".,;:!?'\"()[]{}")

        # Lowercase for consistency (optional - comment out to preserve casing)
        # tag = tag.lower()

        return tag

    def _is_valid_tag(self, tag: str) -> bool:
        """Check if a tag is valid."""
        if not tag:
            return False

        tag = tag.strip()

        # Must be at least 2 characters
        if len(tag) < 2:
            return False

        # Must not be too long (max 50 chars)
        if len(tag) > 50:
            return False

        # Must not be entirely numbers
        if tag.isdigit():
            return False

        # Must not be a common word
        if tag.lower() in COMMON_WORDS or tag.lower() in STOPWORDS:
            return False

        return True

    def _extract_keyword_tags(self, text: str) -> List[str]:
        """
        Extract tags using keyword frequency (fallback method).

        Returns top keywords sorted by frequency.
        """
        # Clean and tokenize
        words = text.lower().split()

        # Count frequencies
        word_freq: Dict[str, int] = {}
        for word in words:
            # Clean word
            clean_word = word.strip(".,!?;:()\"'[]{}")

            # Validate
            if (
                len(clean_word) >= 3
                and clean_word.isalpha()
                and clean_word not in STOPWORDS
                and clean_word not in COMMON_WORDS
            ):
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Take top tags
        tags = [word for word, _ in sorted_words[: self.max_tags]]

        print(f"[TagExtractor] Keyword extraction found {len(tags)} tags")

        return tags

    def set_model(self, model: str) -> None:
        """Change the LLM model."""
        self.model = model
        self._llm = None  # Reset LLM

    def get_info(self) -> Dict[str, Any]:
        """Get extractor info."""
        return {
            "model": self.model,
            "ollama_base_url": self.ollama_base_url,
            "min_tags": self.min_tags,
            "max_tags": self.max_tags,
            "timeout": self.timeout,
        }


# Global instance (lazy)
_tag_extractor: Optional[TagExtractor] = None


def get_tag_extractor(
    model: Optional[str] = None, ollama_base_url: Optional[str] = None, **kwargs
) -> TagExtractor:
    """
    Get or create the global TagExtractor instance.

    Args:
        model: Override default model
        ollama_base_url: Override Ollama URL
        **kwargs: Additional arguments for TagExtractor

    Returns:
        TagExtractor instance
    """
    global _tag_extractor

    if _tag_extractor is None:
        _tag_extractor = TagExtractor(model=model, ollama_base_url=ollama_base_url, **kwargs)

    return _tag_extractor


def reset_tag_extractor() -> None:
    """Reset the global extractor instance."""
    global _tag_extractor
    _tag_extractor = None
