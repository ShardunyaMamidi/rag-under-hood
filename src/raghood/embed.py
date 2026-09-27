"""Embedding with all-MiniLM-L6-v2 (Task 1), reusable for the Task 4 size sweep.

The model is a 3-module pipeline: a 6-layer BERT encoder, mean pooling over the token
vectors, then L2 normalisation. Because of that last module every returned vector has
length exactly 1, which is why cosine similarity reduces to a dot product in `search.py`.

Note `max_seq_length` is 256 tokens. Flask docs run ~1.8 WordPiece tokens per word, so a
200-word chunk is usually truncated -- see `token_stats` and the Task 1 notebook.
"""
import functools

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@functools.lru_cache(maxsize=2)
def load_model(name: str = MODEL_NAME, device: str | None = None) -> SentenceTransformer:
    """Load (and cache) the sentence transformer, on the GPU when one is available."""
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    return SentenceTransformer(name, device=device)


def embed_texts(texts: list[str], model: SentenceTransformer | None = None,
                batch_size: int = 32, show_progress_bar: bool = False) -> np.ndarray:
    """Encode texts into a (N, 384) float32 matrix, row i corresponding to texts[i]."""
    model = model or load_model()
    emb = model.encode(texts, batch_size=batch_size, convert_to_numpy=True,
                       show_progress_bar=show_progress_bar)
    assert emb.shape == (len(texts), model.get_embedding_dimension()), emb.shape
    assert np.isfinite(emb).all(), "NaN/inf in embeddings"
    return emb


def embed_chunks(chunks: list[dict], **kwargs) -> np.ndarray:
    """Encode chunk texts. Assumes `chunks` is ordered by id, so row i belongs to chunk i."""
    assert [c["id"] for c in chunks] == list(range(len(chunks))), "chunks are not ordered by id"
    return embed_texts([c["text"] for c in chunks], **kwargs)


def token_stats(texts: list[str], model: SentenceTransformer | None = None) -> dict:
    """How many texts exceed the encoder's token limit, i.e. get silently truncated."""
    model = model or load_model()
    lengths = np.array([len(model.tokenizer(t)["input_ids"]) for t in texts])
    over = lengths > model.max_seq_length
    return {"max_seq_length": model.max_seq_length, "lengths": lengths,
            "median": float(np.median(lengths)), "max": int(lengths.max()),
            "n_truncated": int(over.sum()), "frac_truncated": float(over.mean())}
