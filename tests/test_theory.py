"""Tests for theoretical BER formulas and dispatch registry."""

import numpy as np
import pytest
from scipy.special import erfc

from pyberlab.theory.ber import (
    bpsk_awgn,
    bpsk_rayleigh,
    get_theory_fn,
    qam16_awgn,
    qam64_awgn,
    qpsk_awgn,
)


# ---------------------------------------------------------------------------
# Formula correctness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("EbN0_dB", [0, 5, 10])
def test_bpsk_awgn_values(EbN0_dB):
    lin = 10 ** (EbN0_dB / 10)
    expected = 0.5 * erfc(np.sqrt(lin))
    assert bpsk_awgn(lin) == pytest.approx(expected, rel=1e-9)


def test_qpsk_awgn_equals_bpsk_awgn():
    """QPSK BER should equal BPSK BER at the same Eb/N0."""
    lin = np.array([1.0, 3.162, 10.0])
    np.testing.assert_allclose(qpsk_awgn(lin), bpsk_awgn(lin))


@pytest.mark.parametrize("EbN0_dB", [0, 5, 10, 15])
def test_qam16_awgn_formula(EbN0_dB):
    lin = 10 ** (EbN0_dB / 10)
    expected = (3 / 8) * erfc(np.sqrt(2 * lin / 5))
    assert qam16_awgn(lin) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("EbN0_dB", [0, 5, 10, 15])
def test_qam64_awgn_formula(EbN0_dB):
    lin = 10 ** (EbN0_dB / 10)
    expected = (7 / 24) * erfc(np.sqrt(lin / 7))
    assert qam64_awgn(lin) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("EbN0_dB", [0, 5, 10, 15])
def test_bpsk_rayleigh_formula(EbN0_dB):
    lin = 10 ** (EbN0_dB / 10)
    expected = 0.5 * (1 - np.sqrt(lin / (1 + lin)))
    assert bpsk_rayleigh(lin) == pytest.approx(expected, rel=1e-9)


def test_ber_decreases_with_snr():
    """All BER functions must be monotonically decreasing in Eb/N0."""
    lin = 10 ** (np.arange(0, 12) / 10)
    for fn in [bpsk_awgn, qpsk_awgn, qam16_awgn, qam64_awgn, bpsk_rayleigh]:
        ber = fn(lin)
        assert np.all(np.diff(ber) < 0), f"{fn.__name__} is not monotonically decreasing"


def test_ber_bounded():
    """BER must be in (0, 0.5] for all tested SNR values."""
    lin = 10 ** (np.arange(0, 12) / 10)
    for fn in [bpsk_awgn, qpsk_awgn, qam16_awgn, qam64_awgn, bpsk_rayleigh]:
        ber = fn(lin)
        assert np.all(ber > 0), f"{fn.__name__} returned BER <= 0"
        assert np.all(ber <= 0.5), f"{fn.__name__} returned BER > 0.5"


def test_rayleigh_worse_than_awgn():
    """Rayleigh BER must be higher than AWGN BER at same Eb/N0."""
    lin = 10 ** (np.arange(1, 12) / 10)
    assert np.all(bpsk_rayleigh(lin) > bpsk_awgn(lin))


# ---------------------------------------------------------------------------
# Dispatch registry
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mod_name, ch_name, expected_fn", [
    ("BPSK",  "awgn",     bpsk_awgn),
    ("QPSK",  "awgn",     qpsk_awgn),
    ("QAM16", "awgn",     qam16_awgn),
    ("QAM64", "awgn",     qam64_awgn),
    ("BPSK",  "rayleigh", bpsk_rayleigh),
])
def test_get_theory_fn_returns_correct_function(mod_name, ch_name, expected_fn):
    assert get_theory_fn(mod_name, ch_name) is expected_fn


def test_get_theory_fn_raises_on_unknown_pair():
    with pytest.raises(KeyError, match="QAM16.*rayleigh"):
        get_theory_fn("QAM16", "rayleigh")
