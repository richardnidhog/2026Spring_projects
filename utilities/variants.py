"""Variant-specific SEIR transition rates.
"""
import numpy as np

from .distributions import ran_pert_dist


class DeltaVariables:
    """COVID-19 Delta variant. R0 5-8, hospitalisation rate ~17 %."""

    @staticmethod
    def s_e() -> float:
        """Returns the transmission rate beta for Delta.

        Beta = R0 / infectious_period, where both are drawn from distributions.

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
        """Returns rates and timing for the E->I transition.

        Returns incubation rate, arrival rate, probability of testing positive, and time to receive test results.
        """
        incubation_rate = float(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.10, 0.18, 0.22, confidence=3, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 2, 7, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        """Returns time to outcome and the outcome (recovery/death) rate."""
        time_to_outcome = int(ran_pert_dist(8, 10, 14, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(8, 10, 14, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class OriginalVariables:
    """Ancestral SARS-CoV-2 (Wuhan). R0 2-3, hospitalisation rate ~3.5 %."""

    @staticmethod
    def s_e() -> float:
        """Returns beta for the original strain. Lower R0 than Delta or Omicron."""
        r0 = np.random.uniform(2.0, 3.0)
        infec_period = ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        """Returns incubation rate, arrival rate, positivity probability, and test time."""
        incubation_rate = float(1.0 / ran_pert_dist(2, 5, 14, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.05, 0.10, 0.30, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 2, 3, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        """Returns time to outcome and outcome rate for the original strain."""
        time_to_outcome = int(ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(5, 8, 14, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class OmicronVariables:
    """COVID-19 Omicron BA.1/BA.2. R0 10-16, hospitalisation rate 1 %.

    Much more transmissible than Delta but causes less severe illness.
    """

    @staticmethod
    def s_e() -> float:
        """Returns beta for Omicron. Much higher R0 and shorter infectious period than Delta.

        >>> import numpy as np; np.random.seed(0)
        >>> beta = OmicronVariables.s_e()
        >>> 10 / 6 <= beta <= 16 / 3
        True
        """
        r0 = np.random.uniform(10.0, 16.0)
        infec_period = ran_pert_dist(3, 4, 6, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        """Returns E->I transition params. Shorter incubation than earlier variants."""
        incubation_rate = float(1.0 / ran_pert_dist(3, 4, 5, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.15, 0.25, 0.40, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 1, 2, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        """Returns time to outcome and outcome rate for Omicron."""
        time_to_outcome = int(ran_pert_dist(3, 5, 8, confidence=4, samples=1)[0])
        outcome_rate    = float(1.0 / ran_pert_dist(3, 4, 6, confidence=4, samples=1)[0])
        return time_to_outcome, outcome_rate


class FluVariables:
    """Seasonal influenza (H1N1/H3N2). R0 1.2-1.4, hospitalisation rate 1.5 %.

    Much lower transmissibility than any COVID variant. Used in H2 and H3 to simulate concurrent flu season.
    """

    @staticmethod
    def s_e() -> float:
        """Returns beta for seasonal flu. Low R0 compared to COVID variants."""
        r0 = np.random.uniform(1.2, 1.4)
        infec_period = ran_pert_dist(3, 5, 7, confidence=4, samples=1)[0]
        return float(r0 / infec_period)

    @staticmethod
    def e_i() -> tuple:
        """Returns E->I transition params for flu."""
        incubation_rate = float(1.0 / ran_pert_dist(1, 2, 4, confidence=4, samples=1)[0])
        arrival_rate    = float(ran_pert_dist(1.70, 1.92, 4.46, confidence=4, samples=1)[0])
        prob_positive   = float(ran_pert_dist(0.01, 0.05, 0.15, confidence=4, samples=1)[0])
        time_test       = int(ran_pert_dist(1, 1, 3, confidence=4, samples=1)[0])
        return incubation_rate, arrival_rate, prob_positive, time_test

    @staticmethod
    def i_r() -> tuple:
        """Returns time to outcome and outcome rate for flu."""
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

# flu starts with more initial cases since it's already circulating
FLU_INITIAL_INFECTED: int = 1000
