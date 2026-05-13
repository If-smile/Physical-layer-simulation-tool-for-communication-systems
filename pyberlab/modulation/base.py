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

    @abstractmethod
    def modulate(self, bits: np.ndarray) -> np.ndarray:
        """Map bit array to symbol array.

        Parameters
        ----------
        bits:
            1-D array of ints in {0, 1}.  Length must be a multiple of
            ``bits_per_symbol``; implementations may silently truncate
            any trailing remainder.

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
