"""Probability distributions used throughout the simulation."""
import numpy as np


def ran_pert_dist(
    minimum: float,
    most_likely: float,
    maximum: float,
    confidence: float = 4,
    samples: int = 1,
) -> np.ndarray:
    """Generate random samples from a modified PERT distribution.

    :param minimum: lowest possible value
    :param most_likely: the mode (peak of the distribution)
    :param maximum: highest possible value
    :param confidence: how tightly to weight around the mode; default 4 is standard PERT
    :param samples: how many values to draw

    >>> x = ran_pert_dist(1, 3, 5, confidence=4, samples=1)
    >>> 1 <= float(x[0]) <= 5
    True
    """
    if confidence < 1 or confidence > 18:
        raise ValueError("confidence value must be in range 1-18.")

    mean = (minimum + confidence * most_likely + maximum) / (confidence + 2)

    # convert PERT parameters to Beta distribution shape params a and b
    a = (mean - minimum) / (maximum - minimum) * (confidence + 2)
    b = ((confidence + 1) * maximum - minimum - confidence * most_likely) / (maximum - minimum)

    beta_samples = np.random.beta(a, b, samples)
    return beta_samples * (maximum - minimum) + minimum
