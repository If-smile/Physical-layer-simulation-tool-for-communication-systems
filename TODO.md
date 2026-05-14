# TODO

## Phase 0 — Project Scaffolding (Done)

- [x] Set up directory structure: `pyberlab/modulation/`, `channel/`, `simulation/`, `theory/`, `plot/`, `tests/`, `examples/`
- [x] Write `pyproject.toml` so the package is locally pip-installable (`pip install -e .`)
- [x] Write `requirements.txt` (numpy, scipy, matplotlib)
- [x] Migrate prototype `test.py` → `examples/bpsk_awgn_prototype.py`
- [x] Verify `pip install -e .` works and all subpackages import

## Phase 0.5 — Quality Foundations (Done)

- [x] Add `__version__ = "0.1.0"` to `pyberlab/__init__.py`, aligned with `pyproject.toml`
- [x] Add `[tool.ruff]` section to `pyproject.toml`; commit baseline lint config so style stays consistent from day one
- [x] Define a `Modulator` abstract base class in `pyberlab/modulation/base.py` with `bits_per_symbol`, `modulate`, `demodulate` interface — BPSK/QPSK/QAM all inherit from it
- [x] Decide reproducibility convention: all simulation entry points accept `seed: int | None`, internally use `np.random.default_rng(seed)` instead of global `np.random` (apply this rule from the very first line of Phase 1 code)

## Phase 1 — Package Foundation (Done)

- [x] Implement `modulation/psk.py`: `BPSK`, `QPSK` classes (subclass `Modulator`) with `modulate` / `demodulate` methods
- [x] Implement `modulation/qam.py`: `QAM` class supporting 16-QAM (Gray-coded, normalized power)
- [x] Implement `theory/ber.py`: `bpsk_awgn`, `qpsk_awgn`, `qam16_awgn` analytical formulas
- [x] Implement `channel/awgn.py`: complex and real noise injection (accept optional `rng` parameter for reproducibility)
- [x] Build `(ModulatorClass, channel_fn) → theory_fn` dispatch registry in `theory/ber.py` so `run_simulation` can auto-pair simulation with theoretical baseline
- [x] Round-trip sanity check: `demodulate(modulate(bits))` must return `bits` exactly when no noise is added (catches bugs earlier than BER tests)
- [x] Verify QPSK BER matches theory (should equal BPSK — same Eb/N0 per bit)
- [x] Verify 16-QAM BER matches `(3/8) * erfc(sqrt(2 * EbN0 / 5))`
- [x] Set up GitHub Actions CI: run `pytest` on every push (Python 3.9–3.12 matrix)

## Phase 2 — Rayleigh Channel (Done)

- [x] Implement `channel/rayleigh.py`: per-symbol complex Gaussian fading with coherent equalization
- [x] Add `bpsk_rayleigh` formula to `theory/ber.py`
- [ ] Run AWGN vs Rayleigh comparison plot for BPSK (this becomes the primary demo figure)
- [x] Confirm simulated Rayleigh BER tracks the theoretical curve `0.5 * (1 - sqrt(EbN0 / (1 + EbN0)))`

## Phase 3 — Simulation Framework (Weeks 5–6)

- [ ] Implement `simulation/runner.py`: `run_simulation(modulator, channel_fn, EbN0_dB_range, ...)` unified interface
- [ ] Migrate adaptive sample sizing logic from `test.py` into `runner.py`
- [ ] Implement `simulation/metrics.py`: BER calculation and basic statistics
- [ ] Implement `plot/curves.py`: generate and save standard BER plots (semilogy, grid, legend)
- [ ] Add CSV export to `run_simulation` results dict
- [ ] End-to-end test: one function call produces a complete BPSK/AWGN experiment with plot and CSV

## Phase 4 — 64-QAM and Testing (Weeks 7–8)

- [ ] Extend `modulation/qam.py` to support 64-QAM
- [ ] Add `qam64_awgn` formula to `theory/ber.py`
- [ ] Verify 64-QAM BER matches `(7/24) * erfc(sqrt(EbN0 / 7))`
- [ ] Write `tests/test_modulation.py`: round-trip bit integrity, power normalization
- [ ] Write `tests/test_channel.py`: noise power matches specified Eb/N0
- [ ] Write `tests/test_simulation.py`: high-SNR BER → 0; low-SNR BER → 0.5
- [ ] Implement `modulation/psk.py`: 8-PSK (Gray-coded)

## Phase 5 — Documentation and Release (Weeks 9–10)

- [ ] Write full README with installation, quick-start, and modulation comparison BER plot
- [ ] Create `examples/bpsk_awgn.ipynb`
- [ ] Create `examples/qpsk_awgn.ipynb`
- [ ] Create `examples/rayleigh_comparison.ipynb` (AWGN vs Rayleigh for all modulation orders)
- [ ] Create `examples/modulation_comparison.ipynb` (all schemes on one plot)
- [ ] Set up `docs/` (at minimum: module docstrings + auto-generated API reference)
- [ ] Publish to PyPI
- [ ] Post to r/signal processing and Papers With Code

## Backlog (Post-v1)

- [ ] Rician channel model
- [ ] OFDM multi-carrier simulation
- [ ] Convolutional code BER (coding gain demo)
- [ ] MIMO channel model
