import os
import sys
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

_SIM_DIR = str(Path(__file__).parent / "2020")
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)
os.environ["PYTHONPATH"] = _SIM_DIR + os.pathsep + os.environ.get("PYTHONPATH", "")

import PR_final_project_revised as sim
from analysis import OUTPUT_DIR, _ci95, report_stats, _save_plots

class FluVariables:
    @staticmethod
    def s_e() -> float:
        r0_flu = np.random.uniform(1.2, 1.4)
        infec_period = sim.ran_pert_dist(3, 5, 7, confidence=4, samples=1000)
        return float(np.random.choice(r0_flu / infec_period))

    @staticmethod
    def e_i() -> tuple[float, float, float, int]:
        incubation_rate = float(np.random.choice(
            1.0 / sim.ran_pert_dist(1, 2, 4, confidence=4, samples=1000)
        ))
        arrival_rate = float(np.random.choice(
            sim.ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1000)
        ))
        prob_positive = float(np.random.choice(
            sim.ran_pert_dist(0.01, 0.05, 0.15, confidence=4, samples=1000)
        ))
        time_test_result = int(np.random.choice(
            sim.ran_pert_dist(1, 1, 3, confidence=4, samples=1000)
        ))
        return incubation_rate, arrival_rate, prob_positive, time_test_result

    @staticmethod
    def i_r() -> tuple[int, float]:
        time_to_outcome = int(np.random.choice(
            sim.ran_pert_dist(5, 7, 10, confidence=4, samples=1000)
        ))
        outcome_rate = float(np.random.choice(
            1.0 / sim.ran_pert_dist(3, 5, 7, confidence=4, samples=1000)
        ))
        return time_to_outcome, outcome_rate

def _seir_stream(
    n_days: int,
    population: int,
    variables,
    compliance: float,
    hosp_rate: float,
) -> tuple[list, list, list, list]:
    
    susceptible = float(population) - 1.0
    exposed     = 0.0
    infected    = 1.0
    recovered   = 0.0

    lst_hospitalized:    list = []
    lst_outcome:         list = []
    lst_day:             list = []
    lst_time_to_outcome: list = []

    for _ in range(n_days):
        beta               = variables.s_e() * (1.0 - compliance)
        incub_rate, _, _, test_result_time = variables.e_i()
        _, rate_outcome    = variables.i_r()

        new_exposed   = min(beta * susceptible * infected / population, susceptible)
        new_infected  = min(incub_rate * exposed, exposed)
        new_recovered = min(rate_outcome * infected, infected)

        susceptible -= new_exposed
        exposed     += new_exposed  - new_infected
        infected    += new_infected - new_recovered
        recovered   += new_recovered

        hosp             = min(infected * hosp_rate, float(population))
        outcome_time, _  = variables.i_r()
        outcome          = rate_outcome * hosp

        lst_hospitalized.append(hosp)
        lst_outcome.append(outcome)
        lst_day.append(test_result_time)
        lst_time_to_outcome.append(outcome_time)

    return lst_hospitalized, lst_outcome, lst_day, lst_time_to_outcome

def dual_model(
    simulation_id: int,
    n_days: int,
    population: int,
    total_beds: int,
    compliance: float      = 0.0,
    hosp_rate_covid: float = 0.17,
    hosp_rate_flu: float   = 0.015,
) -> tuple[list, list]:

    c_hosp, c_out, c_day, c_tto = _seir_stream(
        n_days, population, sim.Variables, compliance, hosp_rate_covid
    )
    f_hosp, f_out, f_day, f_tto = _seir_stream(
        n_days, population, FluVariables,  compliance, hosp_rate_flu
    )

    combined_hosp = [ch + fh for ch, fh in zip(c_hosp, f_hosp)]
    combined_out  = [co + fo for co, fo in zip(c_out,  f_out)]
    combined_day  = [max(cd, fd) for cd, fd in zip(c_day, f_day)]
    combined_tto  = [max(ct, ft) for ct, ft in zip(c_tto, f_tto)]

    bed_count, num_days = sim.test_result_days(
        combined_day, combined_tto, n_days,
        [], combined_out, [], combined_hosp, total_beds,
    )
    return bed_count, num_days


