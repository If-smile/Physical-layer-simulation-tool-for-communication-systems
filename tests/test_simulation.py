"""Tests for the simulation runner."""

from pathlib import Path

import numpy as np
import pytest

from pyberlab.channel import awgn, rayleigh
from pyberlab.modulation import BPSK, QPSK, QAM16
from pyberlab.simulation import run_simulation


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------

def test_result_keys():
    """run_simulation returns dict with required keys."""
    res = run_simulation(BPSK(), awgn, [0, 5], seed=0)
    for key in ["EbN0_dB", "ber_sim", "ber_theory", "n_bits", "n_errors"]:
        assert key in res


def test_result_length():
    """All result lists have the same length as EbN0_dB_range."""
    EbN0s = [0, 2, 4, 6]
    res = run_simulation(BPSK(), awgn, EbN0s, seed=0)
    for key in res:
        assert len(res[key]) == len(EbN0s), f"key '{key}' has wrong length"


# ---------------------------------------------------------------------------
# BER behaviour
# ---------------------------------------------------------------------------

def test_high_snr_ber_near_zero():
    """At very high SNR (20 dB), simulated BER should be very low."""
    res = run_simulation(BPSK(), awgn, [20], seed=0)
    assert res["ber_sim"][0] < 1e-3


def test_low_snr_ber_near_half():
    """At very low SNR (-10 dB), BER should be close to 0.5."""
    res = run_simulation(BPSK(), awgn, [-10], seed=0, max_bits=500_000)
    assert res["ber_sim"][0] > 0.3


def test_ber_decreases_with_snr():
    """Simulated BER should generally decrease as SNR increases."""
    res = run_simulation(BPSK(), awgn, np.arange(0, 10), seed=42)
    bers = res["ber_sim"]
    # Allow one non-monotone step (statistical noise at high SNR is OK)
    violations = sum(bers[i] < bers[i + 1] for i in range(len(bers) - 1))
    assert violations <= 1


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

def test_seed_reproducibility():
    """Same seed → identical results."""
    r1 = run_simulation(BPSK(), awgn, [0, 5, 10], seed=7)
    r2 = run_simulation(BPSK(), awgn, [0, 5, 10], seed=7)
    assert r1["ber_sim"] == r2["ber_sim"]


def test_different_seeds_differ():
    """Different seeds → different BER values (with very high probability)."""
    r1 = run_simulation(BPSK(), awgn, [5], seed=1)
    r2 = run_simulation(BPSK(), awgn, [5], seed=2)
    assert r1["ber_sim"] != r2["ber_sim"]


# ---------------------------------------------------------------------------
# Multiple modulations / channels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mod_cls", [BPSK, QPSK, QAM16])
def test_runs_without_error(mod_cls):
    """run_simulation should complete for all supported modulator/channel pairs."""
    run_simulation(mod_cls(), awgn, [0, 5, 10], seed=0)


def test_rayleigh_channel_runs():
    run_simulation(BPSK(), rayleigh, [0, 5, 10], seed=0)


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def test_csv_export(tmp_path):
    """CSV file is created and has the correct number of data rows."""
    csv_file = tmp_path / "results.csv"
    EbN0s = [0, 5, 10]
    run_simulation(BPSK(), awgn, EbN0s, seed=0, csv_path=csv_file)

    assert csv_file.exists()
    lines = csv_file.read_text().strip().splitlines()
    assert len(lines) == len(EbN0s) + 1  # header + data rows


def test_csv_creates_parent_dirs(tmp_path):
    """csv_path parent directories are created automatically."""
    csv_file = tmp_path / "nested" / "dir" / "out.csv"
    run_simulation(BPSK(), awgn, [0], seed=0, csv_path=csv_file)
    assert csv_file.exists()
