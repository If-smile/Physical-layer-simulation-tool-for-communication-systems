Getting started
===============

Installation
------------

Install the package from the repository root:

.. code-block:: console

   pip install -e .

Install the documentation dependencies when building these pages locally:

.. code-block:: console

   pip install -e ".[docs]"

Quick example
-------------

The simulation runner selects the matching theoretical BER function from the
modulator and channel names. A fixed seed makes the Monte Carlo result
reproducible.

.. code-block:: python

   import numpy as np

   from pyberlab.channel import awgn
   from pyberlab.modulation import QPSK
   from pyberlab.plot import plot_ber
   from pyberlab.simulation import run_simulation

   ebn0_db = np.arange(0, 11, 2)
   result = run_simulation(
       QPSK(),
       awgn,
       ebn0_db,
       seed=42,
       min_errors=100,
       max_bits=1_000_000,
       csv_path="outputs/qpsk_awgn.csv",
   )
   plot_ber(
       [result],
       ["QPSK over AWGN"],
       save_path="outputs/qpsk_awgn.png",
   )

Building the documentation
--------------------------

Treat warnings as errors so invalid cross-references and malformed docstrings
are caught before publishing:

.. code-block:: console

   python -m sphinx -W --keep-going -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` after the command completes.
