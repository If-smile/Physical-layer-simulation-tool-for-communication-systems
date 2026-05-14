# pyberlab — Physical Layer BER Simulation for Communication Systems

A pip-installable Python library for simulating Bit Error Rate (BER) performance of common digital modulation schemes over standard channel models. Designed for wireless communications researchers and engineers who want reproducible, publication-quality BER curves without MATLAB.

---

## Features

- **Modulation schemes**: BPSK, QPSK, 16-QAM (Gray-coded) — 64-QAM and 8-PSK coming in Phase 4
- **Channel models**: AWGN — Rayleigh flat fading coming in Phase 2
- **Theoretical baselines**: Closed-form BER formulas for every modulation/channel pair, auto-paired via dispatch registry
- **Reproducibility**: All simulation entry points accept a `seed` parameter via `np.random.default_rng`
- **Adaptive sampling**: Automatically scales sample count per SNR point to ensure statistical reliability *(Phase 3)*
- **Export**: Results to CSV; BER curves to standard publication-ready plots *(Phase 3)*

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
from pyberlab.modulation import BPSK, QPSK, QAM16
from pyberlab.channel import awgn
from pyberlab.theory import bpsk_awgn

rng = np.random.default_rng(42)
mod = BPSK()

EbN0_dB = 4.0
EbN0_lin = 10 ** (EbN0_dB / 10)

bits = rng.integers(0, 2, 100_000)
rx = awgn(mod.modulate(bits), EbN0_lin, mod.bits_per_symbol, rng=rng)
rx_bits = mod.demodulate(rx)

ber_sim = float(np.mean(bits != rx_bits))
ber_theory = bpsk_awgn(EbN0_lin)
print(f"BER  sim={ber_sim:.4f}  theory={ber_theory:.4f}")
```

Once the simulation framework (Phase 3) is complete, the interface simplifies to:

```python
from pyberlab.simulation.runner import run_simulation

results = run_simulation(
    modulator=BPSK(),
    channel_fn=awgn,
    EbN0_dB_range=np.arange(0, 11),
    seed=42,
)
```

---

## Project Structure

```
pyberlab/
├── pyberlab/
│   ├── modulation/       # BPSK, QPSK, QAM16, QAM64 (+ Modulator ABC)
│   ├── channel/          # AWGN (Rayleigh in Phase 2)
│   ├── simulation/       # run_simulation, metrics (Phase 3)
│   ├── theory/           # Analytical BER formulas + dispatch registry
│   └── plot/             # BER curve generation (Phase 3)
├── examples/
├── tests/
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
| 2 | Rayleigh channel, AWGN vs Rayleigh comparison | Planned |
| 3 | Simulation framework, CSV export, plots | Planned |
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
