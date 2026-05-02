# pyberlab — Physical Layer BER Simulation for Communication Systems

A pip-installable Python library for simulating Bit Error Rate (BER) performance of common digital modulation schemes over standard channel models. Designed for wireless communications researchers and engineers who want reproducible, publication-quality BER curves without MATLAB.

---

## Features

- **Modulation schemes**: BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM (Gray-coded)
- **Channel models**: AWGN, Rayleigh flat fading, Rician (planned)
- **Theoretical baselines**: Closed-form BER formulas for every modulation/channel pair
- **Adaptive sampling**: Automatically scales sample count per SNR point to ensure statistical reliability
- **Export**: Results to CSV; BER curves to standard publication-ready plots

---

## Planned Project Structure

```
pyberlab/
├── pyberlab/
│   ├── modulation/       # BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM
│   ├── channel/          # AWGN, Rayleigh
│   ├── simulation/       # Main simulation loop, metrics
│   ├── theory/           # Analytical BER formulas
│   └── plot/             # BER curve generation
├── examples/             # Jupyter notebooks
├── tests/
├── pyproject.toml
└── requirements.txt
```

---

## Quick Start (prototype)

The current `test.py` demonstrates BPSK over AWGN with adaptive sample sizing:

```python
import numpy as np
from scipy.special import erfc
import matplotlib.pyplot as plt

# Run: python test.py
```

Once the package is installable, the interface will look like:

```python
from pyberlab.modulation.psk import BPSK
from pyberlab.channel.awgn import awgn
from pyberlab.simulation.runner import run_simulation
import numpy as np

results = run_simulation(
    modulator=BPSK(),
    channel_fn=awgn,
    EbN0_dB_range=np.arange(0, 11)
)
```

---

## Roadmap

See [TODO.md](TODO.md) for the full implementation plan.

| Phase | Scope | Status |
|---|---|---|
| Prototype | BPSK + AWGN, adaptive sampling | Done |
| Phase 1 | QPSK, 16-QAM, package structure | Planned |
| Phase 2 | Rayleigh channel, AWGN vs Rayleigh comparison | Planned |
| Phase 3 | Simulation framework, CSV export, plots | Planned |
| Phase 4 | 64-QAM, unit tests | Planned |
| Phase 5 | Docs, notebooks, PyPI release | Planned |

---

## Requirements

- Python 3.9+
- numpy
- scipy
- matplotlib

---

## Background

This project fills the gap between MATLAB-based simulation tools and scattered teaching scripts. The goal is a clean, testable Python implementation with results that can be verified against known analytical BER formulas — useful both for research prototyping and for learning digital communications fundamentals.

---

## License

MIT
