"""Tests for modulation/demodulation correctness."""

import numpy as np
import pytest

from pyberlab.modulation import BPSK, PSK8, QAM16, QAM64, QPSK


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
def test_round_trip_no_noise(cls, rng):
    """demodulate(modulate(bits)) == bits when there is no noise."""
    mod = cls()
    n = 1000 * mod.bits_per_symbol
    bits = rng.integers(0, 2, n)
    recovered = mod.demodulate(mod.modulate(bits))
    assert np.array_equal(bits, recovered), (
        f"{cls.__name__}: {np.sum(bits != recovered)} bit errors in round-trip"
    )


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
def test_symbol_power_normalised(cls, rng):
    """Average symbol power should be within 2% of 1.0."""
    mod = cls()
    bits = rng.integers(0, 2, 100_000 * mod.bits_per_symbol)
    symbols = mod.modulate(bits)
    avg_power = float(np.mean(np.abs(symbols) ** 2))
    assert abs(avg_power - 1.0) < 0.02, (
        f"{cls.__name__}: avg power = {avg_power:.4f}, expected ~1.0"
    )


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
def test_bits_per_symbol(cls):
    """bits_per_symbol matches expected values."""
    expected = {BPSK: 1, QPSK: 2, PSK8: 3, QAM16: 4, QAM64: 6}
    assert cls().bits_per_symbol == expected[cls]


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
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


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
def test_rejects_invalid_bit_input(cls):
    mod = cls()
    if mod.bits_per_symbol > 1:
        with pytest.raises(ValueError, match="multiple"):
            mod.modulate(np.zeros(mod.bits_per_symbol + 1, dtype=int))
    with pytest.raises(ValueError, match="only 0 and 1"):
        mod.modulate(np.full(mod.bits_per_symbol, 2, dtype=int))


@pytest.mark.parametrize("cls", [BPSK, QPSK, PSK8, QAM16, QAM64])
def test_rejects_non_vector_received_input(cls):
    with pytest.raises(ValueError, match="one-dimensional"):
        cls().demodulate(np.ones((2, 2)))


def test_psk8_uses_circular_gray_order():
    """Consecutive phase points, including wrap-around, differ by one bit."""
    gray_labels = np.array([0, 1, 3, 2, 6, 7, 5, 4], dtype=np.uint8)
    label_bits = np.unpackbits(
        gray_labels[:, np.newaxis], axis=1, bitorder="big"
    )[:, -3:]
    symbols = PSK8().modulate(label_bits.flatten())
    expected = np.exp(1j * 2 * np.pi * np.arange(8) / 8)
    np.testing.assert_allclose(symbols, expected, atol=1e-12)
    assert np.all(np.sum(label_bits != np.roll(label_bits, -1, axis=0), axis=1) == 1)
