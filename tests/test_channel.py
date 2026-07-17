"""Tests for channel models."""

import numpy as np
import pytest

from pyberlab.channel import awgn, rayleigh


@pytest.fixture
def rng():
    return np.random.default_rng(1)


@pytest.mark.parametrize("EbN0_dB", [0, 5, 10])
@pytest.mark.parametrize("bits_per_symbol", [1, 2, 4])
def test_awgn_noise_power(EbN0_dB, bits_per_symbol, rng):
    """Measured noise power should match the specified Eb/N0."""
    EbN0_lin = 10 ** (EbN0_dB / 10)
    expected_noise_power = 1.0 / (2.0 * bits_per_symbol * EbN0_lin)

    n = 500_000
    # Use real signal: noise is real with variance = noise_power (one-sided)
    signal = np.ones(n)
    received = awgn(signal, EbN0_lin, bits_per_symbol, rng=rng)
    noise = received - signal
    measured = float(np.mean(noise ** 2))

    # Allow 5% relative tolerance (large n keeps variance small)
    assert abs(measured - expected_noise_power) / expected_noise_power < 0.05, (
        f"EbN0={EbN0_dB}dB bps={bits_per_symbol}: "
        f"measured={measured:.6f} expected={expected_noise_power:.6f}"
    )


def test_awgn_reproducible(rng):
    """Same rng produces identical output."""
    signal = np.ones(100)
    rng1 = np.random.default_rng(99)
    rng2 = np.random.default_rng(99)
    out1 = awgn(signal, 1.0, rng=rng1)
    out2 = awgn(signal, 1.0, rng=rng2)
    np.testing.assert_array_equal(out1, out2)


def test_awgn_complex_output_for_complex_input(rng):
    """Complex input signal should produce complex output."""
    signal = np.ones(100, dtype=complex)
    out = awgn(signal, 1.0, rng=rng)
    assert np.iscomplexobj(out)


def test_awgn_real_output_for_real_input(rng):
    """Real input signal should produce real output."""
    signal = np.ones(100)
    out = awgn(signal, 1.0, rng=rng)
    assert not np.iscomplexobj(out)


@pytest.mark.parametrize("channel", [awgn, rayleigh])
@pytest.mark.parametrize("EbN0_linear", [0, -1, np.inf])
def test_channels_reject_invalid_snr(channel, EbN0_linear):
    with pytest.raises(ValueError, match="finite positive"):
        channel(np.ones(4), EbN0_linear)


@pytest.mark.parametrize("channel", [awgn, rayleigh])
def test_channels_reject_invalid_bits_per_symbol(channel):
    with pytest.raises(ValueError, match="positive integer"):
        channel(np.ones(4), 1.0, bits_per_symbol=0)


# ---------------------------------------------------------------------------
# Rayleigh channel
# ---------------------------------------------------------------------------

def test_rayleigh_reproducible():
    """Same rng seed produces identical output."""
    signal = np.ones(100)
    out1 = rayleigh(signal, 1.0, rng=np.random.default_rng(7))
    out2 = rayleigh(signal, 1.0, rng=np.random.default_rng(7))
    np.testing.assert_array_equal(out1, out2)


def test_rayleigh_real_output_for_real_input(rng):
    """Real input should produce real equalized output."""
    signal = np.ones(100)
    out = rayleigh(signal, 1.0, rng=rng)
    assert not np.iscomplexobj(out)


def test_rayleigh_complex_output_for_complex_input(rng):
    """Complex input should produce complex equalized output."""
    signal = np.ones(100, dtype=complex)
    out = rayleigh(signal, 1.0, rng=rng)
    assert np.iscomplexobj(out)


def test_rayleigh_ber_tracks_theory():
    """Simulated BPSK Rayleigh BER should be within 10% of theory at 10 dB."""
    from pyberlab.modulation import BPSK
    from pyberlab.theory import bpsk_rayleigh

    rng = np.random.default_rng(42)
    mod = BPSK()
    EbN0_lin = 10.0  # 10 dB

    bits = rng.integers(0, 2, 500_000)
    rx = rayleigh(mod.modulate(bits), EbN0_lin, mod.bits_per_symbol, rng=rng)
    ber_sim = float(np.mean(bits != mod.demodulate(rx)))
    ber_theory = bpsk_rayleigh(EbN0_lin)

    assert abs(ber_sim - ber_theory) / ber_theory < 0.10, (
        f"Rayleigh BER sim={ber_sim:.4f} theory={ber_theory:.4f}, "
        f"relative error > 10%"
    )
