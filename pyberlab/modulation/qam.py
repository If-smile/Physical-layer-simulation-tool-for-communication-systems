"""QAM modulation schemes: 16-QAM and 64-QAM."""

from __future__ import annotations

import numpy as np

from .base import Modulator


def _gray_to_bin(g: int) -> int:
    """Convert Gray-coded integer to binary."""
    n = g
    mask = n >> 1
    while mask:
        n ^= mask
        mask >>= 1
    return n


class _SquareQAM(Modulator):
    """Base class for square M-QAM with Gray coding.

    Bit layout per symbol (bits_per_symbol = 2 * bpd):
        [I_bit_0, ..., I_bit_{bpd-1}, Q_bit_0, ..., Q_bit_{bpd-1}]

    Subclasses set ``order`` (must be 16 or 64).
    """

    order: int

    def __init__(self) -> None:
        m = int(np.sqrt(self.order))
        assert m * m == self.order
        self.bits_per_symbol: int = int(np.log2(self.order))
        self._m = m
        self._bpd = self.bits_per_symbol // 2  # bits per dimension

        # Gray-coded PAM levels for one dimension.
        # Position i in this array corresponds to Gray-code index i.
        raw_levels = np.arange(-(m - 1), m, 2, dtype=float)  # e.g. [-3,-1,+1,+3]
        # Simpler: map Gray index → raw level via gray_to_bin
        self._pam_levels = raw_levels[[_gray_to_bin(g) for g in range(m)]]

        # Normalise so average symbol power = 1
        avg_power = 2.0 * (m ** 2 - 1) / 3.0
        self._scale = np.sqrt(avg_power)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bits_to_pam(self, bits: np.ndarray) -> np.ndarray:
        """Convert a flat bit array (length n*bpd) → n PAM levels.

        Bits within each group are MSB-first Gray-code index.
        """
        bpd = self._bpd
        n = len(bits) // bpd
        b = bits[: n * bpd].reshape(n, bpd).astype(np.uint8)
        # Pack bpd bits → integer (MSB first), then keep only bpd LSBs
        packed = np.packbits(b, axis=1, bitorder="big").flatten()
        gray_idx = (packed >> (8 - bpd)) & (self._m - 1)
        return self._pam_levels[gray_idx]

    def _pam_to_bits(self, levels: np.ndarray) -> np.ndarray:
        """Nearest-neighbour slice of PAM levels → flat bit array."""
        bpd = self._bpd
        dist = np.abs(levels[:, np.newaxis] - self._pam_levels[np.newaxis, :])
        gray_idx = np.argmin(dist, axis=1)  # shape (n,)
        # gray_idx is already the Gray-code index; unpack to bpd bits
        bits = np.unpackbits(
            gray_idx.astype(np.uint8)[:, np.newaxis], axis=1, bitorder="big"
        )
        return bits[:, 8 - bpd:].flatten()  # keep bpd LSBs

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map binary labels to unit-power complex QAM symbols.

        Parameters
        ----------
        bits:
            One-dimensional binary array whose length is a multiple of
            :attr:`bits_per_symbol`.

        Returns
        -------
        np.ndarray
            One complex QAM symbol per complete input label.

        Raises
        ------
        ValueError
            If *bits* is not a valid complete binary symbol stream.
        """
        bps = self.bits_per_symbol
        bpd = self._bpd
        bits = self._validate_bits(bits)
        n_sym = len(bits) // bps
        bits = bits.reshape(n_sym, bps)

        i_levels = self._bits_to_pam(bits[:, :bpd].flatten())
        q_levels = self._bits_to_pam(bits[:, bpd:].flatten())

        return (i_levels + 1j * q_levels) / self._scale

    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Recover bits by independently slicing the I and Q PAM levels.

        Parameters
        ----------
        received:
            One-dimensional array of received QAM symbols.

        Returns
        -------
        np.ndarray
            Hard-decision bits in the original per-symbol I/Q layout.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
        received = self._validate_received(received)
        bpd = self._bpd
        n_sym = len(received)
        r = received * self._scale  # undo normalisation

        i_bits = self._pam_to_bits(np.real(r)).reshape(n_sym, bpd)
        q_bits = self._pam_to_bits(np.imag(r)).reshape(n_sym, bpd)

        # Reconstruct original bit layout: [I_bits | Q_bits] per symbol
        return np.hstack([i_bits, q_bits]).flatten()


class QAM16(_SquareQAM):
    """Gray-coded square 16-QAM with unit average symbol power.

    Each symbol carries four bits: two select the in-phase PAM level and two
    select the quadrature PAM level. Demodulation uses nearest-neighbour slicing
    independently on the two axes.
    """

    order = 16


class QAM64(_SquareQAM):
    """Gray-coded square 64-QAM with unit average symbol power.

    Each symbol carries six bits: three select the in-phase PAM level and three
    select the quadrature PAM level. Demodulation uses nearest-neighbour slicing
    independently on the two axes.
    """

    order = 64
