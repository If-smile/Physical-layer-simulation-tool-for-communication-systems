"""Rayleigh flat-fading channel model."""

from __future__ import annotations

import numpy as np

from .awgn import _validate_channel_inputs


def rayleigh(
    signal: np.ndarray,
    EbN0_linear: float,
    bits_per_symbol: int = 1,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Apply Rayleigh flat fading and AWGN, then coherently equalize.

    Each symbol is multiplied by an independent complex Gaussian fading
    coefficient h ~ CN(0, 1), then corrupted by AWGN.  Coherent detection
    assumes perfect channel knowledge at the receiver: the received signal is
    divided by h before making a decision.

    The fading coefficient is normalised so that E[|h|²] = 1, preserving the
    same average SNR definition as the AWGN channel.

    Parameters
    ----------
    signal:
        1-D array of transmitted symbols (real or complex) with unit average
        power.
    EbN0_linear:
        Eb/N0 in linear scale (not dB).
    bits_per_symbol:
        Number of bits encoded in each symbol.
    rng:
        NumPy random generator for reproducibility.  If ``None``, a fresh
        default generator is used.

    Returns
    -------
    np.ndarray
        Equalized received symbols, same length as *signal*.
    """
    if rng is None:
        rng = np.random.default_rng()

    signal = _validate_channel_inputs(signal, EbN0_linear, bits_per_symbol)

    n = len(signal)

    # Rayleigh fading: h ~ CN(0,1), i.e. real/imag each ~ N(0, 1/sqrt(2))
    h = (rng.normal(0, 1 / np.sqrt(2), n) +
         1j * rng.normal(0, 1 / np.sqrt(2), n))

    # AWGN: noise power per dimension = 1 / (2 * bps * EbN0)
    noise_power = 1.0 / (2.0 * bits_per_symbol * EbN0_linear)
    noise = (rng.normal(0, np.sqrt(noise_power), n) +
             1j * rng.normal(0, np.sqrt(noise_power), n))

    # Received signal: y = h * x + n
    received = h * signal + noise

    # Coherent equalization: x_hat = y / h
    equalized = received / h

    # Return real part only for real-valued input signals (e.g. BPSK)
    if not np.iscomplexobj(signal):
        return equalized.real

    return equalized
