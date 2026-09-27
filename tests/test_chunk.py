"""Tests for the sliding-window chunker (Task 1).

These are the invariants the Task 1 notebook asserts over the real corpus, pinned here on
small synthetic inputs so the Task 4 size sweep cannot break them unnoticed.
"""
import pytest

from raghood.chunk import chunk_page, heading_positions

WORDS = " ".join(f"w{i}" for i in range(1000))


def words_of(chunk):
    return chunk["text"].split()


def test_single_chunk_when_page_is_short():
    chunks = chunk_page("one two three", size=200, overlap=20)
    assert len(chunks) == 1
    assert chunks[0]["n_words"] == 3
    assert chunks[0]["text"] == "one two three"


def test_empty_page_yields_nothing():
    assert chunk_page("", size=200, overlap=20) == []
    assert chunk_page("   \n\n  ", size=200, overlap=20) == []


def test_window_size_and_step():
    chunks = chunk_page(WORDS, size=200, overlap=20)
    assert chunks[0]["start_word"] == 0
    assert all(c["n_words"] >= 200 for c in chunks[:-1])
    for a, b in zip(chunks, chunks[1:]):
        assert b["start_word"] == a["end_word"] - 20      # step = size - overlap


def test_neighbours_share_exactly_overlap_words():
    for size, overlap in [(200, 20), (100, 20), (50, 5), (300, 50)]:
        chunks = chunk_page(WORDS, size=size, overlap=overlap)
        for a, b in zip(chunks, chunks[1:]):
            assert words_of(a)[-overlap:] == words_of(b)[:overlap], (size, overlap)


def test_every_word_is_covered():
    for size, overlap in [(200, 20), (100, 20), (37, 7)]:
        chunks = chunk_page(WORDS, size=size, overlap=overlap)
        assert chunks[0]["start_word"] == 0
        assert chunks[-1]["end_word"] == 1000
        for a, b in zip(chunks, chunks[1:]):
            assert b["start_word"] < a["end_word"], "gap between chunks"


def test_no_tiny_tail_chunk():
    """A page of 385 words would naively end in a 25-word chunk, 20 of them repeated."""
    text = " ".join(f"w{i}" for i in range(385))
    chunks = chunk_page(text, size=200, overlap=20)
    assert len(chunks) == 2
    assert chunks[-1]["n_words"] >= 2 * 20
    assert all(c["n_words"] <= 200 + 20 - 1 for c in chunks)


def test_original_whitespace_is_preserved():
    """Chunks are sliced from the source, not rebuilt by joining words."""
    text = "# Title\n\n```python\ndef f():\n    return 1\n```\n\nprose here\n"
    chunk = chunk_page(text, size=200, overlap=20)[0]
    assert "\n    return 1" in chunk["text"], "code indentation was flattened"


def test_section_label_is_nearest_heading_above():
    text = "# First\n\n" + " ".join(f"a{i}" for i in range(250)) + "\n\n## Second\n\n" + " ".join(f"b{i}" for i in range(250))
    chunks = chunk_page(text, size=200, overlap=20)
    assert chunks[0]["section"] == "First"
    assert chunks[-1]["section"] == "Second"


def test_headings_inside_code_fences_are_ignored():
    text = "# Real\n\n```python\n# not a heading\n```\n\n" + " ".join(f"w{i}" for i in range(50))
    assert heading_positions(text) == [(0, "Real")]
    assert chunk_page(text)[0]["section"] == "Real"


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_page(WORDS, size=100, overlap=100)
