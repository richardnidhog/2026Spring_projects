"""Probability distributions used throughout the simulation."""
import numpy as np


def ran_pert_dist(
    minimum: float,
    most_likely: float,
    maximum: float,
    confidence: float = 4,
    samples: int = 1,
) -> np.ndarray:
    if confidence < 1 or confidence > 18:
        raise ValueError("confidence value must be in range 1-18.")

    mean = (minimum + confidence * most_likely + maximum) / (confidence + 2)
    a = (mean - minimum) / (maximum - minimum) * (confidence + 2)
    b = ((confidence + 1) * maximum - minimum - confidence * most_likely) / (maximum - minimum)

    beta_samples = np.random.beta(a, b, samples)
    return beta_samples * (maximum - minimum) + minimum
