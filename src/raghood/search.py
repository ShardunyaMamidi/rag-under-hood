"""Cosine-similarity retrieval written from the formula (Task 2).

No search library is involved: only numpy.dot / torch.matmul. The notebook
`notebooks/manual_retrieval.ipynb` derives and verifies these functions against
sklearn; this module is the reusable copy for Tasks 4 and 5.
"""
import numpy as np
import torch


def cosine_similarity_numpy(q: np.ndarray, D: np.ndarray) -> np.ndarray:
    """Cosine similarity between query vector q (d,) and every row of D (N, d).

    Straight from the definition: (q . d) / (|q| |d|).
    """
    dots = D @ q                                             # (N,)  numerator
    norms = np.linalg.norm(D, axis=1) * np.linalg.norm(q)    # (N,)  denominator
    return dots / norms


def cosine_similarity_torch(q: torch.Tensor, D: torch.Tensor) -> torch.Tensor:
    """Same formula via torch.matmul, so it can run on the GPU."""
    dots = torch.matmul(D, q)
    norms = torch.linalg.norm(D, dim=1) * torch.linalg.norm(q)
    return dots / norms


def top_k(scores: np.ndarray, k: int = 3) -> np.ndarray:
    """Indices of the k highest scores, best first.

    argpartition is an O(N) partial selection; only the k winners are then sorted.
    """
    k = min(k, scores.shape[0])
    idx = np.argpartition(-scores, k - 1)[:k]
    return idx[np.argsort(-scores[idx])]


def search(query: str, model, D: np.ndarray, chunks: list[dict], k: int = 3) -> list[dict]:
    """Embed `query`, score it against every row of D, return the k best chunks with their score."""
    q = model.encode(query, convert_to_numpy=True)
    scores = cosine_similarity_numpy(q, D)
    return [{**chunks[i], "rank": rank + 1, "score": float(scores[i])}
            for rank, i in enumerate(top_k(scores, k))]
