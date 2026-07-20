"""Memoryless channel models used by BER simulations."""

from .awgn import awgn
from .rayleigh import rayleigh

__all__ = ["awgn", "rayleigh"]