def dual_simulation(
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    compliance: float  = 0.0,
    do_threading: bool = True,
) -> tuple[list, list, list]:

    worker = partial(
        dual_model,
        n_days=n_days,
        population=population,
        total_beds=total_beds,
        compliance=compliance,
    )

    beds_and_days: list = []
    if do_threading:
        with Pool(processes=4) as pool:
            for result in tqdm(
                pool.imap_unordered(worker, range(n_simulations)),
                total=n_simulations,
                desc=f"compliance={compliance:.2f}",
            ):
                beds_and_days.append(result)
    else:
        for i in tqdm(range(n_simulations), desc=f"compliance={compliance:.2f}"):
            beds_and_days.append(
                dual_model(i, n_days, population, total_beds, compliance)
            )

    overflow_days:    list = []
    perc_vacant_beds: list = []
    count = 0

    for beds, _ in beds_and_days:
        overflowed = any(b <= 0 for b in beds)
        perc_vacant_beds.append(0.0 if overflowed else (beds[-1] / total_beds) * 100.0)
        for j, b in enumerate(beds):
            if b <= 0:
                overflow_days.append(j)
                count += 1
                break

    print(f"  Overflow probability: {count / n_simulations:.1%}")
    return overflow_days, beds_and_days, perc_vacant_beds

def compliance_sweep(
    compliance_levels: list[float],
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    hosp_rate_flu: float = 0.015,
    do_threading: bool   = True,
) -> list[dict]:

    results = []
    for c in compliance_levels:
        print(f"\n{'─' * 56}")
        print(f"  compliance = {c:.0%}  |  flu_hosp_rate = {hosp_rate_flu:.3f}")
        worker = partial(
            dual_model,
            n_days=n_days,
            population=population,
            total_beds=total_beds,
            compliance=c,
            hosp_rate_flu=hosp_rate_flu,
        )
        beds_and_days: list = []
        if do_threading:
            with Pool(processes=4) as pool:
                for result in tqdm(
                    pool.imap_unordered(worker, range(n_simulations)),
                    total=n_simulations,
                    desc=f"c={c:.2f}",
                ):
                    beds_and_days.append(result)
        else:
            for i in tqdm(range(n_simulations), desc=f"c={c:.2f}"):
                beds_and_days.append(
                    dual_model(i, n_days, population, total_beds, c,
                               hosp_rate_flu=hosp_rate_flu)
                )

        overflow_days:    list = []
        perc_vacant_beds: list = []
        count = 0
        for beds, _ in beds_and_days:
            overflowed = any(b <= 0 for b in beds)
            perc_vacant_beds.append(
                0.0 if overflowed else (beds[-1] / total_beds) * 100.0
            )
            for j, b in enumerate(beds):
                if b <= 0:
                    overflow_days.append(j)
                    count += 1
                    break
        print(f"  Overflow probability: {count / n_simulations:.1%}")

        summary = report_stats(overflow_days, perc_vacant_beds, n_simulations)
        summary["compliance"]     = c
        summary["hosp_rate_flu"]  = hosp_rate_flu
        results.append(summary)

    return results


