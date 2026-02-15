import pytest

from libs.nlp.embeddings import cosine_similarity, softmax_weights
from libs.storage.schema import EMBEDDING_DIM


def test_cosine_similarity_identical():
    a = [1.0, 0.0, 0.0]
    assert abs(cosine_similarity(a, a) - 1.0) < 1e-5


def test_cosine_similarity_orthogonal():
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    assert abs(cosine_similarity(a, b)) < 1e-5


def test_cosine_similarity_opposite():
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert abs(cosine_similarity(a, b) - (-1.0)) < 1e-5


def test_cosine_similarity_zero_vector():
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_softmax_weights_sum_to_one():
    weights = softmax_weights([0.9, 0.5, 0.1])
    assert abs(sum(weights) - 1.0) < 1e-5


def test_softmax_weights_ordering():
    weights = softmax_weights([0.9, 0.1, 0.5])
    assert weights[0] > weights[2] > weights[1]


def test_softmax_weights_temperature():
    sharp = softmax_weights([1.0, 0.0], temperature=0.1)
    flat = softmax_weights([1.0, 0.0], temperature=10.0)
    # sharper temperature -> bigger difference
    assert (sharp[0] - sharp[1]) > (flat[0] - flat[1])


@pytest.mark.slow
def test_encode():
    from libs.nlp.embeddings import get_model
    model = get_model()
    vec = model.encode("hello world")
    assert len(vec) == EMBEDDING_DIM
    assert isinstance(vec[0], float)


@pytest.mark.slow
def test_encode_batch():
    from libs.nlp.embeddings import get_model
    model = get_model()
    vecs = model.encode_batch(["hello", "world"])
    assert len(vecs) == 2
    assert len(vecs[0]) == EMBEDDING_DIM


@pytest.mark.slow
def test_similar_texts_higher_similarity():
    from libs.nlp.embeddings import get_model
    model = get_model()
    v1 = model.encode("machine learning is great")
    v2 = model.encode("deep learning is wonderful")
    v3 = model.encode("the weather is sunny today")
    sim_close = cosine_similarity(v1, v2)
    sim_far = cosine_similarity(v1, v3)
    assert sim_close > sim_far
