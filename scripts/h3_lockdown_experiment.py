"""H3: Lockdown impact across COVID variants and dual-pathogen scenarios.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from utilities.plotting import (
    plot_flu_infection_proportion, plot_flu_infections,
    plot_flu_lockdown_comparison, plot_lockdown_experiments, save_diagnostic_plots,
)
from utilities.seir import compliance_sweep, dual_simulation, flu_seir_simulation
from utilities.stats import report_stats
from utilities.variants import LOCKDOWN_LEVELS, OmicronVariables, VARIANT_MAP


def run_lockdown_experiments(
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    do_threading: bool = True,
    lockdown_levels: list = None,
) -> dict:
    levels = lockdown_levels if lockdown_levels is not None else LOCKDOWN_LEVELS

    print("\n" + "=" * 60)
    print("  Experiment 1 of 3 -- Influenza-only baseline (no COVID)")
    print(f"  Lockdown levels: {[f'{int(L * 100)}%' for L in levels]}")
    print("=" * 60)
    flu_only = compliance_sweep(
        levels, n_days, n_simulations, population, total_beds,
        hosp_rate_covid=0.0, hosp_rate_flu=0.015,
        covid_variables=None, do_threading=do_threading,
    )

    covid_only: dict = {}
    dual:       dict = {}
    for variant_name, (variant_class, hosp_rate) in VARIANT_MAP.items():
        print("\n" + "=" * 60)
        print(f"  Experiment 2 of 3 -- COVID-only [{variant_name}]")
        print("=" * 60)
        covid_only[variant_name] = compliance_sweep(
            levels, n_days, n_simulations, population, total_beds,
            hosp_rate_covid=hosp_rate, hosp_rate_flu=0.0,
            covid_variables=variant_class, do_threading=do_threading,
        )

        print("\n" + "=" * 60)
        print(f"  Experiment 3 of 3 -- COVID + Influenza [{variant_name}]")
        print("=" * 60)
        dual[variant_name] = compliance_sweep(
            levels, n_days, n_simulations, population, total_beds,
            hosp_rate_covid=hosp_rate, hosp_rate_flu=0.015,
            covid_variables=variant_class, do_threading=do_threading,
        )

    return {"flu_only": flu_only, "covid_only": covid_only, "dual": dual}


def _flu_summary(trajectories_by_lockdown: dict, population: int) -> dict:
    summary: dict = {}
    for lockdown, trajs in trajectories_by_lockdown.items():
        final_R  = np.array([t["R"][-1] for t in trajs])
        peak_I   = np.array([max(t["I"]) for t in trajs])
        peak_day = np.array([t["I"].index(max(t["I"])) for t in trajs])

        summary[lockdown] = {
            "attack_rate_pct":     float(np.mean(final_R) / population * 100.0),
            "attack_rate_p5":      float(np.percentile(final_R, 5)  / population * 100.0),
            "attack_rate_p95":     float(np.percentile(final_R, 95) / population * 100.0),
            "peak_infections":     float(np.mean(peak_I)),
            "peak_infections_p5":  float(np.percentile(peak_I, 5)),
            "peak_infections_p95": float(np.percentile(peak_I, 95)),
            "peak_day_mean":       float(np.mean(peak_day)),
        }
    return summary


def _diagnostic_plots_omicron_and_flu(
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    do_threading: bool = True,
) -> dict:
    print("\n" + "=" * 60)
    print("  Per-scenario diagnostic plots")
    print("=" * 60)

    print("\n  Omicron-only at lockdown = 0%:")
    ov, bd, pv = dual_simulation(
        n_days, n_simulations, population, total_beds,
        compliance=0.0, hosp_rate_covid=0.01, hosp_rate_flu=0.0,
        covid_variables=OmicronVariables, do_threading=do_threading,
    )
    s_omicron = report_stats(ov, pv, n_simulations)
    save_diagnostic_plots("H3_omicron_only", ov, bd, pv, s_omicron, total_beds=total_beds)

    print("\n  Flu-only -- running 0%, 25%, 50% lockdowns for infection dynamics...")
    flu_trajectories: dict = {}
    for lockdown in LOCKDOWN_LEVELS:
        flu_trajectories[lockdown] = flu_seir_simulation(
            n_days, n_simulations, population,
            compliance=lockdown, do_threading=do_threading,
        )

    plot_flu_infections(flu_trajectories[0.0], "H3_flu_only", n_days)
    plot_flu_infection_proportion(flu_trajectories[0.0], "H3_flu_only", n_days, population)
    plot_flu_lockdown_comparison(flu_trajectories, "H3_flu_only", n_days, population)

    s_flu = _flu_summary(flu_trajectories, population)

    return {"omicron_only": s_omicron, "flu_only": s_flu}


def run(
    population: int,
    total_beds: int,
    n_simulations: int,
    n_days: int,
    do_threading: bool = True,
) -> dict:
    results = run_lockdown_experiments(
        n_days, n_simulations, population, total_beds, do_threading=do_threading,
    )
    plot_lockdown_experiments(results, total_beds)

    diagnostics = _diagnostic_plots_omicron_and_flu(
        n_days, n_simulations, population, total_beds, do_threading=do_threading,
    )
    results["diagnostics"] = diagnostics

    return results


if __name__ == "__main__":
    run(population=2_710_000, total_beds=33_000, n_simulations=200, n_days=60)
