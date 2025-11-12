"""
Bühlmann and Bühlmann-Straub credibility calculation tools

This module provides functions for experience-based credibility using the
Bühlmann method for equal weights and Bühlmann-Straub for general weights.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Dict, List, Tuple


@dataclass
class BuhlmannInputs:
    # Equal weights (Bühlmann): observations grouped per risk
    # data[risk_id] = [x_t1, x_t2, ..., x_tn]
    data: Dict[str, List[float]]


@dataclass
class BuhlmannStraubInputs:
    # General weights (Bühlmann–Straub): list of (risk_id, value, weight)
    # weight is exposure (or credibility unit) for that observation
    observations: List[Tuple[str, float, float]]  # (risk_id, y, w) with w>0


@dataclass
class BuhlmannResult:
    mu: float         # collective mean
    EPV: float        # expected process variance
    VHM: float        # variance of hypothetical means
    K: float          # EPV/VHM (credibility constant)
    Z_by_risk: Dict[str, float]
    estimate_by_risk: Dict[str, float]  # Z * ybar_i + (1-Z) * mu


def _bm_component_estimates_equal_n(data: Dict[str, List[float]]) -> Tuple[float, float, float]:
    """
    Estimate μ (mu), EPV, VHM under Bühlmann with equal numbers per risk (n_i all equal).
    If n_i differ mildly, treat as 'approximately equal'; for strongly unequal exposures, use BS.
    """
    # Basic sanity
    r = len(data)
    if r < 2:
        raise ValueError("Need at least 2 risks for Bühlmann estimation.")
    n_list = [len(v) for v in data.values()]
    if min(n_list) < 2:
        raise ValueError("Each risk needs at least 2 observations for EPV estimation.")

    # Means
    risk_means = {k: (sum(v) / len(v)) for k, v in data.items()}
    all_vals: List[float] = [x for v in data.values() for x in v]
    mu = sum(all_vals) / len(all_vals)
    n = n_list[0]  # assume equal n

    # EPV: pooled within-risk variance
    ss_within = 0.0
    for k, v in data.items():
        m = risk_means[k]
        ss_within += sum((x - m) ** 2 for x in v)
    EPV = ss_within / (r * (n - 1))

    # VHM: between-risk variance minus EPV/n
    # unbiased between-groups variance
    from statistics import mean
    mean_of_risk_means = mean(risk_means.values())
    ss_between = sum((risk_means[k] - mean_of_risk_means) ** 2 for k in data)
    VHM = max((ss_between / (r - 1)) - (EPV / n), 0.0)

    return mu, EPV, VHM


def buhlmann(inputs: BuhlmannInputs) -> BuhlmannResult:
    """
    Bühlmann credibility (equal weights per time cell).
    Returns μ, EPV, VHM, K, Z_i and credibility estimates for each risk i.
    """
    mu, EPV, VHM = _bm_component_estimates_equal_n(inputs.data)
    if VHM == 0.0:
        K = float("inf")
    else:
        K = EPV / VHM

    # Risk sample sizes (assumes equal n but computes explicitly)
    n_by_risk = {k: len(v) for k, v in inputs.data.items()}
    ybar_by_risk = {k: (sum(v) / len(v)) for k, v in inputs.data.items()}

    Z_by_risk = {k: (n_by_risk[k] / (n_by_risk[k] + K)) if isfinite(K) else 0.0
                 for k in inputs.data}
    estimate_by_risk = {k: Z_by_risk[k] * ybar_by_risk[k] + (1.0 - Z_by_risk[k]) * mu
                        for k in inputs.data}
    return BuhlmannResult(mu=mu, EPV=EPV, VHM=VHM, K=K,
                          Z_by_risk=Z_by_risk, estimate_by_risk=estimate_by_risk)


def buhlmann_straub(inputs: BuhlmannStraubInputs) -> BuhlmannResult:
    """
    Bühlmann–Straub with general weights (exposures). Nonparametric moment estimators.
    observations: list of (risk_id, y, w), w>0
    """
    # Organize by risk
    by_risk: Dict[str, List[Tuple[float, float]]] = {}
    for rid, y, w in inputs.observations:
        if w <= 0:
            raise ValueError("Weights must be positive.")
        by_risk.setdefault(rid, []).append((y, w))

    if len(by_risk) < 2:
        raise ValueError("Need at least 2 risks for Bühlmann–Straub estimation.")

    # Weighted means per risk and overall
    m_i: Dict[str, float] = {rid: sum(w for _, w in obs) for rid, obs in by_risk.items()}
    ybar_i: Dict[str, float] = {
        rid: sum(w * y for y, w in obs) / m_i[rid] for rid, obs in by_risk.items()
    }
    M = sum(m_i.values())
    mu = sum(m_i[rid] * ybar_i[rid] for rid in by_risk) / M

    # EPV_hat (weighted within-risk)
    # Denominator uses effective df: sum_i (m_i - sum_j w_ij^2 / m_i)
    num_within = 0.0
    den_within = 0.0
    sum_wsq_over_mi = 0.0
    for rid, obs in by_risk.items():
        mi = m_i[rid]
        sum_wsq_over_mi_i = sum((w ** 2) / mi for _, w in obs)
        sum_wsq_over_mi += sum_wsq_over_mi_i
        num_within += sum(w * (y - ybar_i[rid]) ** 2 for y, w in obs)
        den_within += (mi - sum_wsq_over_mi_i)

    if den_within <= 0:
        raise ValueError("Insufficient within-risk degrees of freedom.")
    EPV = num_within / den_within

    # VHM_hat (between-risk, corrected for within component)
    # See standard nonparametric Bühlmann–Straub moment estimator.
    num_between = sum(m_i[rid] * (ybar_i[rid] - mu) ** 2 for rid in by_risk)
    den_between = M - sum_wsq_over_mi  # effective df for between
    raw_between = num_between / den_between if den_between > 0 else 0.0
    VHM = max(raw_between - EPV * (1.0 / den_between), 0.0) if den_between > 0 else 0.0

    K = (EPV / VHM) if VHM > 0 else float("inf")
    Z_by_risk = {rid: (m_i[rid] / (m_i[rid] + K)) if isfinite(K) else 0.0 for rid in by_risk}
    estimate_by_risk = {rid: Z_by_risk[rid] * ybar_i[rid] + (1.0 - Z_by_risk[rid]) * mu
                        for rid in by_risk}

    return BuhlmannResult(mu=mu, EPV=EPV, VHM=VHM, K=K,
                          Z_by_risk=Z_by_risk, estimate_by_risk=estimate_by_risk)


__all__ = [
    'BuhlmannInputs', 
    'BuhlmannStraubInputs', 
    'BuhlmannResult',
    'buhlmann', 
    'buhlmann_straub',
]
