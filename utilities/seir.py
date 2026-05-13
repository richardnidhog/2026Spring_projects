"""SEIR Monte Carlo engine for single- and dual-pathogen scenarios.
"""
from functools import partial
from multiprocessing import Pool

from tqdm import tqdm

from .bed_tracking import test_result_days
from .variants import DeltaVariables, FLU_INITIAL_INFECTED, FluVariables


def _seir_stream(
    n_days: int,
    population: int,
    variables,
    compliance: float,
    hosp_rate: float,
    initial_infected: int = 1,
) -> tuple:
    """Runs one SEIR simulation for a single pathogen and returns daily hospitalization data.

    Updates S, E, I, R compartments each day. Returns four lists for use in bed tracking.

    :param n_days: number of days to simulate
    :param population: total population size
    :param variables: variant class (e.g. DeltaVariables, FluVariables)
    :param compliance: lockdown compliance level from 0.0 (none) to 1.0 (full)
    :param hosp_rate: fraction of infected people who need a hospital bed
    :param initial_infected: starting infected count (default 1)
    """
    susceptible = float(population) - float(initial_infected)
    exposed     = 0.0
    infected    = float(initial_infected)
    recovered   = 0.0

    lst_hospitalized: list = []
    lst_outcome:      list = []
    lst_day:          list = []
    lst_tto:          list = []

    for _ in range(n_days):
        # draw stochastic transition rates for this day
        beta = variables.s_e() * (1.0 - compliance)
        incub_rate, _, _, test_result_time = variables.e_i()
        _, rate_outcome = variables.i_r()

        new_exposed   = min(beta * susceptible * infected / population, susceptible)
        new_infected  = min(incub_rate * exposed, exposed)
        new_recovered = min(rate_outcome * infected, infected)

        # move people between compartments
        susceptible -= new_exposed
        exposed     += new_exposed  - new_infected
        infected    += new_infected - new_recovered
        recovered   += new_recovered

        assert abs(susceptible + exposed + infected + recovered - population) < 1.0, (
            f"Population drift: {susceptible + exposed + infected + recovered:.2f} != {population}"
        )

        hosp = min(infected * hosp_rate, float(population))
        outcome_time, _ = variables.i_r()
        outcome = rate_outcome * hosp

        lst_hospitalized.append(hosp)
        lst_outcome.append(outcome)
        lst_day.append(test_result_time)
        lst_tto.append(outcome_time)

    return lst_hospitalized, lst_outcome, lst_day, lst_tto


def model(
    simulation_id: int,
    n_days: int,
    population: int,
    total_beds: int,
    compliance: float = 0.0,
    variables=None,
    hosp_rate: float = 0.17,
) -> tuple:
    """Runs a single COVID-only simulation and returns bed availability over time.
    """
    if variables is None:
        variables = DeltaVariables

    h, o, d, t = _seir_stream(n_days, population, variables, compliance, hosp_rate)
    return test_result_days(d, t, n_days, o, h, total_beds)


