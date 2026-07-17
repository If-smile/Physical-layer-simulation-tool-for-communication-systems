"""Unified simulation runner with adaptive sample sizing and CSV export."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable

import numpy as np

from ..modulation.base import Modulator
from ..theory.ber import get_theory_fn
from .metrics import calculate_ber, count_errors


def run_simulation(
    modulator: Modulator,
    channel_fn: Callable,
    EbN0_dB_range,
    *,
    seed: int | None = None,
    min_errors: int = 100,
    max_bits: int = 10_000_000,
    csv_path: str | Path | None = None,
) -> dict:
    """Run a BER simulation over a range of Eb/N0 values.

    For each SNR point the sample count is chosen adaptively: enough bits are
    generated to expect at least *min_errors* errors (based on the theoretical
    BER), capped at *max_bits* to bound runtime.

    Parameters
    ----------
    modulator:
        An instance of a :class:`~pyberlab.modulation.base.Modulator`
        subclass (e.g. ``BPSK()``, ``QAM16()``).
    channel_fn:
        Channel function with signature
        ``channel_fn(signal, EbN0_linear, bits_per_symbol, *, rng) -> received``.
        Must be one of the registered channels (``awgn``, ``rayleigh``).
    EbN0_dB_range:
        Iterable of Eb/N0 values in dB.
    seed:
        Integer seed for reproducibility.  ``None`` → non-reproducible.
    min_errors:
        Minimum expected error count used to set adaptive sample size.
    max_bits:
        Hard cap on bits per SNR point.
    csv_path:
        If provided, results are saved to this CSV file.

    Returns
    -------
    dict
        Keys: ``EbN0_dB``, ``ber_sim``, ``ber_theory``,
        ``n_bits``, ``n_errors``  — each a list of length
        ``len(EbN0_dB_range)``.
    """
    if not isinstance(modulator, Modulator):
        raise TypeError("modulator must be an instance of Modulator")
    if not callable(channel_fn):
        raise TypeError("channel_fn must be callable")
    if not isinstance(min_errors, (int, np.integer)) or min_errors <= 0:
        raise ValueError("min_errors must be a positive integer")
    if not isinstance(max_bits, (int, np.integer)) or max_bits < modulator.bits_per_symbol:
        raise ValueError("max_bits must be at least bits_per_symbol")

    EbN0_dB_values = list(EbN0_dB_range)
    if not EbN0_dB_values:
        raise ValueError("EbN0_dB_range must not be empty")
    if not all(np.isfinite(value) for value in EbN0_dB_values):
        raise ValueError("EbN0_dB_range must contain only finite values")

    rng = np.random.default_rng(seed)

    modulator_name = type(modulator).__name__
    channel_name = channel_fn.__name__
    theory_fn = get_theory_fn(modulator_name, channel_name)

    results: dict[str, list] = {
        "EbN0_dB": [],
        "ber_sim": [],
        "ber_theory": [],
        "n_bits": [],
        "n_errors": [],
    }

    for EbN0_dB in EbN0_dB_values:
        EbN0_linear = 10 ** (EbN0_dB / 10)
        if not np.isfinite(EbN0_linear) or EbN0_linear <= 0:
            raise ValueError("Eb/N0 values must produce finite positive linear SNRs")

        # Adaptive sample sizing: target min_errors expected bit errors
        expected_ber = float(theory_fn(EbN0_linear))
        expected_ber = max(expected_ber, 1e-10)  # avoid division by zero
        n_bits = int(min_errors / expected_ber)
        n_bits = min(max_bits, max(100_000, n_bits))
        # Align to bits_per_symbol
        bps = modulator.bits_per_symbol
        n_bits = (n_bits // bps) * bps

        tx_bits = rng.integers(0, 2, n_bits)
        tx_symbols = modulator.modulate(tx_bits)
        rx_symbols = channel_fn(tx_symbols, EbN0_linear, bps, rng=rng)
        rx_bits = modulator.demodulate(rx_symbols)

        n_err = count_errors(tx_bits, rx_bits)
        ber = calculate_ber(tx_bits, rx_bits)

        results["EbN0_dB"].append(float(EbN0_dB))
        results["ber_sim"].append(ber)
        results["ber_theory"].append(float(expected_ber))
        results["n_bits"].append(n_bits)
        results["n_errors"].append(n_err)

    if csv_path is not None:
        _save_csv(results, Path(csv_path))

    return results


def _save_csv(results: dict, path: Path) -> None:
    """Write simulation results to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["EbN0_dB", "ber_sim", "ber_theory", "n_bits", "n_errors"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(results["EbN0_dB"])):
            writer.writerow({k: results[k][i] for k in fieldnames})
