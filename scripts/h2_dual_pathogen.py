"""H2 Extended: Does doubling beds still help when influenza co-circulates?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utilities.plotting import save_diagnostic_plots
from utilities.seir import dual_simulation, simulation
from utilities.stats import report_stats


def run(
    population: int,
    total_beds: int,
    n_simulations: int,
    n_days: int,
    do_threading: bool = True,
) -> dict:
    """Compares COVID-only vs COVID+flu at doubled bed capacity (no lockdown).

    Runs two scenarios both at 2x beds. Saves diagnostic plots for each and returns both summaries.

    :return: dict with 'covid_only' and 'dual' summary stat dicts
    """
    doubled_beds = total_beds * 2

    print("\n" + "=" * 60)
    print(f"  H2-A  COVID-only [delta]  beds={doubled_beds:,}  lockdown=0%")
    print("=" * 60)
    ov, bd, pv = simulation(
        n_days, n_simulations, population, doubled_beds, do_threading=do_threading,
    )
    s_a = report_stats(ov, pv, n_simulations)
    save_diagnostic_plots("H2_covid_only_delta", ov, bd, pv, s_a, total_beds=doubled_beds)

    print("\n" + "=" * 60)
    print(f"  H2-B  COVID + Influenza [delta]  beds={doubled_beds:,}  lockdown=0%")
    print("=" * 60)
    ov, bd, pv = dual_simulation(
        n_days, n_simulations, population, doubled_beds,
        compliance=0.0, do_threading=do_threading,
    )
    s_b = report_stats(ov, pv, n_simulations)
    save_diagnostic_plots("H2_dual_pathogen_delta", ov, bd, pv, s_b, total_beds=doubled_beds)

    return {"covid_only": s_a, "dual": s_b}


if __name__ == "__main__":
    run(population=2_710_000, total_beds=33_000, n_simulations=200, n_days=60)
