"""PSK modulation schemes: BPSK and QPSK."""

from __future__ import annotations

import numpy as np

from .base import Modulator


class BPSK(Modulator):
    """Binary Phase Shift Keying.

    Constellation: {-1, +1} on the real axis.
    Average symbol power: 1.
    bits_per_symbol: 1
    """

    bits_per_symbol: int = 1

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map bits {0, 1} → symbols {-1, +1}."""
        bits = self._validate_bits(bits)
        return (2 * bits - 1).astype(float)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Hard decision on real part: positive → 1, negative → 0."""
        received = self._validate_received(received)
        return (np.real(received) > 0).astype(int)


class QPSK(Modulator):
    """Quadrature Phase Shift Keying with Gray coding.

    Bit pairs are mapped to four constellation points in the four quadrants:
        00 → (+1+1j) / √2
        01 → (+1-1j) / √2
        11 → (-1-1j) / √2
        10 → (-1+1j) / √2

    Average symbol power: 1.
    bits_per_symbol: 2
    """

    bits_per_symbol: int = 2

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map bit pairs to complex QPSK symbols.

        Bits are processed in pairs; an odd-length input is rejected.
        """
        bits = self._validate_bits(bits).reshape(-1, 2)
        # I branch: bit 0 → {-1, +1}, Q branch: bit 1 → {-1, +1}
        i = (2 * bits[:, 0] - 1).astype(float)
        q = (2 * bits[:, 1] - 1).astype(float)
        return (i + 1j * q) / np.sqrt(2)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Separate I/Q hard decisions, interleave back to bit stream."""
        received = self._validate_received(received)
        i_bits = (np.real(received) > 0).astype(int)
        q_bits = (np.imag(received) > 0).astype(int)
        # Interleave: [i0, q0, i1, q1, ...]
        return np.column_stack([i_bits, q_bits]).flatten()
