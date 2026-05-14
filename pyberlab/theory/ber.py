"""Closed-form BER formulas and modulator/channel dispatch registry.

Each function takes ``EbN0_linear`` (linear scale, not dB) and returns the
theoretical BER as a float or numpy array.

The module also exposes ``get_theory_fn(modulator, channel_fn)`` which
returns the matching theoretical BER function automatically, so
``run_simulation`` never has to hard-code the pairing.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.special import erfc

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


def qam16_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for 16-QAM over AWGN (Gray-coded, exact for rectangular const.).

    Formula: (3/8) * erfc(sqrt(2 * Eb/N0 / 5))
    """
    return (3 / 8) * erfc(np.sqrt(2 * EbN0_linear / 5))


def qam64_awgn(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for 64-QAM over AWGN (Gray-coded, exact for rectangular const.).

    Formula: (7/24) * erfc(sqrt(Eb/N0 / 7))
    """
    return (7 / 24) * erfc(np.sqrt(EbN0_linear / 7))


def bpsk_rayleigh(EbN0_linear: np.ndarray | float) -> np.ndarray | float:
    """BER for BPSK over Rayleigh flat-fading with coherent detection.

    Formula: 0.5 * (1 - sqrt(Eb/N0 / (1 + Eb/N0)))
    """
    x = EbN0_linear / (1.0 + EbN0_linear)
    return 0.5 * (1.0 - np.sqrt(x))


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
    ("QAM16", "awgn"): qam16_awgn,
    ("QAM64", "awgn"): qam64_awgn,
    ("BPSK", "rayleigh"): bpsk_rayleigh,
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
