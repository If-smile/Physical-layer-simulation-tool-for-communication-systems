"""PSK modulation schemes: BPSK, QPSK, and 8-PSK."""

from __future__ import annotations

import numpy as np

from .base import Modulator


class BPSK(Modulator):
    """Binary phase-shift keying with unit symbol power.

    Zero maps to ``-1`` and one maps to ``+1`` on the real axis. Detection uses
    the sign of the received sample's real component. Each symbol carries one
    bit.
    """

    bits_per_symbol: int = 1

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map binary values to ``-1`` and ``+1`` symbols.

        Parameters
        ----------
        bits:
            One-dimensional binary array.

        Returns
        -------
        np.ndarray
            Real BPSK symbols with unit average power.

        Raises
        ------
        ValueError
            If *bits* is not a one-dimensional binary array.
        """
        bits = self._validate_bits(bits)
        return (2 * bits - 1).astype(float)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Recover bits using a zero-threshold decision on the real part.

        Parameters
        ----------
        received:
            One-dimensional array of received BPSK samples.

        Returns
        -------
        np.ndarray
            Hard-decision bits, with positive samples mapped to one.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
        received = self._validate_received(received)
        return (np.real(received) > 0).astype(int)


class QPSK(Modulator):
    """Gray-coded quadrature phase-shift keying.

    The first and second bits independently select the in-phase and quadrature
    signs. Symbols are divided by ``sqrt(2)`` to give unit average power. This
    produces the circular Gray ordering ``00, 01, 11, 10``. Each symbol carries
    two bits.
    """

    bits_per_symbol: int = 2

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map bit pairs to complex unit-power QPSK symbols.

        Parameters
        ----------
        bits:
            One-dimensional binary array with an even length.

        Returns
        -------
        np.ndarray
            One complex QPSK symbol per input bit pair.

        Raises
        ------
        ValueError
            If *bits* is not a one-dimensional binary array with an even
            length.
        """
        bits = self._validate_bits(bits).reshape(-1, 2)
        # I branch: bit 0 → {-1, +1}, Q branch: bit 1 → {-1, +1}
        i = (2 * bits[:, 0] - 1).astype(float)
        q = (2 * bits[:, 1] - 1).astype(float)
        return (i + 1j * q) / np.sqrt(2)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Recover interleaved bits using independent I/Q sign decisions.

        Parameters
        ----------
        received:
            One-dimensional array of received QPSK symbols.

        Returns
        -------
        np.ndarray
            Two hard-decision bits per received symbol.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
        received = self._validate_received(received)
        i_bits = (np.real(received) > 0).astype(int)
        q_bits = (np.imag(received) > 0).astype(int)
        # Interleave: [i0, q0, i1, q1, ...]
        return np.column_stack([i_bits, q_bits]).flatten()


class PSK8(Modulator):
    """Gray-coded 8-Phase Shift Keying with unit symbol power.

    The three input bits form a Gray-code label. Consecutive phase indices use
    the circular Gray sequence ``000, 001, 011, 010, 110, 111, 101, 100``. Each
    symbol carries three bits.
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
        """Map three-bit Gray labels to unit-magnitude complex symbols.

        Parameters
        ----------
        bits:
            One-dimensional binary array whose length is a multiple of three.

        Returns
        -------
        np.ndarray
            One complex 8-PSK symbol per three input bits.

        Raises
        ------
        ValueError
            If *bits* is not a one-dimensional binary array whose length is a
            multiple of three.
        """
        grouped = self._validate_bits(bits).reshape(-1, self.bits_per_symbol)
        weights = 1 << np.arange(self.bits_per_symbol - 1, -1, -1)
        gray_indices = grouped @ weights
        phase_indices = self._gray_to_binary(gray_indices)
        phases = 2 * np.pi * phase_indices / self._order
        return np.exp(1j * phases)

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Make nearest-phase decisions and return three-bit Gray labels.

        Parameters
        ----------
        received:
            One-dimensional array of received 8-PSK symbols.

        Returns
        -------
        np.ndarray
            Three hard-decision bits per received symbol.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
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
