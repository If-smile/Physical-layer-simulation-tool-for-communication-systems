"""Analytical and numerical BER baselines with automatic dispatch.

Each function takes ``EbN0_linear`` (linear scale, not dB) and returns the
theoretical BER as a float or numpy array.

The module also exposes ``get_theory_fn(modulator, channel_fn)`` which
returns the matching theoretical BER function automatically, so
``run_simulation`` never has to hard-code the pairing.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.integrate import quad
from scipy.special import erfc, ndtr

# ---------------------------------------------------------------------------
# Theoretical BER formulas
# ---------------------------------------------------------------------------

def bpsk_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for BPSK over AWGN: 0.5 * erfc(sqrt(Eb/N0))."""
    return 0.5 * erfc(np.sqrt(EbN0_linear))


def qpsk_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for QPSK over AWGN.

    With Gray coding, each quadrature component is an independent BPSK
    channel at the same Eb/N0, so BER equals the BPSK formula.
    """
    return 0.5 * erfc(np.sqrt(EbN0_linear))


def _psk_phase_pdf(theta: float, concentration: float) -> float:
    """Phase density of a unit phasor corrupted by circular complex AWGN."""
    cosine = np.cos(theta)
    sine = np.sin(theta)
    return float(
        np.exp(-concentration) / (2 * np.pi)
        + np.sqrt(concentration / np.pi)
        * cosine
        * np.exp(-concentration * sine**2)
        * ndtr(np.sqrt(2 * concentration) * cosine)
    )


def _psk_awgn_ber(
    EbN0_linear: np.ndarray | float, order: int
) -> np.ndarray | float:
    """Exact hard-decision BER for circular Gray-coded M-PSK over AWGN."""
    snr = np.asarray(EbN0_linear, dtype=float)
    if np.any(snr < 0):
        raise ValueError("EbN0_linear must be non-negative")
    if order < 2 or order & (order - 1):
        raise ValueError("order must be a power of two")

    bits_per_symbol = int(np.log2(order))
    phase_half_width = np.pi / order
    phase_indices = np.arange(order, dtype=np.uint8)
    labels = phase_indices ^ (phase_indices >> 1)
    hamming = np.unpackbits(
        (labels[:, np.newaxis] ^ labels[np.newaxis, :])[:, :, np.newaxis],
        axis=2,
        bitorder="big",
    ).sum(axis=2)

    result = np.empty_like(snr.reshape(-1))
    for index, value in enumerate(snr.reshape(-1)):
        if value == 0:
            result[index] = 0.5
            continue

        concentration = bits_per_symbol * value
        bit_errors = 0.0
        # Opposite angular offsets have equal probability and equal average
        # Hamming distance, so only half the decision sectors need integration.
        for offset in range(1, order // 2 + 1):
            centre = 2 * np.pi * offset / order
            probability = quad(
                _psk_phase_pdf,
                centre - phase_half_width,
                centre + phase_half_width,
                args=(concentration,),
                epsabs=1e-12,
                epsrel=1e-11,
                limit=100,
            )[0]
            target = (phase_indices + offset) % order
            mean_distance = float(np.mean(hamming[phase_indices, target]))
            multiplicity = 1 if offset == order // 2 else 2
            bit_errors += multiplicity * probability * mean_distance
        result[index] = bit_errors / bits_per_symbol

    result = result.reshape(snr.shape)
    return float(result) if result.ndim == 0 else result


def psk8_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """Exact BER for Gray-coded 8-PSK over AWGN with hard decisions."""
    return _psk_awgn_ber(EbN0_linear, order=8)


def _gray_labels(order: int) -> np.ndarray:
    """Return the Gray-code label associated with each ascending PAM level."""
    levels = int(np.sqrt(order))
    return np.arange(levels, dtype=np.uint8) ^ (
        np.arange(levels, dtype=np.uint8) >> 1
    )


def _square_qam_awgn_ber(
    EbN0_linear: np.ndarray | float, order: int
) -> np.ndarray | float:
    """Exact hard-decision BER for Gray-coded square QAM over AWGN.

    The calculation enumerates one-dimensional PAM decision regions and their
    Gray-label Hamming distances.  I and Q are independent and identically
    distributed, so their per-bit BER is also the BER of the QAM constellation.
    """
    snr = np.asarray(EbN0_linear, dtype=float)
    if np.any(snr < 0):
        raise ValueError("EbN0_linear must be non-negative")

    levels_per_axis = int(np.sqrt(order))
    bits_per_axis = int(np.log2(levels_per_axis))
    bits_per_symbol = 2 * bits_per_axis
    levels = np.arange(-(levels_per_axis - 1), levels_per_axis, 2, dtype=float)
    thresholds = (levels[:-1] + levels[1:]) / 2
    labels = _gray_labels(order)
    hamming = np.unpackbits(
        (labels[:, np.newaxis] ^ labels[np.newaxis, :])[:, :, np.newaxis],
        axis=2,
        bitorder="big",
    ).sum(axis=2)

    # Undo constellation normalisation to express the AWGN standard deviation
    # in the native PAM-level coordinates.
    scale = np.sqrt(2.0 * (levels_per_axis**2 - 1) / 3.0)
    snr_flat = snr.reshape(-1)
    result = np.empty_like(snr_flat)

    for index, value in enumerate(snr_flat):
        if value == 0:
            result[index] = 0.5
            continue

        sigma = scale / np.sqrt(2.0 * bits_per_symbol * value)
        lower = np.concatenate(([-np.inf], thresholds))
        upper = np.concatenate((thresholds, [np.inf]))
        probabilities = ndtr((upper[np.newaxis, :] - levels[:, np.newaxis]) / sigma)
        probabilities -= ndtr(
            (lower[np.newaxis, :] - levels[:, np.newaxis]) / sigma
        )
        result[index] = np.sum(probabilities * hamming) / (
            levels_per_axis * bits_per_axis
        )

    result = result.reshape(snr.shape)
    return float(result) if result.ndim == 0 else result


def qam16_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """Exact BER for Gray-coded 16-QAM over AWGN with hard decisions."""
    return _square_qam_awgn_ber(EbN0_linear, order=16)


def qam64_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """Exact BER for Gray-coded 64-QAM over AWGN with hard decisions."""
    return _square_qam_awgn_ber(EbN0_linear, order=64)


def bpsk_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for BPSK over Rayleigh flat-fading with coherent detection.

    Formula: 0.5 * (1 - sqrt(Eb/N0 / (1 + Eb/N0)))
    """
    x = EbN0_linear / (1.0 + EbN0_linear)
    return 0.5 * (1.0 - np.sqrt(x))


