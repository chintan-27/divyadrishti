import pytest


@pytest.mark.slow
def test_predict_positive():
    from libs.nlp.sentiment import get_model
    model = get_model()
    signal = model.predict("This is absolutely fantastic and wonderful!")
    assert signal.label == "positive"
    assert signal.valence > 0
    assert 0 <= signal.confidence <= 1


@pytest.mark.slow
def test_predict_negative():
    from libs.nlp.sentiment import get_model
    model = get_model()
    signal = model.predict("This is terrible and horrible.")
    assert signal.label == "negative"
    assert signal.valence < 0


@pytest.mark.slow
def test_predict_batch():
    from libs.nlp.sentiment import get_model
    model = get_model()
    signals = model.predict_batch(["Great work!", "Awful code.", "The sky is blue."])
    assert len(signals) == 3
    assert all(s.model_version != "" for s in signals)
    assert all(0 <= s.confidence <= 1 for s in signals)


@pytest.mark.slow
def test_singleton():
    from libs.nlp.sentiment import get_model
    m1 = get_model()
    m2 = get_model()
    assert m1 is m2
