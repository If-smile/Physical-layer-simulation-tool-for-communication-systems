# pyberlab — Physical Layer BER Simulation for Communication Systems

A pip-installable Python library for simulating Bit Error Rate (BER) performance of common digital modulation schemes over standard channel models. Designed for wireless communications researchers and engineers who want reproducible, publication-quality BER curves without MATLAB.

---

## Features

- **Modulation schemes**: BPSK, QPSK, 16-QAM (Gray-coded) — 64-QAM and 8-PSK coming in Phase 4
- **Channel models**: AWGN, Rayleigh flat fading
- **Theoretical baselines**: Closed-form BER formulas for every modulation/channel pair, auto-paired via dispatch registry
- **Reproducibility**: All simulation entry points accept a `seed` parameter via `np.random.default_rng`
- **Adaptive sampling**: Automatically scales sample count per SNR point to ensure statistical reliability
- **Export**: Results to CSV; BER curves to publication-ready plots

---

## Installation

```bash
pip install -e .
```

Requires Python 3.9+ and numpy, scipy, matplotlib (installed automatically).

---

## Quick Start

```python
import numpy as np
from pyberlab.modulation import BPSK
from pyberlab.channel import awgn, rayleigh
from pyberlab.simulation import run_simulation
from pyberlab.plot import plot_ber

EbN0_dB = np.arange(0, 13)

res_awgn     = run_simulation(BPSK(), awgn,     EbN0_dB, seed=42, csv_path="bpsk_awgn.csv")
res_rayleigh = run_simulation(BPSK(), rayleigh,  EbN0_dB, seed=42, csv_path="bpsk_rayleigh.csv")

plot_ber(
    [res_awgn, res_rayleigh],
    ["BPSK AWGN", "BPSK Rayleigh"],
    title="BPSK: AWGN vs Rayleigh Fading",
    save_path="ber_comparison.png",
)
```

---

## Project Structure

```
pyberlab/
├── pyberlab/
│   ├── modulation/       # BPSK, QPSK, QAM16, QAM64 (+ Modulator ABC)
│   ├── channel/          # AWGN, Rayleigh
│   ├── simulation/       # run_simulation, metrics
│   ├── theory/           # Analytical BER formulas + dispatch registry
│   └── plot/             # BER curve generation
├── examples/
├── tests/                # 70 tests, CI on Python 3.9–3.12
├── pyproject.toml
└── requirements.txt
```

---

## Roadmap

See [TODO.md](TODO.md) for the full implementation plan.

| Phase | Scope | Status |
|---|---|---|
| 0 | Directory structure, pyproject.toml, pip install | ✅ Done |
| 0.5 | Modulator ABC, ruff config, rng convention | ✅ Done |
| 1 | BPSK, QPSK, 16-QAM, AWGN, theory BER, CI | ✅ Done |
| 2 | Rayleigh channel, AWGN vs Rayleigh comparison | ✅ Done |
| 3 | Simulation framework, CSV export, plots | ✅ Done |
| 4 | 64-QAM, 8-PSK, unit tests | Planned |
| 5 | Docs, notebooks, PyPI release | Planned |

---

## Requirements

- Python 3.9+
- numpy >= 1.24
- scipy >= 1.10
- matplotlib >= 3.7

---

## Background

This project fills the gap between MATLAB-based simulation tools and scattered teaching scripts. The goal is a clean, testable Python implementation with results that can be verified against known analytical BER formulas — useful both for research prototyping and for learning digital communications fundamentals.

---

## License

MIT
