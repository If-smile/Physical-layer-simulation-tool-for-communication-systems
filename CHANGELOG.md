# Changelog

All notable changes to `pyberlab` are recorded in this file. The project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), and this changelog is
structured using the principles of [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

Future changes made after the `0.1.0` release will be recorded here.

## 0.1.0 - Unreleased

This is the planned initial public release.

### Added

- A common modulator interface with unit-average-power BPSK, Gray-coded QPSK,
  8-PSK, 16-QAM, and 64-QAM implementations.
- Additive white Gaussian noise and independent coherent Rayleigh flat-fading
  channel models with reproducible NumPy random generators.
- Exact hard-decision AWGN BER baselines for every supported modulation.
- Coherent Rayleigh BER baselines using closed-form expressions or numerical
  averaging over the instantaneous-SNR distribution.
- An adaptive Monte Carlo simulation runner with deterministic seeding, error
  counting, theoretical dispatch, sample caps, and CSV export.
- Semilog BER plotting for simulated and theoretical results.
- Executable BPSK/AWGN, QPSK/AWGN, Rayleigh comparison, and modulation
  comparison notebooks.
- Sphinx guides and generated API documentation for every public export.
- Automated Ruff, Python 3.9-3.12 test, and strict documentation checks in
  GitHub Actions.

### Validation

- 107 unit, integration, reproducibility, input-validation, and
  simulation-to-theory tests.

### Known limitations

- Simulations are uncoded and use hard-decision receivers.
- Rayleigh fading is independent per symbol and assumes perfect receiver channel
  knowledge.
- Rician fading, OFDM, channel coding, and MIMO are not included in this release.
