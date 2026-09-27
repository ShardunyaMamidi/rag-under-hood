# Project Plan — `rag-under-hood` (MTech PMI Project 6: Vector Search & RAG)

## Context
Course project 6 from `mtech_pmi_course_projects.pdf`: build a RAG pipeline from scratch with plain matrix
ops, then benchmark it against FAISS/ChromaDB and wire it to an open-weights LLM. Deliverables across the
course: 3 presentations, final report, GitHub repo, GitHub.io demo page, visualizations. Task 3 theory
(MiniLM, contrastive loss, HNSW/IVF) is also examined separately (5 marks), so that report doubles as exam prep.

## Status
| Task | State | Where |
|---|---|---|
| 1 — Chunking & embeddings | **done** | `notebooks/chunking_embeddings.ipynb` |
| 2 — Manual cosine retrieval | **done** | `notebooks/manual_retrieval.ipynb`, `src/raghood/search.py` |
| Eval question set | **next** | `data/eval/questions.jsonl` |
| 4 — Retrieval experiments | blocked on eval set | — |
| 3 — Theory report | not started (independent of code) | `reports/task3_architecture.md` |
| 5 — Frameworks + RAG | not started | — |

## Corpus
Flask documentation, pinned to repo tag **3.1.0** for reproducibility.

- **Not scraped from the website.** `flask.palletsprojects.com` sits behind Cloudflare and serves Jina Reader
  a bot-check page. `scrape.py` instead downloads one tarball of the `pallets/flask` repo and reads
  `docs/*.rst` (~1.3 s; per-file `raw.githubusercontent.com` requests took ~20 s each).
- **71 pages / 59,570 raw words**, 4 stub pages under 200 bytes skipped. Cleaning to prose leaves 58,425 words.
- At 200 words / 20 overlap: **344 chunks**, median 3 per page, `quickstart` the largest at 24.
- `api.rst` is mostly `.. autoclass::` directives whose content lives in source docstrings, not the `.rst`, so
  those sections survive cleaning as bare headings. Left as-is: harmless for generation, and noted in analysis.

## Environment
- **uv with Python 3.12** (3.14 is installed but faiss/bitsandbytes wheels lag), CUDA torch.
- **RTX 3050 Laptop, 4 GB VRAM.** MiniLM (22M params) is trivial; the Task 5 LLM is the only tight fit.
- **LLM for Task 5:** the brief says "open-weights LLM (e.g. Qwen-1.5B or Llama-3.2-1B)" — it requires open
  *weights*, not local execution. Plan for an **open-weights model over an OpenAI-compatible API** (Groq,
  Together, OpenRouter, HF Inference), with `generate.py` written against any such endpoint so a local
  4-bit Qwen2.5-1.5B can be swapped in. *Confirm with the instructor that an API is acceptable.*

## Repo layout
```
rag-under-hood/
  src/raghood/
    scrape.py      # GitHub tarball -> data/raw/*.rst + manifest.jsonl          DONE
    clean.py       # RST -> prose/Markdown (headings, code fences, roles)        DONE
    chunk.py       # sliding window, size/overlap parameterised                  DONE
    embed.py       # MiniLM wrapper -> (N, 384) float32, + token_stats           DONE
    search.py      # manual cosine (numpy + torch), top-k via argpartition       DONE
    lexical.py     # BM25 from scratch (+ rank_bm25 as oracle)                   Task 4
    hybrid.py      # score fusion (weighted / RRF)                               Task 4
    rerank.py      # cross-encoder re-ranking (ms-marco-MiniLM-L-6-v2)           Task 4
    evaluate.py    # Precision@k, Recall@k, MRR over the eval set                Task 4
    index_ext.py   # FAISS (Flat, IVF, HNSW) + ChromaDB adapters                 Task 5
    generate.py    # prompt builder w/ numbered citations + LLM call             Task 5
  notebooks/
    chunking_embeddings.ipynb     retrieval_experiments.ipynb
    manual_retrieval.ipynb        framework_benchmark_rag.ipynb
  tests/           # 31 passing: clean rules, chunk invariants, cosine vs sklearn
  data/ raw/ processed/ eval/questions.jsonl     (raw + processed + .npy gitignored)
  reports/ task3_architecture.md, final_report.md, figures/
  docs/  -> GitHub.io demo page
```

## Findings so far (carry into the report)
1. **86% of 200-word chunks are truncated by the encoder.** MiniLM stops at 256 tokens; Flask docs run ~1.8
   WordPiece tokens/word, so a 200-word chunk is a median 324-token chunk. The text is still returned to the
   LLM, but its tail contributed nothing to the vector that decided retrieval. Measured by size:

   | words | chunks | median tokens | truncated |
   |---|---|---|---|
   | 100 | 728 | 166 | 8% |
   | 150 | 467 | 245 | 43% |
   | 200 | 344 | 324 | 86% |
   | 300 | 233 | 485 | 89% |
   | 500 | 153 | 772 | 90% |

   Note `256 / 1.8 ≈ 143 words` is *not* a safe size: that uses the mean, and the distribution has a long
   right tail from code-dense chunks.
2. **Cosine == dot product on this corpus.** `all-MiniLM-L6-v2` ends with a `Normalize` module, so every
   vector has norm exactly 1. Hence one matmul per query, and `IndexFlatIP` is the correct FAISS baseline.
