"""AWGN channel model."""

from __future__ import annotations

import numpy as np


def _validate_channel_inputs(
    signal: np.ndarray, EbN0_linear: float, bits_per_symbol: int
) -> np.ndarray:
    """Validate common channel inputs and return a one-dimensional signal."""
    samples = np.asarray(signal)
    if samples.ndim != 1:
        raise ValueError("signal must be a one-dimensional array")
    if not isinstance(bits_per_symbol, (int, np.integer)) or bits_per_symbol <= 0:
        raise ValueError("bits_per_symbol must be a positive integer")
    if not np.isfinite(EbN0_linear) or EbN0_linear <= 0:
        raise ValueError("EbN0_linear must be a finite positive value")
    return samples


def awgn(
    signal: np.ndarray,
    EbN0_linear: float,
    bits_per_symbol: int = 1,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Add AWGN noise to a signal.

    Noise power is computed from Eb/N0 and the number of bits per symbol,
    assuming the signal has unit average symbol power.

    Parameters
    ----------
    signal:
        1-D array of transmitted symbols (real or complex).
    EbN0_linear:
        Eb/N0 in linear scale (not dB).
    bits_per_symbol:
        Number of bits encoded in each symbol (e.g. 1 for BPSK, 2 for QPSK).
    rng:
        NumPy random generator for reproducibility.  If ``None``, a fresh
        default generator is used (non-reproducible).

    Returns
    -------
    np.ndarray
        Noise-corrupted signal with the same shape and dtype family as
        *signal*.
    """
    if rng is None:
        rng = np.random.default_rng()

    signal = _validate_channel_inputs(signal, EbN0_linear, bits_per_symbol)

    noise_power = 1.0 / (2.0 * bits_per_symbol * EbN0_linear)

    if np.iscomplexobj(signal):
        noise = rng.normal(0, np.sqrt(noise_power), len(signal)) + \
                1j * rng.normal(0, np.sqrt(noise_power), len(signal))
    else:
        noise = rng.normal(0, np.sqrt(noise_power), len(signal))

    return signal + noise
