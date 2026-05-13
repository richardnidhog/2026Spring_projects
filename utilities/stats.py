"""Statistical reporting for Monte Carlo simulation results."""
import math

import numpy as np
from scipy import stats as sp_stats


def _ci95(arr) -> tuple:
    """Computes a 95% confidence interval using the t-distribution.

    Returns (lower, upper). Returns (nan, nan) for empty input,
    or (mean, mean) if all values are the same (zero standard error).

    >>> lo, hi = _ci95([5.0, 5.0, 5.0])
    >>> lo == hi == 5.0
    True
    """
    n = len(arr)
    if n == 0:
        return float("nan"), float("nan")
    if n == 1:
        return float(arr[0]), float(arr[0])

    mean = float(np.mean(arr))
    sem  = float(sp_stats.sem(arr))
    if sem == 0.0 or math.isnan(sem):
        return mean, mean

    lo, hi = sp_stats.t.interval(0.95, df=n - 1, loc=mean, scale=sem)
    return float(lo), float(hi)


def report_stats(
    overflow_days: list,
    perc_vacant_beds: list,
    n_simulations: int,
) -> dict:
    """Summarizes overflow and bed vacancy statistics across all simulation runs.

    Computes overflow probability, mean first-overflow day with 95% CI,
    and mean bed vacancy at simulation end. Also prints a formatted summary.

    :param overflow_days: list of first-overflow days for runs that overflowed
    :param perc_vacant_beds: vacancy percentage at simulation end for each run
    :param n_simulations: total number of runs (used to compute probability)
    :return: dict with 'overflow' and 'vacancy' sub-dicts
    """
    if overflow_days:
        od = np.array(overflow_days, dtype=float)
        lo, hi = _ci95(od)
        ov = {
            "n_overflowed":  len(overflow_days),
            "prob_overflow": len(overflow_days) / n_simulations,
            "mean":          float(np.mean(od)),
            "ci95":          (lo, hi),
            "p5":            float(np.percentile(od,  5)),
            "p95":           float(np.percentile(od, 95)),
        }
    else:
        ov = {"n_overflowed": 0, "prob_overflow": 0.0}

    va = np.array(perc_vacant_beds, dtype=float)
    lo_v, hi_v = _ci95(va)
    vs = {
        "mean": float(np.mean(va)),
        "ci95": (lo_v, hi_v),
        "p5":   float(np.percentile(va,  5)),
        "p95":  float(np.percentile(va, 95)),
    }

    print("\n-- Overflow ----------------------------------------------------")
    print(f"  Overflow probability : {ov['prob_overflow']:.1%}"
          f"  ({ov['n_overflowed']} / {n_simulations} runs)")
    if overflow_days:
        print(f"  First-overflow day   : mean = {ov['mean']:.1f} days")
        print(f"                         95% CI  [{ov['ci95'][0]:.1f},  {ov['ci95'][1]:.1f}]")
        print(f"                         5th pct {ov['p5']:.0f}  /  95th pct {ov['p95']:.0f}")

    print("\n-- Bed Vacancy at Simulation End -------------------------------")
    print(f"  Mean    {vs['mean']:.2f}%"
          f"   95% CI [{vs['ci95'][0]:.2f}%,  {vs['ci95'][1]:.2f}%]")
    print(f"  5th pct {vs['p5']:.2f}%   95th pct {vs['p95']:.2f}%")
    print("----------------------------------------------------------------\n")

    return {"overflow": ov, "vacancy": vs}
