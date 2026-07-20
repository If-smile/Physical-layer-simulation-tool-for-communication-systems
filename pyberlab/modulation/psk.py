"""PSK modulation schemes: BPSK, QPSK, and 8-PSK."""

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
        00 → (-1-1j) / √2
        01 → (-1+1j) / √2
        11 → (+1+1j) / √2
        10 → (+1-1j) / √2

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


class PSK8(Modulator):
    """Gray-coded 8-Phase Shift Keying with unit symbol power.

    The three input bits form a Gray-code label. Consecutive phase indices use
    the circular Gray sequence ``000, 001, 011, 010, 110, 111, 101, 100``.
    """

    bits_per_symbol: int = 3
    _order: int = 8

    @staticmethod
    def _gray_to_binary(gray: np.ndarray) -> np.ndarray:
        """Convert vectorised 3-bit Gray integers to binary phase indices."""
        binary = gray.copy()
        shift = gray >> 1
        while np.any(shift):
            binary ^= shift
            shift >>= 1
        return binary

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map three-bit Gray labels to unit-magnitude complex symbols."""
        grouped = self._validate_bits(bits).reshape(-1, self.bits_per_symbol)
        weights = 1 << np.arange(self.bits_per_symbol - 1, -1, -1)
        gray_indices = grouped @ weights
        phase_indices = self._gray_to_binary(gray_indices)
        phases = 2 * np.pi * phase_indices / self._order
        return np.exp(1j * phases)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Make nearest-phase decisions and return three-bit Gray labels."""
        received = self._validate_received(received)
        phase_step = 2 * np.pi / self._order
        phases = np.mod(np.angle(received), 2 * np.pi)
        phase_indices = np.floor(phases / phase_step + 0.5).astype(np.uint8)
        phase_indices %= self._order
        gray_indices = phase_indices ^ (phase_indices >> 1)
        unpacked = np.unpackbits(
            gray_indices[:, np.newaxis], axis=1, bitorder="big"
        )
        return unpacked[:, -self.bits_per_symbol :].flatten()
