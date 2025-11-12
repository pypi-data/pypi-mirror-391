"""
Complement calculation tools for ratemaking

This subpackage provides complement methods including:
- First-Dollar methods from Werner & Modlin Chapter 12
"""

from .first_dollar import (
    trended_present_rates_loss_cost,
    trended_present_rates_rate_change_factor,
    larger_group_applied_rate_change_to_present_rate,
    HarwayneInputs,
    harwayne_complement,
)

__all__ = [
    'trended_present_rates_loss_cost',
    'trended_present_rates_rate_change_factor', 
    'larger_group_applied_rate_change_to_present_rate',
    'HarwayneInputs',
    'harwayne_complement',
]
