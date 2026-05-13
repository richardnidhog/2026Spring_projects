"""
Hospital Bed Monte Carlo Simulation
"""
import argparse
import time

from scripts import h1_bed_doubling, h2_dual_pathogen, h3_lockdown_experiment
from utilities.reporting import write_markdown_summary

DEFAULT_POPULATION    = 2_710_000
DEFAULT_TOTAL_BEDS    = 33_000
DEFAULT_N_SIMULATIONS = 200
DEFAULT_N_DAYS        = 60


EXPERIMENTS = {
    "h1": ("Bed doubling under COVID-only surge", h1_bed_doubling.run),
    "h2": ("Bed doubling under COVID + Influenza", h2_dual_pathogen.run),
    "h3": ("Lockdown impact across variants and pathogens", h3_lockdown_experiment.run),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hospital bed Monte Carlo simulation hub.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--hypothesis", choices=list(EXPERIMENTS) + ["all"], default="all",
        help="Which hypothesis to run.",
    )
    parser.add_argument("--population", type=int, default=DEFAULT_POPULATION)
    parser.add_argument("--beds",       type=int, default=DEFAULT_TOTAL_BEDS)
    parser.add_argument("--sims",       type=int, default=DEFAULT_N_SIMULATIONS)
    parser.add_argument("--days",       type=int, default=DEFAULT_N_DAYS)
    parser.add_argument(
        "--single-process", action="store_true",
        help="Disable multiprocessing (slower but easier to debug).",
    )
    args = parser.parse_args()

    config = {
        "population":    args.population,
        "total_beds":    args.beds,
        "n_simulations": args.sims,
        "n_days":        args.days,
        "do_threading":  not args.single_process,
    }
    targets = list(EXPERIMENTS) if args.hypothesis == "all" else [args.hypothesis]

    print("\n" + "=" * 60)
    print("  Hospital Bed Monte Carlo Simulation Hub")
    print("=" * 60)
    print(f"  Population : {config['population']:,}")
    print(f"  Total beds : {config['total_beds']:,}")
    print(f"  Days       : {config['n_days']}")
    print(f"  Sims       : {config['n_simulations']}")
    print(f"  Targets    : {', '.join(t.upper() for t in targets)}")

    start = time.time()
    all_results: dict = {}
    for tag in targets:
        label, run_fn = EXPERIMENTS[tag]
        print("\n\n" + "#" * 60)
        print(f"  {tag.upper()}: {label}")
        print("#" * 60)
        all_results[tag] = run_fn(**config)

    runtime = time.time() - start

    summary_path = write_markdown_summary(all_results, config, runtime)
    print(f"\n  Markdown summary saved -> {summary_path}")

    print(f"\n\n{'=' * 60}")
    print(f"  All experiments complete.  Total runtime: {runtime:.1f} s")
    print("=" * 60)


if __name__ == "__main__":
    main()
