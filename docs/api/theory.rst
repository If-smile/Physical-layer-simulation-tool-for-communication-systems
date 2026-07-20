BER theory
==========

All theory functions accept Eb/N0 in linear units rather than decibels. Scalar
inputs return scalar BER values and NumPy arrays return arrays of matching shape.

AWGN
----

.. autofunction:: pyberlab.theory.bpsk_awgn

.. autofunction:: pyberlab.theory.qpsk_awgn

.. autofunction:: pyberlab.theory.psk8_awgn

.. autofunction:: pyberlab.theory.qam16_awgn

.. autofunction:: pyberlab.theory.qam64_awgn

Coherent Rayleigh fading
------------------------

.. autofunction:: pyberlab.theory.bpsk_rayleigh

.. autofunction:: pyberlab.theory.qpsk_rayleigh

.. autofunction:: pyberlab.theory.psk8_rayleigh

.. autofunction:: pyberlab.theory.qam16_rayleigh

.. autofunction:: pyberlab.theory.qam64_rayleigh

Dispatch
--------

.. autofunction:: pyberlab.theory.get_theory_fn
