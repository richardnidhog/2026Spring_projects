import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as sp_stats

_SIM_DIR = str(Path(__file__).parent / "2020")
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
os.environ["PYTHONPATH"] = _SIM_DIR + os.pathsep + os.environ.get("PYTHONPATH", "")

import PR_final_project_revised as sim  # noqa: E402

OUTPUT_DIR = Path(__file__).parent / "test_images"
OUTPUT_DIR.mkdir(exist_ok=True)

def _ci95(arr: np.ndarray) -> tuple[float, float]:
    """
    Return the 95% t-distribution confidence interval for the mean of *arr*.

    Uses the t-distribution (exact for any sample size).  Returns ``(nan, nan)``
    for empty arrays and ``(value, value)`` for single-element arrays.

    :param arr: 1-D array of numeric values.
    :return: (lower_bound, upper_bound) of the 95% CI.

    >>> import numpy as np
    >>> lo, hi = _ci95(np.array([1.0, 2.0, 3.0]))
    >>> lo < 2.0 < hi
    True
    >>> _ci95(np.array([]))
    (nan, nan)
    >>> _ci95(np.array([5.0]))
    (5.0, 5.0)
    """
    n = len(arr)
    if n == 0:
        return float("nan"), float("nan")
    if n == 1:
        return float(arr[0]), float(arr[0])
    lo, hi = sp_stats.t.interval(
        0.95,
        df=n - 1,
        loc=float(np.mean(arr)),
        scale=float(sp_stats.sem(arr)),
    )
    return float(lo), float(hi)

def report_stats(
    overflow_days: list,
    perc_vacant_beds: list,
    n_simulations: int,
) -> dict:
    """
    Compute and print a full statistical summary of Monte Carlo results.

    For **overflow day** (only runs that overflowed): mean, 95% CI, 5th/95th pct.
    For **bed vacancy** (all runs, 0 when overflowed): mean, 95% CI, 5th/95th pct.

    :param overflow_days:     Days beds first reached zero, one entry per run that overflowed.
    :param perc_vacant_beds:  Percent vacant beds at simulation end (0.0 for overflowed runs).
    :param n_simulations:     Total number of Monte Carlo runs.
    :return: ``{"overflow": {...}, "vacancy": {...}}``

    >>> stats = report_stats([52, 55, 58], [0.0, 0.0, 0.0], 3)  # doctest: +ELLIPSIS
    ...
    >>> set(stats.keys()) == {"overflow", "vacancy"}
    True
    >>> stats["overflow"]["n_overflowed"]
    3
    """
    if overflow_days:
        od = np.array(overflow_days, dtype=float)
        lo, hi = _ci95(od)
        overflow_summary: dict = {
            "n_overflowed":  len(overflow_days),
            "prob_overflow": len(overflow_days) / n_simulations,
            "mean":          float(np.mean(od)),
            "ci95":          (lo, hi),
            "p5":            float(np.percentile(od,  5)),
            "p95":           float(np.percentile(od, 95)),
        }
    else:
        overflow_summary = {
            "n_overflowed":  0,
            "prob_overflow": 0.0,
        }

    va = np.array(perc_vacant_beds, dtype=float)
    lo_v, hi_v = _ci95(va)
    vacancy_summary: dict = {
        "mean": float(np.mean(va)),
        "ci95": (lo_v, hi_v),
        "p5":   float(np.percentile(va,  5)),
        "p95":  float(np.percentile(va, 95)),
    }

    ov = overflow_summary
    n_ov = ov["n_overflowed"]
    print("\n── Overflow ─────────────────────────────────────────────────")
    print(f"  Overflow probability : {ov['prob_overflow']:.1%}"
          f"  ({n_ov} / {n_simulations} runs)")
    if overflow_days:
        print(f"  First-overflow day   : mean = {ov['mean']:.1f} days")
        print(f"                         95% CI  [{ov['ci95'][0]:.1f},  {ov['ci95'][1]:.1f}]")
        print(f"                         5th pct {ov['p5']:.0f}  /  95th pct {ov['p95']:.0f}")

    vs = vacancy_summary
    print("\n── Bed Vacancy at Simulation End ────────────────────────────")
    print(f"  Mean    {vs['mean']:.2f}%"
          f"   95% CI [{vs['ci95'][0]:.2f}%,  {vs['ci95'][1]:.2f}%]")
    print(f"  5th pct {vs['p5']:.2f}%   95th pct {vs['p95']:.2f}%")
    print("─────────────────────────────────────────────────────────────\n")

    return {"overflow": ov, "vacancy": vs}


# Plotting

