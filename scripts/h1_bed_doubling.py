"""H1: Does doubling hospital beds eliminate overflow under a COVID-only surge?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities.plotting import save_diagnostic_plots
from utilities.seir import simulation
from utilities.stats import report_stats


def run(
    population: int,
    total_beds: int,
    n_simulations: int,
    n_days: int,
    do_threading: bool = True,
) -> dict:
    """Tests whether doubling beds eliminates overflow under a Delta COVID-only surge.

    Runs two scenarios. Saves three diagnostic plots for each scenario
    and returns summary statistics for both.

    :param population: total population size
    :param total_beds: baseline bed count (doubled version is computed internally)
    :param n_simulations: number of Monte Carlo runs per scenario
    :param n_days: simulation length in days
    :return: dict with 'before' and 'after' summary stat dicts
    """
    print("\n" + "=" * 60)
    print(f"  H1 Before  pop={population:,}  beds={total_beds:,}  sims={n_simulations}")
    print("=" * 60)
    ov, bd, pv = simulation(
        n_days, n_simulations, population, total_beds, do_threading=do_threading,
    )
    s_before = report_stats(ov, pv, n_simulations)
    save_diagnostic_plots("H1_before", ov, bd, pv, s_before, total_beds=total_beds)

    print("\n" + "=" * 60)
    print(f"  H1 After   pop={population:,}  beds={total_beds * 2:,}  sims={n_simulations}")
    print("=" * 60)
    ov, bd, pv = simulation(
        n_days, n_simulations, population, total_beds * 2, do_threading=do_threading,
    )
    s_after = report_stats(ov, pv, n_simulations)
    save_diagnostic_plots("H1_after", ov, bd, pv, s_after, total_beds=total_beds * 2)

    return {"before": s_before, "after": s_after}


if __name__ == "__main__":
    run(population=2_710_000, total_beds=33_000, n_simulations=200, n_days=60)