def qpsk_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for Gray-coded QPSK over coherent Rayleigh flat fading."""
    return bpsk_rayleigh(EbN0_linear)


def _psk_rayleigh_ber(
    EbN0_linear: np.ndarray | float, order: int
) -> np.ndarray | float:
    """Average exact AWGN M-PSK BER over independent Rayleigh fading."""
    snr = np.asarray(EbN0_linear, dtype=float)
    if np.any(snr < 0):
        raise ValueError("EbN0_linear must be non-negative")

    result = np.empty_like(snr.reshape(-1))
    for index, value in enumerate(snr.reshape(-1)):
        if value == 0:
            result[index] = 0.5
            continue
        result[index] = quad(
            lambda fading: float(_psk_awgn_ber(value * fading, order))
            * np.exp(-fading),
            0.0,
            np.inf,
            epsabs=1e-10,
            epsrel=1e-9,
            limit=150,
        )[0]
    result = result.reshape(snr.shape)
    return float(result) if result.ndim == 0 else result


def psk8_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for Gray-coded 8-PSK over coherent Rayleigh flat fading."""
    return _psk_rayleigh_ber(EbN0_linear, order=8)


def _square_qam_rayleigh_ber(
    EbN0_linear: np.ndarray | float, order: int
) -> np.ndarray | float:
    """Average exact AWGN QAM BER over independent Rayleigh fading.

    With coherent equalisation, the instantaneous Eb/N0 is exponentially
    distributed around the average Eb/N0. Adaptive quadrature evaluates that
    expectation accurately without a Monte-Carlo baseline.
    """
    snr = np.asarray(EbN0_linear, dtype=float)
    if np.any(snr < 0):
        raise ValueError("EbN0_linear must be non-negative")

    result = np.empty_like(snr.reshape(-1))
    for index, value in enumerate(snr.reshape(-1)):
        if value == 0:
            result[index] = 0.5
            continue
        result[index] = quad(
            lambda fading: float(_square_qam_awgn_ber(value * fading, order))
            * np.exp(-fading),
            0.0,
            np.inf,
            epsabs=1e-11,
            epsrel=1e-10,
            limit=200,
        )[0]
    result = result.reshape(snr.shape)
    return float(result) if result.ndim == 0 else result


def qam16_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for Gray-coded 16-QAM over coherent Rayleigh flat fading."""
    return _square_qam_rayleigh_ber(EbN0_linear, order=16)


def qam64_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for Gray-coded 64-QAM over coherent Rayleigh flat fading."""
    return _square_qam_rayleigh_ber(EbN0_linear, order=64)


# ---------------------------------------------------------------------------
# Dispatch registry
# ---------------------------------------------------------------------------
# Keys are (modulator_class_name, channel_function_name) string pairs so
# that this module does not need to import from modulation/ (avoids circular
# imports).  run_simulation passes str(type(modulator).__name__) and
# channel_fn.__name__ to look up the right formula.

_REGISTRY: dict[tuple[str, str], Callable] = {
    ("BPSK", "awgn"): bpsk_awgn,
    ("QPSK", "awgn"): qpsk_awgn,
    ("PSK8", "awgn"): psk8_awgn,
    ("QAM16", "awgn"): qam16_awgn,
    ("QAM64", "awgn"): qam64_awgn,
    ("BPSK", "rayleigh"): bpsk_rayleigh,
    ("QPSK", "rayleigh"): qpsk_rayleigh,
    ("PSK8", "rayleigh"): psk8_rayleigh,
    ("QAM16", "rayleigh"): qam16_rayleigh,
    ("QAM64", "rayleigh"): qam64_rayleigh,
}


def get_theory_fn(
    modulator_name: str,
    channel_name: str,
) -> Callable:
    """Return the theoretical BER function for a given modulator/channel pair.

    Parameters
    ----------
    modulator_name:
        ``type(modulator).__name__``, e.g. ``"BPSK"``.
    channel_name:
        ``channel_fn.__name__``, e.g. ``"awgn"``.

    Raises
    ------
    KeyError
        If the combination is not registered.
    """
    key = (modulator_name, channel_name)
    if key not in _REGISTRY:
        raise KeyError(
            f"No theoretical BER formula registered for "
            f"({modulator_name}, {channel_name}).  "
            f"Available pairs: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[key]
