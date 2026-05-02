import numpy as np
from scipy.special import erfc
import matplotlib.pyplot as plt

def bpsk_modulate(bits):
    return 2 * bits - 1

def bpsk_demodulate(received):
    return (received > 0).astype(int)

def awgn(signal, EbN0_linear, bits_per_symbol=1):
    noise_power = 1 / (2 * bits_per_symbol * EbN0_linear)
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise

def calculate_ber(tx_bits, rx_bits):
    errors = np.sum(tx_bits != rx_bits)
    return errors / len(tx_bits)

EbN0_dB_range = np.arange(0, 11)
ber_sim = []
ber_theory = []

for EbN0_dB in EbN0_dB_range:
    EbN0_linear = 10 ** (EbN0_dB / 10)
    
    n_bits = max(100000, int(100 / (0.5 * erfc(np.sqrt(EbN0_linear)))))
    n_bits = min(n_bits, 10000000)  
    tx_bits = np.random.randint(0, 2, n_bits)
    tx_symbols = bpsk_modulate(tx_bits)
    rx_symbols = awgn(tx_symbols, EbN0_linear)
    rx_bits = bpsk_demodulate(rx_symbols)
    
    ber_sim.append(calculate_ber(tx_bits, rx_bits))
    ber_theory.append(0.5 * erfc(np.sqrt(EbN0_linear)))

plt.semilogy(EbN0_dB_range, ber_sim, 'o-', label='Simulation')
plt.semilogy(EbN0_dB_range, ber_theory, '--', label='Theory')
plt.xlabel('Eb/N0 (dB)')
plt.ylabel('BER')
plt.legend()
plt.grid(True)
plt.show()