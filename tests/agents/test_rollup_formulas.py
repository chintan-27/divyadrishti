from agents.rollup_accountant.formulas import (
    compute_consensus,
    compute_heat,
    compute_momentum,
    compute_split,
)


def test_split_even():
    assert compute_split(0.5, 0.5) == 100.0


def test_split_one_sided():
    assert compute_split(1.0, 0.0) == 0.0


def test_split_zero():
    assert compute_split(0.0, 0.0) == 0.0


def test_consensus_positive():
    pos, neg = compute_consensus(0.8, 0.2)
    assert pos == 80.0
    assert neg == 0.0


def test_consensus_negative():
    pos, neg = compute_consensus(0.2, 0.8)
    assert pos == 0.0
    assert neg == 80.0


def test_consensus_zero():
    assert compute_consensus(0.0, 0.0) == (0.0, 0.0)


def test_heat():
    result = compute_heat(10.0, 5)
    assert result > 0


def test_heat_zero_authors():
    assert compute_heat(10.0, 0) == 0.0


def test_momentum_rising():
    result = compute_momentum(0.8, 0.4)
    assert result == 100.0


def test_momentum_falling():
    result = compute_momentum(0.2, 0.4)
    assert result == -50.0


def test_momentum_from_zero():
    assert compute_momentum(0.5, 0.0) == 100.0


def test_momentum_to_zero():
    assert compute_momentum(0.0, 0.5) == -100.0
