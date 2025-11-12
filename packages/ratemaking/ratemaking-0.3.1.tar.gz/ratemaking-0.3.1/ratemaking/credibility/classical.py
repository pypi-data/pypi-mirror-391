"""
Classical (Limited Fluctuation) credibility calculation tools

This module provides functions for traditional credibility theory based on
limiting fluctuations to acceptable levels.
"""

from statistics import NormalDist


def _z_two_sided(p: float) -> float:
    """
    Two-sided normal critical value: find z s.t. P(|Z| <= z) = p
    (i.e., z_{1 - α/2} where p = 1 - α).
    """
    if not (0.5 < p < 0.999999):
        raise ValueError("p must be in (0.5, 0.999999) for two-sided coverage")
    return NormalDist().inv_cdf((1 + p) / 2.0)


def classical_full_credibility_frequency(p: float, k: float) -> float:
    """
    Full-credibility standard for COUNT of claims under Poisson approximation:
      require expected number of claims n ≥ (z/k)^2
    where p = two-sided coverage (e.g., 0.95), k = relative tolerance (e.g., 0.10).
    Returns required expected number of claims n_full.
    """
    z = _z_two_sided(p)
    return (z / k) ** 2


def classical_full_credibility_severity(cv: float, p: float, k: float) -> float:
    """
    Full-credibility standard for the MEAN SEVERITY:
      require number of claims n ≥ (z * CV / k)^2
    where CV = sigma/mean of severity.
    Returns required number of claims n_full.
    """
    z = _z_two_sided(p)
    return (z * cv / k) ** 2


def classical_full_credibility_pure_premium(cv_sev: float, p: float, k: float) -> float:
    """
    Full-credibility standard for PURE PREMIUM per exposure (compound Poisson):
      relative variance ≈ (CV_X^2 + 1) / n, where n = expected #claims.
      require z^2 * (CV_X^2 + 1) / n ≤ k^2 ⇒ n ≥ z^2 * (CV_X^2 + 1) / k^2.
    Returns required expected number of claims n_full.
    """
    z = _z_two_sided(p)
    return (z ** 2) * (cv_sev ** 2 + 1.0) / (k ** 2)


def classical_partial_credibility(n: float, n_full: float) -> float:
    """
    Partial credibility weight:
      Z = min(1, sqrt(n / n_full))
    where n is the applicable exposure size metric (e.g., expected #claims).
    """
    if n_full <= 0:
        raise ValueError("n_full must be > 0")
    if n < 0:
        raise ValueError("n must be ≥ 0")
    from math import sqrt
    return min(1.0, sqrt(n / n_full))


__all__ = [
    'classical_full_credibility_frequency',
    'classical_full_credibility_severity', 
    'classical_full_credibility_pure_premium',
    'classical_partial_credibility',
]
