"""Variant-specific SEIR transition rates.
"""
import numpy as np

from .distributions import ran_pert_dist


class DeltaVariables:
    """COVID-19 Delta variant. R0 5-8, hospitalisation rate ~17 %."""

    @staticmethod
    def s_e() -> float:
        """Transmission rate beta = R0 / infectious_period.

        >>> import numpy as np; np.random.seed(0)
        >>> beta = DeltaVariables.s_e()
        >>> 5 / 14 <= beta <= 8 / 8
        True
        """
        r0 = np.random.uniform(5.0, 8.0)
        infec_period = ran_pert_dist(8, 10, 14, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        incubation_rate = float(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 2, 7, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        time_to_outcome = int(ran_pert_dist(8, 10, 14, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class OriginalVariables:
    """Ancestral SARS-CoV-2 (Wuhan). R0 2-3, hospitalisation rate ~3.5 %."""

    @staticmethod
    def s_e() -> float:
        r0 = np.random.uniform(2.0, 3.0)
        infec_period = ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        incubation_rate = float(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.05, 0.10, 0.30, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 2, 3, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        time_to_outcome = int(ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class OmicronVariables:
    """COVID-19 Omicron BA.1/BA.2. R0 10-16, hospitalisation rate ~1 %."""

    @staticmethod
    def s_e() -> float:
        r0 = np.random.uniform(10.0, 16.0)
        infec_period = ran_pert_dist(3, 4, 6, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        incubation_rate = float(1.0 / ran_pert_dist(3, 4, 5, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.15, 0.25, 0.40, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 1, 2, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        time_to_outcome = int(ran_pert_dist(3, 5, 8, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(3, 4, 6, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class FluVariables:
    """Seasonal influenza (H1N1/H3N2). R0 1.2-1.4, hospitalisation rate ~1.5 %."""

    @staticmethod
    def s_e() -> float:
        r0 = np.random.uniform(1.2, 1.4)
        infec_period = ran_pert_dist(3, 5, 7, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        incubation_rate = float(1.0 / ran_pert_dist(1, 2, 4, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.01, 0.05, 0.15, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 1, 3, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        time_to_outcome = int(ran_pert_dist(5, 7, 10, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(3, 5, 7, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate

VARIANT_MAP: dict = {
    "original": (OriginalVariables, 0.035),
    "delta":    (DeltaVariables,    0.17),
    "omicron":  (OmicronVariables,  0.01),
}

VARIANT_LABELS: dict = {
    "original": "Original (R0=2-3, hosp=3.5%)",
    "delta":    "Delta  (R0=5-8, hosp=17%)",
    "omicron":  "Omicron  (R0=10-16, hosp=1%)",
}

LOCKDOWN_LEVELS: list = [0.0, 0.25, 0.50]

FLU_INITIAL_INFECTED: int = 1000
