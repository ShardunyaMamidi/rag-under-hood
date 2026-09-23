# Project Plan — `rag-under-hood` (MTech PMI Project 6: Vector Search & RAG)

## Context
Course project 6 from `D:\woxsen\mtech_pmi_course_projects_260923_204641.pdf`: build a RAG pipeline
from scratch with plain matrix ops, then benchmark it against FAISS/ChromaDB and wire it to a small
open-weights LLM. Deliverables across the course: 3 presentations, final report, GitHub repo,
GitHub.io demo page, visualizations. Task 3 theory (MiniLM, contrastive loss, HNSW/IVF) is also
examined separately (5 marks), so the report doubles as exam prep.

This deliverable is a **plan only** — no code yet. Project root: `D:\Coding Stuff\rag-under-hood` (created, empty).

## Decisions
- **Corpus:** Flask documentation (fits the brief's "course documentation files" option).
  - Scrape via **Jina Reader** (`https://r.jina.ai/<url>`) → clean Markdown per page.
  - **Pin a version** (e.g. `https://flask.palletsprojects.com/en/3.1.x/`) so the corpus is reproducible.
  - Discover URLs by crawling the docs index/toctree (same-prefix links only), ~40–60 pages.
  - Free tier without key is rate-limited (~20 req/min) → throttle + cache raw pages to disk; scrape once.
  - Fallback if Jina is flaky: the same docs exist as `.rst` in the `pallets/flask` repo `docs/` folder.
  - Watch-out: `api.html` is huge and will dominate chunk counts — keep it but tag it, and note it in analysis.
- **Hardware:** RTX 3050 Laptop, **4 GB VRAM**.
  - Embeddings (MiniLM, 22M params) — trivial on GPU.
  - LLM: `Qwen2.5-1.5B-Instruct` in fp16 (~3.1 GB) is tight; plan for **4-bit (bitsandbytes)** or
    fall back to `Llama-3.2-1B-Instruct` fp16 (~2.5 GB). Keep context ≤ ~2k tokens (top-3 chunks).
- **Env:** Python 3.14 is installed but ML wheels (faiss, bitsandbytes) lag → use **uv with Python 3.12** venv, CUDA torch.
- **Structure:** reusable package + one notebook per task.

## Repo layout
```
rag-under-hood/
  pyproject.toml / requirements.txt
  src/raghood/
    scrape.py      # Jina Reader crawl -> data/raw/*.md + manifest.jsonl (url, title, section)
    chunk.py       # fixed-size word chunking w/ overlap; chunk records keep source url + offsets
    embed.py       # sentence-transformers wrapper -> np.ndarray (N, 384), saved as .npy
    search.py      # manual cosine: normalize + matmul, top-k via argpartition  (Task 2)
    lexical.py     # BM25 from scratch (+ rank_bm25 as sanity check)          (Task 4)
    hybrid.py      # score fusion (weighted / RRF)                               (Task 4)
    rerank.py      # cross-encoder re-ranking (ms-marco-MiniLM-L-6-v2)         (Task 4)
    evaluate.py    # Precision@k, Recall@k, MRR over eval set                   (Task 4)
    index_ext.py   # FAISS (Flat, IVF, HNSW) + ChromaDB adapters                 (Task 5)
    generate.py    # prompt builder w/ numbered citations + HF LLM generation    (Task 5)
  notebooks/
    01_chunking_embeddings.ipynb
    02_manual_retrieval.ipynb
    04_retrieval_experiments.ipynb
    05_framework_benchmark_rag.ipynb
  data/ raw/ processed/ eval/questions.jsonl   (raw + embeddings gitignored)
  reports/ task3_architecture.md, final_report.md, figures/
  docs/  -> GitHub.io demo page
```

## Task-by-task plan
**Task 1 — Chunking & embeddings**
- Scrape → clean Markdown (strip nav/footer). Chunk 200 words / 20 overlap; keep code blocks intact where possible.
- Embed with `all-MiniLM-L6-v2` → verify shape `(N, 384)`, dtype, L2 norms.
- Deliverables: chunk stats table (pages, chunks, words/chunk histogram), shape assertion output.

**Task 2 — Manual retrieval engine**
- `cosine(q, D) = (D @ q) / (‖D‖·‖q‖)`; pre-normalize D once so search = single matmul. Implement in both NumPy and torch.
- Verify against `sklearn.metrics.pairwise.cosine_similarity` (numerical parity check).
- Deliverables: top-3 results for 3 queries (e.g. "How do I register a blueprint?", "What is the application context?", "How to handle file uploads?").

**Task 3 — Theory report** (`reports/task3_architecture.md`)
- MiniLM-L6: 6-layer BERT-style encoder, mean pooling with attention mask → 384-d, normalization.
- Contrastive training: InfoNCE / Multiple Negatives Ranking Loss with in-batch negatives, temperature.
- ANN: IVF (k-means coarse quantizer, `nprobe`), HNSW (layered graph, greedy descent, `M`/`efSearch`), vs exact O(N·d).
- Diagrams + equations; cross-reference with our Task 5 empirical numbers.

**Task 4 — Retrieval experiments** (do all three; two are required)
- Build **10+ eval questions** with gold chunk/page labels (hand-written from Flask docs; label at page+section level so labels survive re-chunking).
- Experiments: chunk size 100/300/500; hybrid BM25+dense (Flask identifiers like `url_for`, `g`, `app.teardown_appcontext` favor lexical); cross-encoder re-rank of top-20.
- Deliverables: Precision@k (k=1,3,5) table: naive vs each variant vs combined.

**Task 5 — Framework comparison + RAG**
- Same chunks into FAISS (IndexFlatIP, IVF, HNSW) and ChromaDB.
- Latency benchmark at N = 100 / 1,000 / 5,000 (pad with dummy/synthetic chunks since Flask yields ~1k), warm runs, median + p95 over many queries; CPU vs GPU matmul for the custom engine.
- RAG: top-k contexts → numbered `[1] [2]` sources in prompt → Qwen2.5-1.5B answers with citations mapped back to doc URLs.
- Deliverables: corpus size vs latency plot, sample answers with highlighted citations.

**Demo page (GitHub.io)**
- Static page in `docs/`: project overview, figures, benchmark tables, and pre-computed Q&A examples (no live LLM hosting).

## Suggested milestones (align with 3 presentations)
1. **Presentation 1:** Tasks 1–2 working + corpus stats + manual search demo.
2. **Presentation 2:** Task 3 report draft + Task 4 experiments and P@k table.
3. **Presentation 3:** Task 5 benchmarks + RAG demo + demo page; final report.

## Verification
- `pytest` unit tests: chunk overlap correctness, cosine parity vs sklearn, BM25 vs `rank_bm25`, P@k on a toy example.
- Notebooks run top-to-bottom from a clean venv (`uv sync` → run all).
- `torch.cuda.is_available()` and peak VRAM logged before LLM step.