def _save_plots(
    label: str,
    overflow_days: list,
    beds_and_days: list,
    perc_vacant: list,
    summary: dict,
) -> None:
    """Save the three standard diagnostic plots for one scenario, annotated with statistics."""
    safe = label.replace(" ", "_")
    n = len(beds_and_days)
    # lower alpha for large simulation counts to avoid overplotting
    alpha = float(np.clip(50.0 / n, 0.04, 0.5))

    fig, ax = plt.subplots(figsize=(8, 5))
    for beds, days in beds_and_days:
        ax.plot(days, beds, alpha=alpha, linewidth=0.5, color="steelblue")
    ax.set_xlabel("Number of Days")
    ax.set_ylabel("Available Beds")
    ax.set_title(f"{label}: Available Number of Beds")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-beds-vs-days.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ov = summary["overflow"]
    if overflow_days:
        ax.hist(overflow_days, bins=10, color="steelblue", edgecolor="white")
        ax.axvline(ov["mean"], color="crimson", linestyle="--", linewidth=1.5,
                   label=f"Mean = {ov['mean']:.1f} d")
        ax.axvspan(ov["ci95"][0], ov["ci95"][1], alpha=0.15, color="crimson",
                   label=f"95% CI  [{ov['ci95'][0]:.1f}, {ov['ci95'][1]:.1f}]")
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.5, "No overflow events", transform=ax.transAxes,
                ha="center", va="center", fontsize=13, color="seagreen",
                fontweight="bold")
    ax.set_xlabel("Day of First Bed Overflow")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{label}: First Day Beds Reach Zero  "
                 f"(P={ov['prob_overflow']:.1%})")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-overflow-hist.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    vs = summary["vacancy"]
    ax.hist(perc_vacant, bins=15, color="steelblue", edgecolor="white")
    ax.axvline(vs["mean"], color="crimson", linestyle="--", linewidth=1.5,
               label=f"Mean = {vs['mean']:.2f}%")
    if not (np.isnan(vs["ci95"][0]) or vs["ci95"][0] == vs["ci95"][1]):
        ax.axvspan(vs["ci95"][0], vs["ci95"][1], alpha=0.15, color="crimson",
                   label=f"95% CI  [{vs['ci95'][0]:.2f}%, {vs['ci95'][1]:.2f}%]")
    ax.legend(fontsize=8)
    ax.set_xlabel("% Vacant Beds at Simulation End")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{label}: Percent Vacant Beds")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{safe}-vacancy-hist.png", dpi=150)
    plt.close(fig)

    print(f"  Plots saved → {OUTPUT_DIR / safe}-*.png")

def run_and_report(
    label: str,
    population: int,
    total_beds: int,
    n_simulations: int,
    number_of_days: int,
    do_threading: bool = True,
) -> dict:
    """
    Run one simulation scenario, print its statistics, and save annotated plots.

    :param label:          Scenario name used in plot titles and file prefixes.
    :param population:     Total regional population.
    :param total_beds:     Total hospital beds available.
    :param n_simulations:  Number of Monte Carlo runs.
    :param number_of_days: Simulation length in days.
    :param do_threading:   Use multiprocessing (set False for unit tests).
    :return: Statistical summary dict produced by :func:`report_stats`.
    """
    print(f"\n{'='*60}")
    print(f"  Scenario  : {label}")
    print(f"  pop={population:,}   beds={total_beds:,}   "
          f"sims={n_simulations:,}   days={number_of_days}")
    print(f"{'='*60}")

    overflow_days, beds_and_days, perc_vacant = sim.simulation(
        number_of_days, n_simulations, population, total_beds, do_threading,
    )
    summary = report_stats(overflow_days, perc_vacant, n_simulations)
    _save_plots(label, overflow_days, beds_and_days, perc_vacant, summary)
    return summary

if __name__ == "__main__":
    # Chicago-area baseline parameters (Sanvaliya et al. 2020)
    POP  = 2_710_000
    BEDS =    33_000
    SIMS =     1_000
    DAYS =        60

    # H1 – Does doubling beds eliminate overflow under a COVID-only surge?
    run_and_report("H1_before", POP, BEDS,      SIMS, DAYS)
    run_and_report("H1_after",  POP, BEDS * 2,  SIMS, DAYS)

    # H2 – Does a 25 % lockdown delay overflow with the original bed count?
    # (Effective susceptible population ≈ 203,250 when 92.5 % comply)
    run_and_report("H2_before", POP,     BEDS,  SIMS, DAYS)
    run_and_report("H2_after",  203_250, BEDS,  SIMS, DAYS)
