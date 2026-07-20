# pyberlab — Physical-Layer BER Simulation

`pyberlab` is a Python library for simulating bit-error-rate (BER)
performance of digital modulation schemes over common wireless channel models.
It is intended for reproducible communication-systems experiments without a
MATLAB dependency.

## Features

- Modulation: BPSK, QPSK, Gray-coded 8-PSK, 16-QAM, and 64-QAM
- Channels: AWGN and independent Rayleigh flat fading with perfect coherent
  equalisation
- Theory baselines: exact hard-decision BER for the supported AWGN schemes;
  Rayleigh BER for every implemented modulation
- Reproducible Monte-Carlo experiments through `numpy.random.Generator` seeds
- Adaptive sample counts based on the theoretical BER, with a configurable cap
- CSV export and publication-ready semilog BER plots
- Parameter validation that prevents truncated bit streams and invalid SNRs

## Installation

```bash
pip install -e .
```

For development tools and tests:

```bash
pip install -e ".[dev]"
```

Python 3.9+ is required.

## Quick start

```python
import numpy as np

from pyberlab.channel import awgn, rayleigh
from pyberlab.modulation import BPSK, PSK8, QAM64
from pyberlab.plot import plot_ber
from pyberlab.simulation import run_simulation

EbN0_dB = np.arange(0, 13)

bpsk_awgn = run_simulation(BPSK(), awgn, EbN0_dB, seed=42)
bpsk_rayleigh = run_simulation(BPSK(), rayleigh, EbN0_dB, seed=42)
qam64_awgn = run_simulation(QAM64(), awgn, EbN0_dB, seed=42)
psk8_rayleigh = run_simulation(PSK8(), rayleigh, EbN0_dB, seed=42)

plot_ber(
    [bpsk_awgn, bpsk_rayleigh, qam64_awgn, psk8_rayleigh],
    ["BPSK AWGN", "BPSK Rayleigh", "64-QAM AWGN", "8-PSK Rayleigh"],
    title="BER comparison",
    save_path="outputs/ber_comparison.png",
)
```

Each result dictionary contains `EbN0_dB`, simulated and theoretical BER,
the number of simulated bits, and error counts. Pass `csv_path` to
`run_simulation` to persist the result table.

## Examples

- [`examples/bpsk_awgn.ipynb`](examples/bpsk_awgn.ipynb) presents a complete,
  reproducible BPSK/AWGN experiment with constellation, statistics, CSV export,
  and BER plotting.
- [`examples/qpsk_awgn.ipynb`](examples/qpsk_awgn.ipynb) demonstrates the
  Gray-coded QPSK constellation, independent I/Q decisions, and its theoretical
  BER equivalence with BPSK.
- [`examples/rayleigh_comparison.ipynb`](examples/rayleigh_comparison.ipynb)
  compares every implemented modulation over AWGN and coherent Rayleigh fading,
  including target-BER fading penalties and per-experiment CSV exports.
- [`examples/modulation_comparison.ipynb`](examples/modulation_comparison.ipynb)
  compares all supported constellations and their AWGN BER performance, including
  the Eb/N0 required to reach a target BER and the penalty relative to BPSK.

## Theory model

For BPSK and QPSK, the AWGN and coherent-Rayleigh formulas are closed form.
For Gray-coded 8-PSK, the exact AWGN baseline integrates the receiver's angular
decision regions, and its Rayleigh baseline averages over instantaneous SNR.
For Gray-coded 16-QAM and 64-QAM, the AWGN baseline exactly enumerates the
hard-decision PAM regions and Gray-label Hamming distances. Their Rayleigh
baseline numerically averages that exact conditional BER over the exponential
instantaneous-SNR distribution.

The formulas therefore match the package's hard-decision receiver model at low
SNR as well as high SNR. They are not the common high-SNR QAM approximations.

## Project layout

```
pyberlab/
├── modulation/       # Modulator ABC, BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM
├── channel/          # AWGN and coherent Rayleigh flat fading
├── simulation/       # Runner, BER metrics, CSV output
├── theory/           # Analytical and numerical BER baselines
└── plot/             # BER curve generation
examples/             # Executable notebooks and standalone prototypes
tests/                # Unit and end-to-end tests
```

## Status and roadmap

The initial library, Rayleigh support, simulation framework, CSV export,
plotting, 8-PSK, and 64-QAM are complete. Remaining near-term work is example
notebooks, API documentation, and a PyPI release. See [TODO.md](TODO.md)
for the detailed plan.

## License

MIT
