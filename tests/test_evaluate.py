"""Tests for the span-overlap retrieval metrics (Task 4)."""
import json

import pytest

from raghood.chunk import chunk_page, section_spans
from raghood.evaluate import evaluate_question, is_hit, summarise

PAGE = ("# Guide\n\n" + " ".join(f"g{i}" for i in range(120))
        + "\n\n## Sessions\n\n" + " ".join(f"s{i}" for i in range(220))
        + "\n\n## Cookies\n\n" + " ".join(f"c{i}" for i in range(120)))


@pytest.fixture
def fixture():
    texts = {"guide": PAGE}
    index = {("guide", title): (s0, s1, len(PAGE[s0:s1].split()))
             for s0, s1, title in section_spans(PAGE)}
    chunks = [{**c, "page": "guide", "id": i} for i, c in enumerate(chunk_page(PAGE, 200, 20))]
    return chunks, index, texts


def test_hit_requires_enough_shared_text(fixture):
    chunks, index, texts = fixture
    gold = [{"page": "guide", "section": "Sessions"}]
    # the chunk covering the bulk of Sessions is a hit; one that barely clips it is not
    hits = [is_hit(c, gold, index, texts) for c in chunks]
    assert any(h == "Sessions" for h in hits)
    assert not all(h for h in hits), "not every chunk should count as a hit"


def test_chunk_starting_in_another_section_still_hits(fixture):
    """The bug this rule exists for: judge by text overlap, not by the section label."""
    chunks, index, texts = fixture
    straddler = next(c for c in chunks if len(c["sections"]) > 1 and "Sessions" in c["sections"])
    assert is_hit(straddler, [{"page": "guide", "section": "Sessions"}], index, texts) == "Sessions"


def test_wrong_page_never_hits(fixture):
    chunks, index, texts = fixture
    other = {**chunks[0], "page": "elsewhere"}
    assert is_hit(other, [{"page": "guide", "section": "Sessions"}], index, texts) is None


def test_short_section_only_needs_most_of_itself(fixture):
    """A 10-word section can never share 50 words, so the fraction rule must apply."""
    text = "# Tiny\n\n" + " ".join(f"t{i}" for i in range(10)) + "\n\n## Rest\n\n" + " ".join(f"r{i}" for i in range(300))
    texts = {"p": text}
    index = {("p", t): (a, b, len(text[a:b].split())) for a, b, t in section_spans(text)}
    chunk = {**chunk_page(text, 200, 20)[0], "page": "p", "id": 0}
    assert is_hit(chunk, [{"page": "p", "section": "Tiny"}], index, texts) == "Tiny"


def test_unknown_gold_label_raises(fixture):
    chunks, index, texts = fixture
    with pytest.raises(KeyError):
        is_hit(chunks[0], [{"page": "guide", "section": "No Such Section"}], index, texts)


def test_metrics_on_a_known_ranking(fixture):
    chunks, index, texts = fixture
    gold = [{"page": "guide", "section": "Sessions"}]
    hit = next(c for c in chunks if is_hit(c, gold, index, texts))
    miss = {**chunks[0], "page": "elsewhere"}

    q = {"id": 1, "question": "q", "relevant": gold, "primary": gold[0]}

    row = evaluate_question(q, [hit, miss, miss], index, texts, ks=(1, 3))
    assert row["P@1"] == 1.0
    assert row["P@3"] == pytest.approx(1 / 3)
    assert row["MRR"] == 1.0
    assert row["first_hit_rank"] == 1

    row = evaluate_question(q, [miss, miss, hit], index, texts, ks=(1, 3))
    assert row["P@1"] == 0.0
    assert row["MRR"] == pytest.approx(1 / 3)
    assert row["first_hit_rank"] == 3

    row = evaluate_question(q, [miss, miss], index, texts, ks=(1, 3))
    assert row["MRR"] == 0.0 and row["first_hit_rank"] is None


def test_recall_counts_distinct_gold_sections(fixture):
    chunks, index, texts = fixture
    gold = [{"page": "guide", "section": "Sessions"}, {"page": "guide", "section": "Cookies"}]
    q = {"id": 1, "question": "q", "relevant": gold}
    s_hit = next(c for c in chunks if is_hit(c, [gold[0]], index, texts))
    row = evaluate_question(q, [s_hit, s_hit, s_hit], index, texts, ks=(3,))
    assert row["R@3"] == pytest.approx(0.5), "same section three times is still one of two"


def test_summarise_averages_and_counts_misses(fixture):
    rows = [{"P@1": 1.0, "R@1": 1.0, "MRR": 1.0, "first_hit_rank": 1},
            {"P@1": 0.0, "R@1": 0.0, "MRR": 0.0, "first_hit_rank": None}]
    out = summarise(rows, ks=(1,))
    assert out["P@1"] == 0.5 and out["MRR"] == 0.5
    assert out["n_questions"] == 2 and out["n_missed"] == 1