def dual_model(
    simulation_id: int,
    n_days: int,
    population: int,
    total_beds: int,
    compliance: float      = 0.0,
    hosp_rate_covid: float = 0.17,
    hosp_rate_flu: float   = 0.015,
    covid_variables=None,
) -> tuple:
    """Runs a single simulation with COVID and/or influenza co-circulating.

    :param hosp_rate_covid: set to 0.0 to disable COVID entirely
    :param hosp_rate_flu: set to 0.0 to disable influenza entirely
    """
    if covid_variables is None:
        covid_variables = DeltaVariables

    # only COVID is active — skip flu stream entirely
    if hosp_rate_flu == 0.0 and hosp_rate_covid > 0.0:
        h, o, d, t = _seir_stream(n_days, population, covid_variables, compliance, hosp_rate_covid)
        return test_result_days(d, t, n_days, o, h, total_beds)

    # only flu is active — skip COVID stream
    if hosp_rate_covid == 0.0 and hosp_rate_flu > 0.0:
        h, o, d, t = _seir_stream(n_days, population, FluVariables, compliance, hosp_rate_flu,
                                   initial_infected=FLU_INITIAL_INFECTED)
        return test_result_days(d, t, n_days, o, h, total_beds)

    if hosp_rate_covid == 0.0 and hosp_rate_flu == 0.0:
        return [total_beds] * n_days, list(range(n_days))

    # both active — run two independent SEIR streams and combine
    c_h, c_o, c_d, c_t = _seir_stream(n_days, population, covid_variables, compliance, hosp_rate_covid)
    f_h, f_o, f_d, f_t = _seir_stream(n_days, population, FluVariables,    compliance, hosp_rate_flu,
                                       initial_infected=FLU_INITIAL_INFECTED)

    combined_hosp = [ch + fh for ch, fh in zip(c_h, f_h)]
    combined_out  = [co + fo for co, fo in zip(c_o, f_o)]
    combined_day  = [max(cd, fd) for cd, fd in zip(c_d, f_d)]
    combined_tto  = [max(ct, ft) for ct, ft in zip(c_t, f_t)]

    return test_result_days(
        combined_day, combined_tto, n_days, combined_out, combined_hosp, total_beds,
    )


def _summarize_runs(beds_and_days: list, total_beds: int) -> tuple:
    """Extracts overflow days and vacancy percentages from all simulation runs.

    For each run, finds the first day beds hit zero and the percentage of
    beds still available at the end. Runs with overflow get vacancy = 0.

    >>> results = [([100, 50, -5], [0, 1, 2])]
    >>> overflow, vacancy = _summarize_runs(results, 200)
    >>> overflow
    [2]
    >>> vacancy
    [0.0]
    """
    overflow_days:    list = []
    perc_vacant_beds: list = []
    for beds, _ in beds_and_days:
        overflowed = any(b <= 0 for b in beds)
        perc_vacant_beds.append(0.0 if overflowed else (beds[-1] / total_beds) * 100.0)
        for j, b in enumerate(beds):
            if b <= 0:
                overflow_days.append(j)
                break
    return overflow_days, perc_vacant_beds


def _run_pool(worker, n_simulations: int, do_threading: bool, desc: str = "") -> list:
    """Runs n_simulations calls to worker, with or without multiprocessing.

    :param worker: a partial function that accepts a simulation_id int
    :param do_threading: if True, uses a Pool of 4 worker processes
    """
    results: list = []
    if do_threading:
        with Pool(processes=4) as pool:
            for r in tqdm(
                pool.imap_unordered(worker, range(n_simulations)),
                total=n_simulations, desc=desc,
            ):
                results.append(r)
    else:
        for i in tqdm(range(n_simulations), desc=desc):
            results.append(worker(i))
    return results


def simulation(
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    compliance: float = 0.0,
    variables=None,
    hosp_rate: float = 0.17,
    do_threading: bool = True,
) -> tuple:
    """Runs multiple COVID-only simulations and returns aggregated results.

    Returns overflow days, all beds/days raw data, and vacancy percentages across all runs.
    """
    worker = partial(
        model, n_days=n_days, population=population, total_beds=total_beds,
        compliance=compliance, variables=variables, hosp_rate=hosp_rate,
    )
    beds_and_days = _run_pool(
        worker, n_simulations, do_threading, desc=f"compliance={compliance:.2f}",
    )
    overflow_days, perc_vacant_beds = _summarize_runs(beds_and_days, total_beds)
    print(f"  Overflow probability: {len(overflow_days) / n_simulations:.1%}")
    return overflow_days, beds_and_days, perc_vacant_beds


