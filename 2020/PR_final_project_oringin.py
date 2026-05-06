
"""
IS 590 PR - Final Project

Monte Carlo Simulation on Hospital Capacity During COVID-19

Team members:
                        Varad Deshpande
                        Rohit Sanvaliya
                        Tanya Gupta
Note:
    The ranges of all randomised variables have been taken from real data from various
    sources that are cited within the code as well as in the README document of github
    repository

"""
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm


def ran_pert_dist(minimum: float, most_likely: float, maximum: float, confidence: float, samples: int) -> float:
    """Produce random numbers according to the 'Modified PERT' distribution.

        :param minimum: The lowest value expected as possible.
        :param most_likely: The 'most likely' value, statistically, the mode.
        :param maximum: The highest value expected as possible.
        :param confidence: This is typically called 'lambda' in literature
                            about the Modified PERT distribution. The value
                            4 here matches the standard PERT curve. Higher
                            values indicate higher confidence in the mode.
                            Currently allows values 1-18
        :param samples: number of samples to create the distribution

        Formulas to convert beta to PERT are adapted from a whitepaper
        "Modified Pert Simulation" by Paulo Buchsbaum.
        >>> x =  ran_pert_dist(1, 3, 5, confidence = 4, samples= 1)
        >>> if 1<= x <=5:
        ...         print("True")
        True
        """
    # Check for reasonable confidence levels to allow:
    if confidence < 1 or confidence > 18:
        raise ValueError('confidence value must be in range 1-18.')

    mean = (minimum + confidence * most_likely + maximum) / (confidence + 2)

    a = (mean - minimum) / (maximum - minimum) * (confidence + 2)
    b = ((confidence + 1) * maximum - minimum - confidence * most_likely) / (maximum - minimum)

    beta = np.random.beta(a, b, samples)
    beta = beta * (maximum - minimum) + minimum
    return beta


class Variables:
    """
        This class contains all the variables which we are considering for our simulation
        According to our SEIR model:
        S = Susceptible
        E = Exposed
        I = Infected
        R = Result (used interchangeably with the term outcome in the code)
        """
    # concept of transition between compartments - https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/
    @staticmethod
    def s_e():  # s = Susceptible    ;   e= Exposed
        """
        Computes each variable required for transition between Suceptible(S) and Exposed(E) compartments
        Infectious Rate (Beta) = R1 * Outcome Rate, where R1 (Reproduction Rate) = 1 (due to social distancing)
        Reproduction rate value is based on assumption of strict social distancing - https://www.vox.com/future-perfect/2020/4/15/21217027/coronavirus-social-distancing-flatten-curve-new-york, https://github.com/coronafighter/coronaSEIR/blob/master/main_coronaSEIR.py
        Infectious Rate is the rate of transmission of the virus
        :return: Infectious Rate
        >>> infectious_rate = np.random.choice(1.0 / (ran_pert_dist(8, 10, 14, confidence=4, samples=1)))
        >>> if   0.072 <= infectious_rate <= 0.125:
        ...         print("Pass")
        ... else:
        ...     print("Fail")
        Pass
        """
        # infectious rate - https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus
        infectious_rate = np.random.choice(1.0 / (ran_pert_dist(8, 10, 14, confidence=4, samples=1000)))  # beta
        return infectious_rate

    @staticmethod
    def e_i():  # e= Exposed;    i = Infected
        """
        Computes each variable required for transition between Exposed(E) and Infected(I) compartments
        Incubation Rate (Alpha) = 1/Incubation Period, where Incubation Period follows PERT distribution
        Incubation Rate is the rate at which symptoms start showing, after being exposed to the virus
        Arrival Rate =  Arrival Rate of patients at the hospitals (follows PERT distribution)
        Probability of testing positive for COVID-19 follows modified PERT distribution with confidence = 3
        Test Results  =  Time for test results to arrive (Follows PERT distribution)
        :return: Incubation Rate, Arrival Rate, Probability of testing positive for COVID-19, Test Results
        >>> incubation_rate = np.random.choice(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1))
        >>> arrival_rate = np.random.choice(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1))
        >>> prob_positive = np.random.choice(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1))
        >>> time_test_result = int(np.random.choice(ran_pert_dist(1, 2, 7, confidence=4, samples=1)))
        >>> if  0.072 <= incubation_rate <= 0.5 and 1.70 <= arrival_rate <= 4.46 and 0.10 <= prob_positive <= 0.22 and 1 <= time_test_result <= 7 :
        ...         print("True")
        ... else:
        ...         print("False")
        True
        """
        # incubation rate - https: // www.inverse.com / mind - body / how - long - are - you - infectious - when - you - have - coronavirus, https://www.medscape.com/answers/2500114-197431/what-is-the-incubation-period-for-coronavirus-disease-2019-covid-19
        incubation_rate = np.random.choice(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1000))  # alpha
        # arrival rate - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/05012020/covid-like-illness.html
        arrival_rate = np.random.choice(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1000))
        # probability of people testing positive for COVID-19 - https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/index.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fcoronavirus%2F2019-ncov%2Fcovid-data%2Fcovidview.html
        prob_positive = np.random.choice(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1000))
        time_test_result = int(np.random.choice(ran_pert_dist(1, 2, 7, confidence=4, samples=1000)))
        return incubation_rate, arrival_rate, prob_positive, time_test_result

    @staticmethod
    def i_r():  # i= Infected;    r = Result
        """
        Computes each variable required for transition between Infected(I) and Result(R) compartments
        Time to Outcome = Number of days in which recovered/dead patients will leave the hospital
        Outcome Rate = 1/Infectious Period, where Infectious Period indicates the duration of infection after which the patient either recovers/dies
        Outcome Rate is the rate at which recovered/dead patients are leaving hospital beds
        :return: Time to Outcome, Outcome Rate
        >>> time_to_outcome = int(np.random.choice(ran_pert_dist(8, 10, 14, confidence=4, samples=1)))
        >>> outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1))
        >>> if  8 <= time_to_outcome <= 14 and 0.072 <= outcome_rate <= 0.125:
        ...         print("True")
        ... else:
        ...         print("False")
        True
        """
        # time_to_outcome, outcome_rate - https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus
        time_to_outcome = int(np.random.choice(ran_pert_dist(8, 10, 14, confidence=4, samples=1000)))
        outcome_rate = np.random.choice(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1000))
        return time_to_outcome, outcome_rate


