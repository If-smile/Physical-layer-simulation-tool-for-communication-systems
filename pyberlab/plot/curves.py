"""Standard BER curve plotting utilities."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_ber(
    results_list: list[dict],
    labels: list[str],
    *,
    show_theory: bool = True,
    title: str = "BER vs Eb/N0",
    save_path: str | Path | None = None,
    show: bool = True,
) -> plt.Figure:
    """Plot one or more BER curves on a single semilogy axes.

    Parameters
    ----------
    results_list:
        List of result dicts as returned by :func:`run_simulation`.
    labels:
        Display label for each result dict (same order).
    show_theory:
        If ``True``, overlay dashed theoretical curves.
    title:
        Plot title.
    save_path:
        If provided, save the figure to this path (PNG/PDF/SVG auto-detected
        from extension).
    show:
        If ``True``, call ``plt.show()`` after plotting.

    Returns
    -------
    matplotlib.figure.Figure
    """
    if len(results_list) != len(labels):
        raise ValueError("results_list and labels must have the same length")
    if not results_list:
        raise ValueError("results_list must not be empty")

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for idx, (res, label) in enumerate(zip(results_list, labels)):
        color = colors[idx % len(colors)]
        x = np.array(res["EbN0_dB"])
        ber_sim = np.array(res["ber_sim"])

        # Replace zero BERs with NaN so they don't drag the log axis down
        ber_sim_plot = np.where(ber_sim > 0, ber_sim, np.nan)

        ax.semilogy(x, ber_sim_plot, "o-", color=color, label=f"{label} (sim)")

        if show_theory:
            ber_th = np.array(res["ber_theory"])
            ax.semilogy(x, ber_th, "--", color=color,
                        alpha=0.7, label=f"{label} (theory)")

    ax.set_xlabel("Eb/N0 (dB)", fontsize=12)
    ax.set_ylabel("BER", fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(fontsize=10)
    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    if show:
        plt.show()

    return fig
