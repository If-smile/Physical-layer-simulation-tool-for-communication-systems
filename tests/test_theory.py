"""Tests for theoretical BER formulas and dispatch registry."""

import numpy as np
import pytest
from scipy.special import erfc

from pyberlab.theory.ber import (
    bpsk_awgn,
    bpsk_rayleigh,
    get_theory_fn,
    psk8_awgn,
    psk8_rayleigh,
    qam16_awgn,
    qam16_rayleigh,
    qam64_awgn,
    qam64_rayleigh,
    qpsk_awgn,
    qpsk_rayleigh,
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


def test_psk8_awgn_exact_values():
    lin = 10 ** (np.array([0, 5, 10, 15]) / 10)
    expected = [
        0.1226927610785051,
        0.0318614414208807,
        0.001011395320988671,
        4.516092535387308e-08,
    ]
    np.testing.assert_allclose(psk8_awgn(lin), expected, rtol=1e-10)


def test_qam16_awgn_exact_values():
    lin = 10 ** (np.array([0, 5, 10, 15]) / 10)
    expected = [
        0.1409816350668416,
        0.04189276004646234,
        0.001754150617892711,
        1.841855511268188e-07,
    ]
    np.testing.assert_allclose(qam16_awgn(lin), expected, rtol=1e-12)


def test_qam64_awgn_exact_values():
    lin = 10 ** (np.array([0, 5, 10, 15]) / 10)
    expected = [
        0.1998413523001502,
        0.1007916072951138,
        0.02653270879756516,
        0.000772472180420463,
    ]
    np.testing.assert_allclose(qam64_awgn(lin), expected, rtol=1e-12)


def test_exact_qam64_baseline_corrects_low_snr_approximation():
    """The common high-SNR approximation underestimates BER at 0 dB."""
    approximation = (7 / 24) * erfc(np.sqrt(1 / 7))
    assert qam64_awgn(1.0) > approximation


@pytest.mark.parametrize("EbN0_dB", [0, 5, 10, 15])
def test_bpsk_rayleigh_formula(EbN0_dB):
    lin = 10 ** (EbN0_dB / 10)
    expected = 0.5 * (1 - np.sqrt(lin / (1 + lin)))
    assert bpsk_rayleigh(lin) == pytest.approx(expected, rel=1e-9)


def test_ber_decreases_with_snr():
    """All BER functions must be monotonically decreasing in Eb/N0."""
    lin = 10 ** (np.arange(0, 12) / 10)
    for fn in [
        bpsk_awgn,
        qpsk_awgn,
        psk8_awgn,
        qam16_awgn,
        qam64_awgn,
        bpsk_rayleigh,
    ]:
        ber = fn(lin)
        assert np.all(np.diff(ber) < 0), f"{fn.__name__} is not monotonically decreasing"


def test_ber_bounded():
    """BER must be in (0, 0.5] for all tested SNR values."""
    lin = 10 ** (np.arange(0, 12) / 10)
    for fn in [
        bpsk_awgn,
        qpsk_awgn,
        psk8_awgn,
        qam16_awgn,
        qam64_awgn,
        bpsk_rayleigh,
    ]:
        ber = fn(lin)
        assert np.all(ber > 0), f"{fn.__name__} returned BER <= 0"
        assert np.all(ber <= 0.5), f"{fn.__name__} returned BER > 0.5"


def test_rayleigh_worse_than_awgn():
    """Rayleigh BER must be higher than AWGN BER at same Eb/N0."""
    lin = 10 ** (np.arange(1, 12) / 10)
    assert np.all(bpsk_rayleigh(lin) > bpsk_awgn(lin))


def test_qpsk_rayleigh_equals_bpsk_rayleigh():
    lin = np.array([1.0, 3.162, 10.0])
    np.testing.assert_allclose(qpsk_rayleigh(lin), bpsk_rayleigh(lin))


def test_psk8_rayleigh_values():
    lin = 10 ** (np.array([0, 5, 10, 15]) / 10)
    expected = [
        0.1818181376761986,
        0.09154808415308803,
        0.0366742047250139,
        0.01273965337615775,
    ]
    np.testing.assert_allclose(psk8_rayleigh(lin), expected, rtol=1e-9)


def test_qam_rayleigh_values():
    lin = 10 ** (np.array([0, 5, 10, 15]) / 10)
    np.testing.assert_allclose(
        qam16_rayleigh(lin),
        [0.197573957989034, 0.1031315911194764, 0.04237097119324414, 0.01489209062604484],
        rtol=1e-12,
    )
    np.testing.assert_allclose(
        qam64_rayleigh(lin),
        [0.2470632661919897, 0.1535529447382122, 0.07667955322432671, 0.03061624049339226],
        rtol=1e-12,
    )


# ---------------------------------------------------------------------------
# Dispatch registry
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mod_name, ch_name, expected_fn", [
    ("BPSK",  "awgn",     bpsk_awgn),
    ("QPSK",  "awgn",     qpsk_awgn),
    ("PSK8",  "awgn",     psk8_awgn),
    ("QAM16", "awgn",     qam16_awgn),
    ("QAM64", "awgn",     qam64_awgn),
    ("BPSK",  "rayleigh", bpsk_rayleigh),
    ("QPSK",  "rayleigh", qpsk_rayleigh),
    ("PSK8",  "rayleigh", psk8_rayleigh),
    ("QAM16", "rayleigh", qam16_rayleigh),
    ("QAM64", "rayleigh", qam64_rayleigh),
])
def test_get_theory_fn_returns_correct_function(mod_name, ch_name, expected_fn):
    assert get_theory_fn(mod_name, ch_name) is expected_fn


def test_get_theory_fn_raises_on_unknown_pair():
    with pytest.raises(KeyError, match="NotAModulator.*rayleigh"):
        get_theory_fn("NotAModulator", "rayleigh")
