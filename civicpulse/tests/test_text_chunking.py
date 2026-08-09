"""Unit tests for the shared sentence-aware chunker."""

import sys

sys.path.append("..")
from jobs.common.text_chunking import chunk_text, split_sentences


def test_split_sentences_basic():
    text = "This is one sentence. This is another! And a third?"
    assert split_sentences(text) == [
        "This is one sentence.",
        "This is another!",
        "And a third?",
    ]


def test_chunk_text_respects_target_size_roughly():
    long_text = " ".join([f"Sentence number {i}." for i in range(200)])
    chunks = chunk_text(long_text, target_tokens=50, overlap_tokens=10)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 80 for c in chunks)  # allows slack for overlap + last sentence


def test_chunk_text_empty_input():
    assert chunk_text("") == []
