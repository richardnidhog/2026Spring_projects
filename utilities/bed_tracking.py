"""Bed-occupancy accounting given hospitalization and discharge schedules."""


def admitted_bed(
    number_of_days: int,
    new_days: list,
    lst_outcome: list,
    lst_day_out: list,
    lst_hospitalized: list,
    number_of_beds: int,
) -> tuple:
    """Reduces available beds as patients are admitted on their test-result day.

    Simulate day by day, and when a patient's test results are available, 
    subtract the number of hospitalized patients from the total number of beds. 
    Then call the `available_bed` function to recalculate the number of available beds.

    >>> admitted_bed(2, [5, 10], [40, 28], [23, 33], [10, 5], 500)
    ([530, 513], [0, 1])
    """
    admitted_beds: list = []
    for i in range(number_of_days):
        for j in range(new_days[i] + 1):
            if j == new_days[i]:
                number_of_beds = max(number_of_beds - lst_hospitalized[i], 0.0)
                admitted_beds.append(number_of_beds)
    return available_bed(number_of_days, lst_outcome, lst_day_out, number_of_beds, admitted_beds)


def available_bed(
    number_of_days: int,
    lst_outcome: list,
    lst_day_out: list,
    number_of_beds: int,
    admitted_beds: list,
) -> tuple:
    """Adds beds back as patients are discharged.

    Returns a list of available beds per day and the corresponding day indices.
    """
    x_num_days:     list = []
    available_beds: list = []
    for i in range(number_of_days):
        x_num_days.append(i)
        for j in range(lst_day_out[i] + 1):
            if j == lst_day_out[i]:
                if admitted_beds[i] > 0:
                    admitted_beds[i] = admitted_beds[i] + lst_outcome[i]
                available_beds.append(admitted_beds[i])
    return available_beds, x_num_days


def test_result_days(
    lst_day: list,
    lst_time_to_outcome: list,
    number_of_days: int,
    lst_outcome: list,
    lst_hospitalized: list,
    number_of_beds: int,
) -> tuple:
    """Converts per-day test delays into absolute day indices, then runs bed tracking.

    Adds the test result delay to each day index so patients are admitted on the right absolute day.

    >>> test_result_days([2, 3], [6, 7], 2, [40, 28], [10, 5], 500)
    ([530, 513], [0, 1])
    """
    new_days:    list = []
    lst_day_out: list = []
    for k in range(len(lst_day)):
        day     = k + lst_day[k]
        day_out = day + lst_time_to_outcome[k]
        new_days.append(day)
        lst_day_out.append(day_out)
    return admitted_bed(
        number_of_days, new_days, lst_outcome, lst_day_out, lst_hospitalized, number_of_beds,
    )
