"""Digital modulation and hard-decision demodulation schemes.

All modulators implement the :class:`Modulator` interface and use
unit-average-power constellations so that channel Eb/N0 handling is consistent.
"""

from .base import Modulator
from .psk import BPSK, PSK8, QPSK
from .qam import QAM16, QAM64

__all__ = ["Modulator", "BPSK", "QPSK", "PSK8", "QAM16", "QAM64"]
