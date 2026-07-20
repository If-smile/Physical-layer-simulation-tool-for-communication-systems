# TODO

## Completed foundations

- [x] Package structure, editable installation, dependencies, and CI
- [x] Modulator abstraction and reproducible RNG convention
- [x] BPSK, QPSK, Gray-coded 8-PSK, 16-QAM, and 64-QAM
- [x] AWGN and coherent independent Rayleigh flat-fading channels
- [x] Exact hard-decision AWGN BER baselines for all implemented modulations
- [x] Rayleigh BER baselines and dispatch entries for all implemented modulations
- [x] Unified adaptive simulation runner, BER metrics, CSV export, and plots
- [x] Input validation for bit streams, channels, sampling parameters, and plots
- [x] Unit, integration, reproducibility, and simulation-to-theory tests

## Next: modulation and examples

- [ ] Create `examples/bpsk_awgn.ipynb`
- [ ] Create `examples/qpsk_awgn.ipynb`
- [ ] Create `examples/rayleigh_comparison.ipynb`
- [ ] Create `examples/modulation_comparison.ipynb`

## Documentation and release

- [ ] Add module docstrings and generated API reference
- [ ] Publish the package to PyPI
- [ ] Add versioned release notes and a changelog

## Backlog

- [ ] Rician channel model
- [ ] OFDM multi-carrier simulation
- [ ] Convolutional-code BER and coding-gain experiments
- [ ] MIMO channel models
