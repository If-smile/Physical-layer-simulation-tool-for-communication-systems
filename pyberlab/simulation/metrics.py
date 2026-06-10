"""BER calculation and basic simulation statistics."""

from __future__ import annotations

import numpy as np


def calculate_ber(tx_bits: np.ndarray, rx_bits: np.ndarray) -> float:
    """Compute Bit Error Rate between transmitted and received bit arrays.

    Parameters
    ----------
    tx_bits:
        Transmitted bit array (1-D, dtype int).
    rx_bits:
        Received / decoded bit array.  Must have the same length as
        *tx_bits* (or longer; extra bits are ignored).

    Returns
    -------
    float
        Fraction of bits in error, in [0, 1].
    """
    n = len(tx_bits)
    errors = int(np.sum(tx_bits != rx_bits[:n]))
    return errors / n


def count_errors(tx_bits: np.ndarray, rx_bits: np.ndarray) -> int:
    """Return the number of bit errors."""
    n = len(tx_bits)
    return int(np.sum(tx_bits != rx_bits[:n]))
