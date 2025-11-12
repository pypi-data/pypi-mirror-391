from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Optional
from datetime import date, datetime
import pandas as pd

def _to_years(start: date | datetime, end: date | datetime) -> float:
    """Year fraction using 365.2425-day year."""
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()
    return (end - start).days / 365.2425

def trended_present_rates_loss_cost(
    present_rate: float,
    prior_indicated_factor: float,
    prior_implemented_factor: float,
    loss_trend_annual: float,
    trend_years: Optional[float] = None,
    trend_from: Optional[date | datetime] = None,
    trend_to: Optional[date | datetime] = None,
) -> float:
    """
    WM Ch.12 (First-Dollar): Trended present rates complement (pure premium form).
    C = Present Rate × (1 + loss_trend_annual)^t × (Prior Indicated / Prior Implemented).

    Trend period t must be measured from the *prior review's target effective date* to the
    *new filing's target effective date* (not actual), per WM guidance.  (Refs: WM Ch.12, pp. 230–231)

    Args:
        present_rate: Current average rate or loss cost (>= 0).
        prior_indicated_factor: (1 + last indicated rate change). Example: 1.10.
        prior_implemented_factor: (1 + last implemented rate change). Example: 1.06.
        loss_trend_annual: Annual loss trend (as decimal). Example: 0.05 for 5%.
        trend_years: If provided, use directly. Otherwise compute from (trend_from, trend_to).
        trend_from, trend_to: Target effective dates (prior review -> new filing).

    Returns:
        Complement C as a *loss cost / pure premium*.

    Raises:
        ValueError on invalid inputs.
    """
    if present_rate < 0:
        raise ValueError("present_rate must be >= 0")
    if prior_indicated_factor <= 0 or prior_implemented_factor <= 0:
        raise ValueError("prior factors must be > 0")
    if loss_trend_annual < -1:
        raise ValueError("loss_trend_annual < -100% is invalid")

    if trend_years is None:
        if not (trend_from and trend_to):
            raise ValueError("Provide trend_years or both trend_from and trend_to.")
        trend_years = _to_years(trend_from, trend_to)

    trend_factor = (1.0 + loss_trend_annual) ** trend_years
    residual_ratio = prior_indicated_factor / prior_implemented_factor
    return present_rate * trend_factor * residual_ratio


def trended_present_rates_rate_change_factor(
    prior_indicated_factor: float,
    prior_implemented_factor: float,
    loss_trend_annual: float,
    premium_trend_annual: float,
    trend_years: Optional[float] = None,
    trend_from: Optional[date | datetime] = None,
    trend_to: Optional[date | datetime] = None,
) -> float:
    """
    WM Ch.12 (First-Dollar): Trended present rates complement in *rate-change-factor* form.
    C_factor = (prior_indicated / prior_implemented) × ((1 + loss_trend)/(1 + premium_trend))^t.

    Use when your workflow is in loss-ratio space and you need a complement as a factor to blend
    with an indicated rate change factor (WM example computes residual then applies net trend).
    (Refs: WM Ch.12 pp. 230–231; Appendix A narrative)

    Returns:
        Complement factor (> 0). To convert to a rate change percentage, subtract 1.
    """
    if prior_indicated_factor <= 0 or prior_implemented_factor <= 0:
        raise ValueError("prior factors must be > 0")
    if (1.0 + premium_trend_annual) <= 0:
        raise ValueError("premium trend annual must be > -100%")

    if trend_years is None:
        if not (trend_from and trend_to):
            raise ValueError("Provide trend_years or both trend_from and trend_to.")
        trend_years = _to_years(trend_from, trend_to)

    net_trend = ((1.0 + loss_trend_annual) / (1.0 + premium_trend_annual)) ** trend_years
    residual_ratio = prior_indicated_factor / prior_implemented_factor
    return residual_ratio * net_trend


def larger_group_applied_rate_change_to_present_rate(
    present_rate: float,
    larger_group_indicated_factor: float,
) -> float:
    """
    WM First-Dollar method: Apply the *larger group's* indicated rate change factor to the subject's
    present rate to form the complement.  (Refs: WM Ch.12 list of methods)
    Returns a loss cost / pure premium.
    """
    if present_rate < 0 or larger_group_indicated_factor <= 0:
        raise ValueError("Invalid inputs.")
    return present_rate * larger_group_indicated_factor


@dataclass(frozen=True)
class HarwayneInputs:
    # Subject state's class mix (exposure counts by class)
    target_class_exposures: pd.Series  # index: class
    # Subject state's average pure premium (scalar). If None, can compute from subject class PP & exposures.
    target_avg_pure_premium: float
    # Related states' class PP and exposures: dict[state] -> Series(class -> value)
    related_state_class_pp: Mapping[str, pd.Series]
    related_state_class_exposures: Mapping[str, pd.Series]
    # Class of interest (e.g., the class you are rating)
    class_of_interest: str

def harwayne_complement(inputs: HarwayneInputs) -> float:
    """
    WM First-Dollar: Harwayne's method.
    Steps (for each related state s):
      1) Reweight state s class PP to the subject state's class mix: Lhat_s = sum_c w_A(c)*L_{s,c},
         where w_A(c) = X_{A,c}/sum_c X_{A,c}.
      2) Adjustment factor F_s = Lbar_A / Lhat_s, where Lbar_A is subject state's average PP.
      3) Adjust state s class-of-interest: Ltilde_{s,ci} = F_s * L_{s,ci}.
    Final complement: exposure-weighted average of Ltilde_{s,ci} across related states using each
    state's exposures for the class of interest.
    (Refs: WM Ch.12 Harwayne example and exposition.)
    """
    X_A = inputs.target_class_exposures.astype(float)
    w_A = X_A / X_A.sum()
    Lbar_A = float(inputs.target_avg_pure_premium)

    adjusted_ci = []
    weights = []
    for state, L_s in inputs.related_state_class_pp.items():
        L_s = L_s.astype(float).reindex(w_A.index)
        if L_s.isna().any():
            missing = L_s.index[L_s.isna()].tolist()
            raise ValueError(f"Related state {state} missing class PP for classes: {missing}")
        Lhat_s = float((w_A * L_s).sum())
        if Lhat_s <= 0:
            raise ValueError(f"Reweighted average pure premium <= 0 for state {state}")
        F_s = Lbar_A / Lhat_s

        # class-of-interest must exist for state s
        if inputs.class_of_interest not in L_s.index:
            raise ValueError(f"class_of_interest {inputs.class_of_interest} not in state {state}")

        L_tilde_s_ci = F_s * float(L_s[inputs.class_of_interest])

        X_s = inputs.related_state_class_exposures[state].astype(float)
        if inputs.class_of_interest not in X_s.index:
            raise ValueError(f"class_of_interest {inputs.class_of_interest} not in exposures for state {state}")
        X_s_ci = float(X_s[inputs.class_of_interest])

        adjusted_ci.append(L_tilde_s_ci)
        weights.append(X_s_ci)

    total_w = sum(weights)
    if total_w <= 0:
        raise ValueError("Total exposures for class_of_interest across related states must be > 0")

    # Exposure-weighted average of adjusted class PP across related states
    return sum(w * v for w, v in zip(weights, adjusted_ci)) / total_w
