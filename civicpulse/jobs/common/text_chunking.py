"""
Sentence-boundary-aware chunking shared by transform_bills.py and
transform_agendas.py. Deliberately dependency-free (no nltk/spacy download at
job time) — good enough for legislative/agenda prose, which is mostly plain
punctuation-terminated sentences.
"""

from __future__ import annotations

import re
from typing import List

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


def chunk_text(
    text: str,
    target_tokens: int = 500,
    overlap_tokens: int = 50,
) -> List[str]:
    """
    Greedy sentence-packing chunker. Approximates tokens as whitespace-split
    words (close enough for a ~400-600 token target; swap in a real tokenizer
    if the embedding model's exact token accounting matters later).
    """
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current and current_tokens + sentence_tokens > target_tokens:
            chunks.append(" ".join(current))
            # carry the tail of the previous chunk forward for overlap
            overlap: List[str] = []
            overlap_count = 0
            for s in reversed(current):
                overlap_count += len(s.split())
                overlap.insert(0, s)
                if overlap_count >= overlap_tokens:
                    break
            current = overlap[:]
            current_tokens = sum(len(s.split()) for s in current)

        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks
