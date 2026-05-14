"""Tests for modulation/demodulation correctness."""

import numpy as np
import pytest

from pyberlab.modulation import BPSK, QPSK, QAM16, QAM64


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.mark.parametrize("cls", [BPSK, QPSK, QAM16, QAM64])
def test_round_trip_no_noise(cls, rng):
    """demodulate(modulate(bits)) == bits when there is no noise."""
    mod = cls()
    n = 1000 * mod.bits_per_symbol
    bits = rng.integers(0, 2, n)
    recovered = mod.demodulate(mod.modulate(bits))
    assert np.array_equal(bits, recovered), (
        f"{cls.__name__}: {np.sum(bits != recovered)} bit errors in round-trip"
    )


@pytest.mark.parametrize("cls", [BPSK, QPSK, QAM16, QAM64])
def test_symbol_power_normalised(cls, rng):
    """Average symbol power should be within 2% of 1.0."""
    mod = cls()
    bits = rng.integers(0, 2, 100_000 * mod.bits_per_symbol)
    symbols = mod.modulate(bits)
    avg_power = float(np.mean(np.abs(symbols) ** 2))
    assert abs(avg_power - 1.0) < 0.02, (
        f"{cls.__name__}: avg power = {avg_power:.4f}, expected ~1.0"
    )


@pytest.mark.parametrize("cls", [BPSK, QPSK, QAM16, QAM64])
def test_bits_per_symbol(cls):
    """bits_per_symbol matches expected values."""
    expected = {BPSK: 1, QPSK: 2, QAM16: 4, QAM64: 6}
    assert cls().bits_per_symbol == expected[cls]


@pytest.mark.parametrize("cls", [BPSK, QPSK, QAM16, QAM64])
def test_output_length(cls, rng):
    """modulate output length and demodulate output length are consistent."""
    mod = cls()
    bps = mod.bits_per_symbol
    n_sym = 256
    bits = rng.integers(0, 2, n_sym * bps)
    symbols = mod.modulate(bits)
    assert len(symbols) == n_sym
    recovered = mod.demodulate(symbols)
    assert len(recovered) == n_sym * bps