def admitted_bed(number_of_days: int, new_days: list, lst_outcome: list, lst_day_out: list, lst_hospitalized: list, number_of_beds: int) -> tuple:
    """
        This function calculates the number of hospital beds that are remaining after being occupied by hospitalized patients
        :param number_of_days:  Number of days considered for each iteration of the simulation
        :param new_days: List containing the number of days after which the test result are coming out
        :param lst_outcome: List of number of patients with some outcome. Either recovered or dead
        :param lst_day_out: List of number of days for each day in simulation, after which the outcome is received
        :param lst_hospitalized: List of number of patients who are hospitalized after being tested for infection
        :param number_of_beds: Available number of hospital beds in the given city
        :return: beds_available: Number of available beds on a given day based on the admitted patients and outcome patients,
                     num_x_days: The days to be plotted on x-axis in the graph
        >>> admitted_bed(2, [5,10],  [40,28], [23,33], [10, 5], 500)
        ([530, 513], [0, 1])
        """
    admitted_beds = []
    for i in range(number_of_days):
        for j in range(new_days[i] + 1):
            if j == new_days[i]:
                number_of_beds = number_of_beds - lst_hospitalized[i]
                admitted_beds.append(number_of_beds)
    beds_available, num_x_days = available_bed(number_of_days, lst_outcome, lst_day_out, number_of_beds, admitted_beds)
    return beds_available, num_x_days


def available_bed(number_of_days: int, lst_outcome: list, lst_day_out: list, number_of_beds: list, admitted_beds: list) -> tuple:
    """
        This function gives the number of available beds remaining after admitting the infected patients and discharging the recovered/dead patients
        It keeps on updating the number of available beds based on the admitted patients and  outcome patients
        :param number_of_days: Number of days for which each iteration of the simulation has to run
        :param lst_outcome:  List of number of patients with some outcome. Either recovered or dead
        :param lst_day_out:  List of number of days for each day in simulation, after which the outcome is recieved
        :param number_of_beds:  Available number of hospital beds in the given city
        :param admitted_beds: List of beds after admitting the patients
        :return: available_beds: List of available beds on a given day based on the admitted patients and outcome (recovered/dead) patients,
                     x_num_days: The days to be plotted on x-axis in the graph
        >>> available_bed(2, [40,28],[23,33], [2000, 1900], [345, 400])
        ([385, 428], [0, 1])
        """
    x_num_days = []
    available_beds = []
    for i in range(number_of_days):
        x_num_days.append(i)

        for j in range(lst_day_out[i] + 1):
            if j == lst_day_out[i]:
                admitted_beds[i] = admitted_beds[i] + lst_outcome[i]
                available_beds.append(admitted_beds[i])

    return available_beds, x_num_days