3. **Embedding the query costs ~70x more than searching all 344 chunks** (4.7 ms vs 0.068 ms). Any "our search
   is fast" claim in Task 5 must be read against that fixed cost.
4. **The GPU is slower than NumPy at N=344** (0.088 vs 0.068 ms) — kernel-launch overhead dominates. Task 5's
   N = 100/1000/5000 sweep should show the crossover explicitly.
5. **Good hits only score 0.4–0.57.** MiniLM was trained on *symmetric* sentence pairs but retrieval is
   asymmetric (7-word question vs 200-word passage), so only the ordering is meaningful and a fixed score
   threshold would reject every correct answer.
6. **25% of chunks cut a code block in half** — the baseline cost of pure fixed-size chunking.

## Next: evaluation set (`data/eval/questions.jsonl`)
The measuring instrument for all of Task 4, so it comes before the experiments.

- **20–25 questions** (brief asks for 10; more because with 71 pages one question flipping moves P@3 by 10 points).
- **Label by `page` + `section`, never by chunk id** — ids change the moment chunk size changes, and the whole
  Task 4 sweep depends on labels surviving re-chunking.
- Draft candidates from the corpus's page/section structure **without running search first**, so the question
  set is not unconsciously selected to flatter the current pipeline. Then review and cut.
- Include a deliberate mix: conceptual ("what is the application context"), identifier-led ("what does
  `url_for` do") to give BM25 something to win on, and multi-hop where the answer spans two pages.

## Task 4 — Retrieval experiments
All three enhancements (two are required):

1. **Chunk-size sweep: 100 / 150 / 200 / 300 / 500 words.** The brief names 100/300/500; 150 and 200 are added
   to cover the region where truncation actually changes. Hypothesis from finding 1: 300 and 500 cannot improve
   retrieval because ~90% of those chunks are partly invisible to the encoder. If they *don't* degrade, that
   itself needs explaining (the first 256 tokens may simply be enough).
   - **Report P@k two ways:** at equal k, and at an equal retrieved-word budget (top-3 at 200 words ≈ top-6 at
     100 words). Otherwise smaller chunks are judged on half the context.
2. **Hybrid search** — BM25 from scratch, fused with dense scores (weighted sum and RRF). Flask identifiers
   (`url_for`, `g`, `teardown_appcontext`) are exactly what lexical matching should win on.
3. **Cross-encoder re-ranking** of the top ~20. Concrete target: "How do I register a blueprint?" currently
   ranks `tutorial/views` above the dedicated `blueprints > Registering Blueprints` section.

Deliverables: Precision@k (k=1,3,5) table — naive vs each variant vs combined — plus MRR and Recall@k.

## Task 3 — Theory report (`reports/task3_architecture.md`)
- **Sentence Transformer architecture:** 6-layer BERT encoder → mean pooling with attention mask → 384-d →
  L2 normalisation. Why mean pooling over `[CLS]`, and what the 3-module pipeline means in practice.
- **Contrastive pre-training:** InfoNCE / Multiple Negatives Ranking Loss, in-batch negatives, temperature.
  Ties to finding 5 (symmetric training vs asymmetric use).
- **ANN indexing:** IVF (k-means coarse quantiser, `nprobe`) and HNSW (layered graph, greedy descent, `M` /
  `efSearch`), sub-linear vs exact O(N·d). Cross-reference the Task 5 measurements.
- Diagrams and equations; written to double as prep for the 5-mark reference-model test.

## Task 5 — Framework comparison + RAG
- Same chunks into FAISS (`IndexFlatIP`, IVF, HNSW) and ChromaDB.
- **Latency at N = 100 / 1,000 / 5,000.** The real corpus is only 344 chunks, so 1,000 and 5,000 need synthetic
  padding — state that plainly and keep the *real* 344-chunk numbers separate from the padded ones.
- Warm runs, median + p95 over many queries; custom NumPy vs torch-GPU vs FAISS vs Chroma on the same axis.
- RAG: top-k contexts → numbered `[1] [2]` sources in the prompt → answers with citations mapped to doc URLs.
- Deliverables: corpus size vs latency plot, sample answers with highlighted sources.

## Demo page (GitHub.io)
Static page in `docs/`: overview, figures, benchmark tables, pre-computed Q&A examples (no live LLM hosting).

## Milestones (align with the 3 presentations)
1. **Presentation 1:** Tasks 1–2 — corpus stats, chunking, embeddings, manual search demo. *(ready)*
2. **Presentation 2:** Task 3 report draft + Task 4 experiments and the P@k table.
3. **Presentation 3:** Task 5 benchmarks + RAG demo + demo page; final report.

## Verification
- `pytest tests/` — clean rules, chunk invariants, cosine parity vs sklearn; add BM25 vs `rank_bm25` and P@k
  on a toy example in Task 4.
- Notebooks run top-to-bottom from a clean venv (`uv sync` → `jupyter nbconvert --execute`).
- Modules must reproduce committed artifacts exactly (verified after the module move: cleaned pages identical,
  344 chunks identical, embeddings bit-identical).
- `torch.cuda.is_available()` and peak VRAM logged before any LLM step.
