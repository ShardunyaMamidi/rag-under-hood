"""Fixed-size sliding-window chunking (Task 1), parameterised for the Task 4 size sweep.

Words are counted but the *original* text is sliced, so a chunk keeps its newlines and
code indentation. Chunks never span two pages, so every chunk has exactly one source URL.

Derived and verified in `notebooks/chunking_embeddings.ipynb`.
"""
import json
import re
from pathlib import Path

WORD = re.compile(r"\S+")
HEADING = re.compile(r"#{1,6} (.+)")


def heading_positions(text: str) -> list[tuple[int, str]]:
    """[(char_offset, title)] for '#' headings outside code fences.

    Fences are skipped because a Python `# comment` is not a heading.
    """
    heads, in_fence, pos = [], False, 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and (m := HEADING.match(line)):
            heads.append((pos, m.group(1).strip()))
        pos += len(line)
    return heads


def chunk_page(text: str, size: int = 200, overlap: int = 20) -> list[dict]:
    """Split one page into windows of `size` words sharing `overlap` words with the next.

    If the final window would add fewer than `overlap` new words, it is folded into the
    previous chunk instead, so a page never ends in a tiny near-duplicate chunk (a chunk
    can therefore hold up to `size + overlap - 1` words).

    Returns dicts with the word range, character range, section title, n_words and text.
    """
    if overlap >= size:
        raise ValueError(f"overlap ({overlap}) must be smaller than size ({size})")

    words = list(WORD.finditer(text))
    n, step = len(words), size - overlap
    if n == 0:
        return []

    spans, start = [], 0
    while True:
        end = min(start + size, n)
        spans.append([start, end])
        if end == n:
            break
        start += step

    if len(spans) > 1 and spans[-1][1] - spans[-2][1] < overlap:
        spans[-2][1] = spans[-1][1]
        spans.pop()

    heads = heading_positions(text)
    chunks = []
    for s, e in spans:
        c0, c1 = words[s].start(), words[e - 1].end()
        section = next((title for pos, title in reversed(heads) if pos <= c0), None)
        chunks.append({"start_word": s, "end_word": e, "n_words": e - s,
                       "char_start": c0, "char_end": c1, "section": section, "text": text[c0:c1]})
    return chunks


def load_pages(processed_dir: Path) -> list[dict]:
    """Read the cleaned-page manifest written by the Task 1 notebook."""
    with open(Path(processed_dir) / "manifest.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def chunk_corpus(pages: list[dict], root: Path, size: int = 200, overlap: int = 20) -> list[dict]:
    """Chunk every page in a manifest. `id` is the row number in the embedding matrix."""
    chunks = []
    for page in pages:
        text = (Path(root) / page["path"]).read_text(encoding="utf-8")
        for k, c in enumerate(chunk_page(text, size, overlap)):
            chunks.append({"id": len(chunks), "page": page["page"], "url": page["url"],
                           "chunk_no": k, **c})
    return chunks