def test_result_days(lst_day: list, lst_time_to_outcome: list, number_of_days: int, new_days: list, lst_outcome: list, lst_day_out: list, lst_hospitalized: list, number_of_beds: int) -> tuple:
    """
        This function creates two lists of the number of days after which testing results are received and the number of days after which recovered/dead patients are discharged
        :param lst_day: List of nth days after which test result are coming out
        :param lst_time_to_outcome: The nth day after which outcome is witnessed with respect to the admitted day
        :param number_of_days: Number of days to test the simulation
        :param new_days: List of number of days for each day in simulation, after which the test result are arriving
        :param lst_outcome: List of number of patients with some outcome. Either recovered or dead
        :param lst_day_out: List of number of days for each day in simulation, after which the outcome is recieved
        :param lst_hospitalized: List of number of patients to be hospitalized
        :param number_of_beds: Number of hospital beds available in simulation
        :return: avail_beds: List of available beds on a given day based on the admitted patients and outcome (recovered/dead) patients,
                     num_days: The days to be plotted on x-axis in the graph

        >>> test_result_days([2, 3], [6, 7], 2, [5,10],[40,28], [23,33], [10, 5], 500)
        ([530, 513], [0, 1])
        """
    new_days = []
    lst_day_out = []
    for k in range(len(lst_day)):
        day = k
        day = day + lst_day[k]
        day_out = day + lst_time_to_outcome[k]
        new_days.append(day)
        lst_day_out.append(day_out)
    avail_beds, num_days = admitted_bed(number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds)
    return avail_beds, num_days


def model(simulation_id: int, number_of_days: int, population: int, total_beds: int) -> tuple:
    """
        Computes the number of people in each compartment based on the transitional variables defined in the class Variables
        :param simulation_id: ID for a simulation for a given pool of processes
        :param number_of_days: Number of days for which the simulation has to run
        :param population: General population of the region considered
        :param total_beds: Total number of hospital beds available in the region considered
        :return: bed_count: List of available beds on a given day based on the admitted patients and outcome (recovered/dead) patients,
                    num_days: The days to be plotted on x-axis in the graph
        >>> model(1, 2, 200, 100)
        ([100.0, 100.0], [0, 1])
        """
    # concept of compartments - https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/
    number_of_beds = total_beds
    total_population = population
    exposed = 1.0
    susceptible = total_population
    infected = 0.0
    day = 0


    lst_outcome = []
    lst_time_to_outcome = []
    lst_day = []
    lst_day_out = []
    new_days = []
    lst_hospitalized = []

    for i in range(number_of_days):
        susceptible = susceptible - int(Variables.s_e())*infected*susceptible
        incub_rate, arr_rate, prob_pos, test_result_time = Variables.e_i()
        exposed = (Variables.s_e() * susceptible - incub_rate * exposed)*0.05  # People getting exposed after social distancing - https://github.com/covid19-bh-biostats/seir/blob/master/SEIR/model_configs/basic
        day = day + test_result_time
        infected = arr_rate * prob_pos * exposed
        hospitalized = int(infected*(17/100))  # People who require hospitalization - https://gis.cdc.gov/grasp/covidnet/COVID19_3.html ; https://en.as.com/en/2020/04/12/other_sports/1586725810_541498.html
        lst_hospitalized.append(hospitalized)
        outcome_time, rate_outcome = Variables.i_r()
        outcome = rate_outcome * hospitalized
        lst_outcome.append(outcome)
        lst_day.append(test_result_time)
        lst_time_to_outcome.append(outcome_time)
    bed_count, num_days = test_result_days(lst_day, lst_time_to_outcome, number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds)

    return bed_count, num_days