def dual_simulation(
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    compliance: float      = 0.0,
    hosp_rate_covid: float = 0.17,
    hosp_rate_flu: float   = 0.015,
    covid_variables=None,
    do_threading: bool = True,
) -> tuple:
    """Same as simulation() but supports co-circulating pathogens.

    Set hosp_rate_flu=0.0 for COVID-only or hosp_rate_covid=0.0 for flu-only.
    """
    worker = partial(
        dual_model, n_days=n_days, population=population, total_beds=total_beds,
        compliance=compliance, hosp_rate_covid=hosp_rate_covid,
        hosp_rate_flu=hosp_rate_flu, covid_variables=covid_variables,
    )
    beds_and_days = _run_pool(
        worker, n_simulations, do_threading, desc=f"compliance={compliance:.2f}",
    )
    overflow_days, perc_vacant_beds = _summarize_runs(beds_and_days, total_beds)
    print(f"  Overflow probability: {len(overflow_days) / n_simulations:.1%}")
    return overflow_days, beds_and_days, perc_vacant_beds


def seir_trajectory(
    simulation_id: int,
    n_days: int,
    population: int,
    variables=None,
    compliance: float = 0.0,
    initial_infected: int = 1,
) -> dict:
    """Runs the SEIR model and returns the full S, E, I, R time series.

    Returns a dict with keys 'S', 'E', 'I', 'R', 'new_infections'.
    """
    if variables is None:
        variables = FluVariables

    susceptible = float(population) - float(initial_infected)
    exposed     = 0.0
    infected    = float(initial_infected)
    recovered   = 0.0

    S:       list = []
    E:       list = []
    I:       list = []
    R:       list = []
    new_inf: list = []

    for _ in range(n_days):
        beta            = variables.s_e() * (1.0 - compliance)
        incub_rate, *_  = variables.e_i()
        _, rate_outcome = variables.i_r()

        new_exposed   = min(beta * susceptible * infected / population, susceptible)
        new_infected  = min(incub_rate * exposed, exposed)
        new_recovered = min(rate_outcome * infected, infected)

        susceptible -= new_exposed
        exposed     += new_exposed  - new_infected
        infected    += new_infected - new_recovered
        recovered   += new_recovered

        # record compartment sizes for this day
        S.append(susceptible)
        E.append(exposed)
        I.append(infected)
        R.append(recovered)
        new_inf.append(new_infected)

    return {"S": S, "E": E, "I": I, "R": R, "new_infections": new_inf}


def flu_seir_simulation(
    n_days: int,
    n_simulations: int,
    population: int,
    compliance: float = 0.0,
    do_threading: bool = True,
    initial_infected: int = None,
) -> list:
    """Runs multiple SEIR simulations for influenza-only dynamics."""
    if initial_infected is None:
        initial_infected = FLU_INITIAL_INFECTED

    worker = partial(
        seir_trajectory,
        n_days=n_days, population=population,
        variables=FluVariables, compliance=compliance,
        initial_infected=initial_infected,
    )
    return _run_pool(
        worker, n_simulations, do_threading,
        desc=f"flu compliance={compliance:.2f}",
    )


def compliance_sweep(
    compliance_levels: list,
    n_days: int,
    n_simulations: int,
    population: int,
    total_beds: int,
    hosp_rate_covid: float = 0.17,
    hosp_rate_flu: float   = 0.015,
    covid_variables=None,
    do_threading: bool = True,
) -> list:
    """Runs a sweep over lockdown compliance levels for COVID and/or flu."""
    from .stats import report_stats   # local import: avoid circular dep on plotting

    results: list = []
    for c in compliance_levels:
        print("\n" + "-" * 56)
        print(f"  compliance={c:.0%}  covid_hosp={hosp_rate_covid:.3f}  flu_hosp={hosp_rate_flu:.3f}")
        ov, _, pv = dual_simulation(
            n_days, n_simulations, population, total_beds,
            compliance=c, hosp_rate_covid=hosp_rate_covid, hosp_rate_flu=hosp_rate_flu,
            covid_variables=covid_variables, do_threading=do_threading,
        )
        summary = report_stats(ov, pv, n_simulations)
        summary["compliance"]      = c
        summary["hosp_rate_covid"] = hosp_rate_covid
        summary["hosp_rate_flu"]   = hosp_rate_flu
        results.append(summary)
    return results
