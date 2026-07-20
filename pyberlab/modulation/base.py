"""Abstract base class for all modulation schemes."""

from abc import ABC, abstractmethod

import numpy as np


class Modulator(ABC):
    """Abstract interface for a digital modulation scheme.

    Implementations map one-dimensional binary arrays to unit-average-power
    symbols and recover hard-decision bits from received symbols. Subclasses
    must define :attr:`bits_per_symbol` and implement :meth:`modulate` and
    :meth:`demodulate`. The :attr:`bits_per_symbol` attribute reports how many
    input bits each transmitted symbol represents.
    """

    #: Number of bits carried by each complex symbol.
    bits_per_symbol: int

    def _validate_bits(self, bits: np.ndarray) -> np.ndarray:
        """Validate and return a one-dimensional binary bit array.

        Raises
        ------
        ValueError
            If the input is not one-dimensional, contains values other than
            zero and one, or cannot be divided into complete symbols.
        """
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
        """Validate and return a one-dimensional received-symbol array.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
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
            One-dimensional array containing zeros and ones. Its length must
            be a multiple of ``bits_per_symbol``.

        Returns
        -------
        np.ndarray
            One-dimensional array of real or complex symbols with normalized
            average power of one.

        Raises
        ------
        ValueError
            If *bits* is not a valid complete binary symbol stream.
        """

    @abstractmethod
    def demodulate(self, received: np.ndarray) -> np.ndarray:
        """Map received symbol array back to a bit array.

        Parameters
        ----------
        received:
            One-dimensional array of real or complex received samples,
            possibly corrupted by noise or fading.

        Returns
        -------
        np.ndarray
            One-dimensional array of hard-decision bits. Its length equals
            ``len(received) * bits_per_symbol``.

        Raises
        ------
        ValueError
            If *received* is not one-dimensional.
        """
