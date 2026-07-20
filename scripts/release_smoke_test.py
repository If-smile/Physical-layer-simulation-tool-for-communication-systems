"""Exercise an installed pyberlab wheel outside the source tree."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import numpy as np

import pyberlab
from pyberlab.channel import awgn
from pyberlab.modulation import BPSK, PSK8, QAM16, QAM64, QPSK
from pyberlab.simulation import run_simulation


def main() -> None:
    """Check metadata, modulation round trips, and a short BER simulation."""
    project_root = Path(__file__).resolve().parents[1]
    imported_path = Path(pyberlab.__file__).resolve()
    if project_root in imported_path.parents:
        raise RuntimeError("smoke test imported the source tree instead of the wheel")

    installed_version = version("pyberlab")
    if installed_version != pyberlab.__version__:
        raise RuntimeError("installed and runtime versions do not match")

    rng = np.random.default_rng(2026)
    for modulator in (BPSK(), QPSK(), PSK8(), QAM16(), QAM64()):
        count = 24 * modulator.bits_per_symbol
        bits = rng.integers(0, 2, count)
        recovered = modulator.demodulate(modulator.modulate(bits))
        if not np.array_equal(bits, recovered):
            raise RuntimeError(f"{type(modulator).__name__} round trip failed")

    result = run_simulation(
        BPSK(),
        awgn,
        [0.0, 4.0],
        seed=2026,
        min_errors=10,
        max_bits=20_000,
    )
    if len(result["ber_sim"]) != 2 or not all(result["n_bits"]):
        raise RuntimeError("installed-package BER simulation failed")

    print(
        f"Installed pyberlab {installed_version} passed modulation and BER smoke tests"
    )


if __name__ == "__main__":
    main()
