"""Abstract base class for all modulation schemes."""

from abc import ABC, abstractmethod

import numpy as np


class Modulator(ABC):
    """Common interface for all modulation schemes.

    Subclasses must set ``bits_per_symbol`` and implement
    ``modulate`` / ``demodulate``.
    """

    #: Number of bits carried by each complex symbol.
    bits_per_symbol: int

    def _validate_bits(self, bits: np.ndarray) -> np.ndarray:
        """Validate and return a one-dimensional binary bit array."""
        values = np.asarray(bits)
        if values.ndim != 1:
            raise ValueError("bits must be a one-dimensional array")
        if len(values) % self.bits_per_symbol:
            raise ValueError(
                "bit array length must be a multiple of bits_per_symbol "
                f"({self.bits_per_symbol})"
            )
        if not np.all((values == 0) | (values == 1)):
            raise ValueError("bits must contain only 0 and 1")
        return values.astype(int, copy=False)

    @staticmethod
    def _validate_received(received: np.ndarray) -> np.ndarray:
        """Validate and return a one-dimensional received-symbol array."""
        values = np.asarray(received)
        if values.ndim != 1:
            raise ValueError("received symbols must be a one-dimensional array")
        return values

    @abstractmethod
    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map bit array to symbol array.

        Parameters
        ----------
        bits:
            1-D array of ints in {0, 1}. Length must be a multiple of
            ``bits_per_symbol``.

        Returns
        -------
        np.ndarray
            1-D array of complex (or real) symbols with normalised
            average power of 1.
        """

    @abstractmethod
    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Map received symbol array back to a bit array.

        Parameters
        ----------
        received:
            1-D array of complex (or real) received samples, possibly
            noise-corrupted.

        Returns
        -------
        np.ndarray
            1-D array of hard-decision bits in {0, 1}.  Length equals
            ``len(received) * bits_per_symbol``.
        """