def plot_compliance_sweep(
    covid_only_results: list[dict],
    dual_results:       list[dict],
) -> None:

    def _extract(results):
        levels  = [r["compliance"]                for r in results]
        prob_ov = [r["overflow"]["prob_overflow"]  for r in results]
        mean_va = [r["vacancy"]["mean"]            for r in results]
        ci_lo   = [r["vacancy"]["ci95"][0]         for r in results]
        ci_hi   = [r["vacancy"]["ci95"][1]         for r in results]
        return levels, prob_ov, mean_va, ci_lo, ci_hi

    c_lvl, c_pov, c_mva, c_lo, c_hi = _extract(covid_only_results)
    d_lvl, d_pov, d_mva, d_lo, d_hi = _extract(dual_results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # overflow probability
    ax1.plot(c_lvl, c_pov, marker="o", color="steelblue",  linewidth=2,
             label="COVID-19 only")
    ax1.plot(d_lvl, d_pov, marker="s", color="crimson",    linewidth=2,
             label="COVID-19 + Influenza")
    ax1.axhline(0.05, color="gray", linestyle="--", linewidth=1,
                label="5 % threshold")
    ax1.axvline(0.25, color="orange", linestyle=":", linewidth=1.5,
                label="25 % compliance mark")
    ax1.set_xlabel("Public Health Compliance")
    ax1.set_ylabel("Overflow Probability")
    ax1.set_title("H3: Overflow Probability vs. Compliance")
    ax1.set_ylim(-0.02, 1.05)
    ax1.set_xlim(-0.02, 1.02)
    ax1.legend(fontsize=8)

    # mean vacancy
    ax2.plot(c_lvl, c_mva, marker="o", color="steelblue", linewidth=2,
             label="COVID-19 only")
    ax2.fill_between(c_lvl, c_lo, c_hi, alpha=0.15, color="steelblue")
    ax2.plot(d_lvl, d_mva, marker="s", color="crimson",   linewidth=2,
             label="COVID-19 + Influenza")
    ax2.fill_between(d_lvl, d_lo, d_hi, alpha=0.15, color="crimson")
    ax2.axvline(0.25, color="orange", linestyle=":", linewidth=1.5,
                label="25 % compliance mark")
    ax2.set_xlabel("Public Health Compliance")
    ax2.set_ylabel("Mean % Vacant Beds at Day 60")
    ax2.set_title("H3: Bed Vacancy vs. Compliance")
    ax2.set_xlim(-0.02, 1.02)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    out = OUTPUT_DIR / "H3_compliance_sweep.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  H3 sweep plot saved → {out}")

if __name__ == "__main__":
    POP        = 2_710_000
    BEDS       = 33_000
    SIMS       = 1_000
    SIMS_SWEEP = 500
    DAYS       = 60

    print("\n" + "=" * 60)
    print("  H2E-A  COVID-only, 66,000 beds, compliance = 0.0")
    print("=" * 60)
    ov, bd, pv = sim.simulation(DAYS, SIMS, POP, BEDS * 2, do_threading=True)
    s_h2e_a = report_stats(ov, pv, SIMS)
    _save_plots("H2E_covid_only", ov, bd, pv, s_h2e_a)

    print("\n" + "=" * 60)
    print("  H2E-B  COVID+Flu, 66,000 beds, compliance = 0.0")
    print("=" * 60)
    ov, bd, pv = dual_simulation(DAYS, SIMS, POP, BEDS * 2, compliance=0.0)
    s_h2e_b = report_stats(ov, pv, SIMS)
    _save_plots("H2E_dual_pathogen", ov, bd, pv, s_h2e_b)

    LEVELS = [0.0, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.0]

    print("\n" + "=" * 60)
    print("  H3  COVID-only compliance sweep  (33,000 beds)")
    print("=" * 60)
    covid_only = compliance_sweep(
        LEVELS, DAYS, SIMS_SWEEP, POP, BEDS,
        hosp_rate_flu=0.0,
    )

    print("\n" + "=" * 60)
    print("  H3  COVID+Flu compliance sweep  (33,000 beds)")
    print("=" * 60)
    dual_flu = compliance_sweep(
        LEVELS, DAYS, SIMS_SWEEP, POP, BEDS,
        hosp_rate_flu=0.015,
    )

    plot_compliance_sweep(covid_only, dual_flu)