def simulation(number_of_days: int, number_of_simulation: int, population: int, total_beds: int, do_threading=True):
    """
    Simulates the defined model for the mentioned number of simulations
    :param number_of_days: Number of days for which the simulation has to run
    :param number_of_simulation: Total number of simulations specified
    :param population: Population in the region considered
    :param total_beds: Total hospital beds available in the region considered
    :param do_threading: Boolean value
    :return overflow_day: the nth day on which the hospital beds will overflow,
               list_of_beds_and_days: list of tuple of available beds and days in the simulation,
               perc_vacant_beds: percentage of vacant beds by the end of the simulation
    >>> simulation(2, 1, 500, True)
    The Probability of vacant beds is: 0.0 %
    ([], [([1.0, 1.0], [0, 1])], [100.0])
    """
    count = 0
    perc_vacant_beds = []

    worker = partial(model, number_of_days=number_of_days, population=population, total_beds=total_beds)

    overflow_day = []
    list_of_beds_and_days = []

    # starting Multiprocessing
    if do_threading:
        p = Pool(processes=4)
        for beds_and_days in tqdm(p.imap_unordered(worker, range(number_of_simulation)), total=number_of_simulation):
            list_of_beds_and_days.append(beds_and_days)

        p.close()
        p.join()

        # Linear code without Multiprocessing
    else:
        for i in tqdm(range(number_of_simulation)):
            beds, days = model(i, number_of_days, population, total_beds)
            list_of_beds_and_days.append((beds, days))

    # Hypothesis -2: -If 25% of the total population is strictly asked to follow a lockdown, 50% of the total hospital beds will become vacant.
    # This patch gives the percentage of vacant beds for the nth simulation day

    for beds, days in list_of_beds_and_days:
        if beds[-1] < 0:
            prob_vacant = 0
        else:
            prob_vacant = (beds[-1] * 1.0 / total_beds)
        perc_vacant_beds.append(prob_vacant*100)
# Hypothesis-1 : If the number of hospital beds is doubled, there will never be an overflow in the available number of beds.
# This patch gives the day on which the number of beds hits zero and appends that day number in overflow_day list
# which is later plotted accordingly.

        for j in range(len(beds)):
            if beds[j] < 0:
                overflow_day.append(j)
                count += 1
                break
    probability = count / number_of_simulation
    print('The Probability of vacant beds is:', probability, '%')
    return overflow_day, list_of_beds_and_days, perc_vacant_beds


if __name__ == '__main__':

    # Inputs for testing hypotheses
    # Hypothesis -1
    #               Before:
    #                           population = 2710000 (Chicago area)
    #                           total beds = 33000 (Chicago area)
    #                           simulation = 1000
    #                           number_of days = 60
    #               After:
    #                           population = 2710000 (Chicago area)
    #                           total beds = 66000 (Chicago area)
    #                           simulation = 1000
    #                           number_of days = 60

    # Hypothesis - 2
    #               Before:
    #                           population = 2710000 (Chicago area)
    #                           total beds = 33000 (Chicago area)
    #                           simulation = 10000
    #                           number_of days = 60
    #               After:
    #                           population = 203250(Chicago area)
    #                           total beds = 33000 (Chicago area)
    #                           simulation = 10000
    #                           number_of days = 60

    population = int(input("Enter the total population to be considered: "))  # Chicago_population  = 2710000
    total_beds = int(input("Enter the number of beds to be considered: "))  # total_beds in Chicago      = 33000
    simulations = int(input("Enter the number of simulations to be considered: "))  # Simulation= (Select any Number)
    number_of_days = int(input("Enter the number of days to be considered: "))  # number_of_days   = 60

    import time

    start = time.time()
    overflow_day, list_of_beds_and_days, perc_vacant_beds = simulation(number_of_days, simulations, population, total_beds, True)
    print("Simulation time: %f" % (time.time() - start))

    # Plot for Hypothesis - 2
    # This plot is only used when the Hypothesis -2 is getting tested
    plt.hist(perc_vacant_beds, bins=15)
    plt.ylabel('Frequency')
    plt.xlabel('% vacant beds')
    plt.title("Percent Vacant Beds")
    plt.savefig('percent_vacant_beds-hist.png')
    plt.clf()

    # Plot for Hypothesis - 1
    plt.hist(overflow_day, bins=10)
    plt.ylabel('Frequency')
    plt.xlabel('Number of Days until Overflow')
    plt.title("nth Day When Beds Overflows")
    plt.savefig('overflow-days-hist.png')

    # Plot for simulation
    for beds, days in list_of_beds_and_days:
        plt.plot(days, beds)
    plt.ylabel('Available Beds')
    plt.xlabel('Number of Days')
    plt.title("Available Number of Beds")
    plt.savefig('beds-vs-days.png')
    plt.clf()
