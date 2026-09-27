"""Tests for the hand-written cosine retrieval (Task 2)."""
import numpy as np
import pytest
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

from raghood.search import cosine_similarity_numpy, cosine_similarity_torch, top_k


@pytest.fixture
def random_corpus():
    """Deliberately un-normalised vectors with wildly different lengths, so |d| matters."""
    rng = np.random.default_rng(0)
    D = rng.normal(size=(64, 384)).astype(np.float32) * rng.uniform(0.1, 20, (64, 1)).astype(np.float32)
    q = (rng.normal(size=384) * 5).astype(np.float32)
    return q, D


def test_matches_sklearn(random_corpus):
    q, D = random_corpus
    assert np.allclose(cosine_similarity_numpy(q, D), sk_cosine(q.reshape(1, -1), D).ravel(), atol=1e-5)


def test_torch_matches_numpy(random_corpus):
    import torch

    q, D = random_corpus
    got = cosine_similarity_torch(torch.from_numpy(q), torch.from_numpy(D)).numpy()
    assert np.allclose(got, cosine_similarity_numpy(q, D), atol=1e-5)


def test_bounded_and_scale_invariant(random_corpus):
    q, D = random_corpus
    sims = cosine_similarity_numpy(q, D)
    assert sims.shape == (len(D),)
    assert np.all((sims >= -1.0001) & (sims <= 1.0001))
    # cosine depends on direction only: scaling q or any row must not change the scores
    assert np.allclose(sims, cosine_similarity_numpy(q * 37.0, D * 0.013), atol=1e-5)


def test_identical_vector_scores_one():
    D = np.array([[1.0, 2.0, 3.0], [-1.0, 0.0, 1.0]], dtype=np.float32)
    assert cosine_similarity_numpy(D[0], D)[0] == pytest.approx(1.0, abs=1e-6)
    assert cosine_similarity_numpy(-D[0], D)[0] == pytest.approx(-1.0, abs=1e-6)


def test_top_k_matches_full_sort(random_corpus):
    q, D = random_corpus
    sims = cosine_similarity_numpy(q, D)
    for k in (1, 3, 10, len(D)):
        assert list(top_k(sims, k)) == list(np.argsort(-sims)[:k])


def test_top_k_is_sorted_best_first(random_corpus):
    q, D = random_corpus
    sims = cosine_similarity_numpy(q, D)
    chosen = sims[top_k(sims, 5)]
    assert list(chosen) == sorted(chosen, reverse=True)


def test_top_k_clamps_to_corpus_size():
    scores = np.array([0.1, 0.9, 0.5])
    assert len(top_k(scores, 99)) == 3
    assert list(top_k(scores, 99)) == [1, 2, 0]
