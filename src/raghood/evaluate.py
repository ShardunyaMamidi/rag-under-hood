"""Retrieval metrics for the Task 4 experiments.

A question's gold answer is recorded as `(page, section)` pairs, but a retrieved chunk is
**not** judged by comparing section names. Fixed-size windows straddle heading boundaries
constantly (~69% of chunks at size 200), so a chunk can be mostly about section B while
starting in section A. Comparing names would then score a correct retrieval as a miss.

Instead a gold section is treated as a **character span** of its page, and a chunk counts
as a hit when its own span overlaps that range by enough words to actually contain answer
text. That is independent of chunk size, which is what the 100/150/200/300/500 sweep needs.
"""
import json
from pathlib import Path

from .chunk import overlap_words, section_spans

MIN_OVERLAP_WORDS = 50   # enough text to plausibly contain the answer
MIN_SECTION_FRAC = 0.8   # ...but a section shorter than that only needs most of itself


def load_questions(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build_section_index(pages: list[dict], root: Path) -> dict[tuple[str, str], tuple[int, int, int]]:
    """{(page, section): (char_start, char_end, n_words)} for every heading in the corpus."""
    index = {}
    for page in pages:
        text = (Path(root) / page["path"]).read_text(encoding="utf-8")
        for s0, s1, title in section_spans(text):
            index[(page["page"], title)] = (s0, s1, overlap_words(text, s0, s1, s0, s1))
    return index


def build_page_texts(pages: list[dict], root: Path) -> dict[str, str]:
    return {p["page"]: (Path(root) / p["path"]).read_text(encoding="utf-8") for p in pages}


def is_hit(chunk: dict, gold: list[dict], section_index: dict, page_texts: dict[str, str],
           min_words: int = MIN_OVERLAP_WORDS) -> str | None:
    """Return the gold section this chunk satisfies, or None.

    A chunk qualifies when it shares at least `min_words` with the gold section -- or, for
    a section shorter than that, at least `MIN_SECTION_FRAC` of the whole section.
    """
    for g in gold:
        if g["page"] != chunk["page"]:
            continue
        span = section_index.get((g["page"], g["section"]))
        if span is None:
            raise KeyError(f"unknown gold label: {g['page']} > {g['section']}")
        s0, s1, sec_words = span
        shared = overlap_words(page_texts[chunk["page"]], chunk["char_start"], chunk["char_end"], s0, s1)
        if shared >= min(min_words, int(MIN_SECTION_FRAC * sec_words) or 1):
            return g["section"]
    return None


def evaluate_question(question: dict, retrieved: list[dict], section_index: dict,
                      page_texts: dict[str, str], ks=(1, 3, 5), min_words: int = MIN_OVERLAP_WORDS) -> dict:
    """Metrics for one question given its ranked chunks (best first)."""
    gold = question["relevant"]
    hits = [is_hit(c, gold, section_index, page_texts, min_words) for c in retrieved]

    row = {"id": question["id"], "question": question["question"],
           "type": question.get("type"), "difficulty": question.get("difficulty")}
    for k in ks:
        row[f"P@{k}"] = sum(h is not None for h in hits[:k]) / k
        row[f"R@{k}"] = len({h for h in hits[:k] if h}) / len({g["section"] for g in gold})
    first = next((i for i, h in enumerate(hits) if h), None)
    row["MRR"] = 1.0 / (first + 1) if first is not None else 0.0
    row["first_hit_rank"] = first + 1 if first is not None else None

    # stricter variant: did we get the one section a reader most wants?
    primary = [question["primary"]] if "primary" in question else []
    if primary:
        p_hits = [is_hit(c, primary, section_index, page_texts, min_words) for c in retrieved]
        row["primary@1"] = float(bool(p_hits[:1] and p_hits[0]))
        row["primary@3"] = float(any(p_hits[:3]))
    return row


def evaluate_all(questions: list[dict], retrieve, section_index: dict, page_texts: dict[str, str],
                 k: int = 5, ks=(1, 3, 5), min_words: int = MIN_OVERLAP_WORDS) -> list[dict]:
    """`retrieve(question_text, k)` must return ranked chunk dicts, best first."""
    return [evaluate_question(q, retrieve(q["question"], k), section_index, page_texts, ks, min_words)
            for q in questions]


def summarise(rows: list[dict], ks=(1, 3, 5)) -> dict:
    """Mean of each metric over all questions."""
    keys = [f"P@{k}" for k in ks] + [f"R@{k}" for k in ks] + ["MRR"]
    keys += [c for c in ("primary@1", "primary@3") if c in rows[0]]
    out = {key: sum(r[key] for r in rows) / len(rows) for key in keys}
    out["n_questions"] = len(rows)
    out["n_missed"] = sum(1 for r in rows if r["first_hit_rank"] is None)
    return out
