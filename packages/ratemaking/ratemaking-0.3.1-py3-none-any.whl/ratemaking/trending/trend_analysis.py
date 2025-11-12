"""
Trend analysis and date calculation functions for actuarial ratemaking

This module provides:
- Future average date calculations (written, earned, accident dates)
"""

from datetime import datetime, date
from typing import Union
from dateutil.relativedelta import relativedelta


def _parse_date(input_date: Union[date, datetime, str]) -> date:
    """
    Parse various date input formats into a date object.
    
    Args:
        input_date: Date as datetime.date, datetime.datetime, or string
        
    Returns:
        date object
        
    Raises:
        ValueError: If string format cannot be parsed
        TypeError: If input type is not supported
    """
    if isinstance(input_date, date) and not isinstance(input_date, datetime):
        return input_date
    elif isinstance(input_date, datetime):
        return input_date.date()
    elif isinstance(input_date, str):
        for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%m-%d-%Y', '%m-%d-%y']:
            try:
                return datetime.strptime(input_date, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date string: {input_date}. Supported formats: MM/DD/YYYY, MM/DD/YY, YYYY-MM-DD, MM-DD-YYYY, MM-DD-YY")
    else:
        raise TypeError(f"Expected date, datetime, or string, got {type(input_date)}")


def future_average_written_date(
    effective_date: Union[date, datetime, str],
    rates_in_effect_months: Union[int, float]
) -> date:
    """
    Calculate the future average written date for policies.
    
    This is the midpoint of the period during which policies will be written
    under the proposed rates. Uses actual calendar months for precision.
    
    Args:
        effective_date: Date when proposed rates take effect
        rates_in_effect_months: Number of months the rates will be in effect
        
    Returns:
        Future average written date as a date object
        
    Example:
        >>> future_average_written_date('1/1/2017', 12)
        datetime.date(2017, 7, 1)
    """
    eff_date = _parse_date(effective_date)
    
    half_months = rates_in_effect_months / 2
    whole_months = int(half_months)
    remaining_fraction = half_months - whole_months
    
    result_date = eff_date + relativedelta(months=whole_months)
    
    if remaining_fraction > 0:
        days_in_month = (result_date + relativedelta(months=1) - result_date).days
        additional_days = int(days_in_month * remaining_fraction)
        result_date = result_date + relativedelta(days=additional_days)
    
    return result_date


def future_average_earned_date(
    effective_date: Union[date, datetime, str],
    rates_in_effect_months: Union[int, float],
    policy_term_months: Union[int, float]
) -> date:
    """
    Calculate the future average earned date for policies.
    
    This is the midpoint between when the first policy starts earning premium
    (the effective date) and when the last policy expires (effective date plus
    rates in effect period plus policy term). Uses actual calendar months for precision.
    
    Args:
        effective_date: Date when proposed rates take effect
        rates_in_effect_months: Number of months the rates will be in effect
        policy_term_months: Length of the policy term in months
        
    Returns:
        Future average earned date as a date object
        
    Example:
        >>> future_average_earned_date('1/1/2017', 12, 6)
        datetime.date(2017, 10, 1)
    """
    eff_date = _parse_date(effective_date)
    
    total_months = rates_in_effect_months + policy_term_months
    half_months = total_months / 2
    whole_months = int(half_months)
    remaining_fraction = half_months - whole_months
    
    result_date = eff_date + relativedelta(months=whole_months)
    
    if remaining_fraction > 0:
        days_in_month = (result_date + relativedelta(months=1) - result_date).days
        additional_days = int(days_in_month * remaining_fraction)
        result_date = result_date + relativedelta(days=additional_days)
    
    return result_date


def future_average_accident_date(
    effective_date: Union[date, datetime, str],
    rates_in_effect_months: Union[int, float],
    policy_term_months: Union[int, float]
) -> date:
    """
    Calculate the future average accident date for policies.
    
    This is identical to the future average earned date, as accidents are
    assumed to occur uniformly during the policy term when premiums are earned.
    
    Args:
        effective_date: Date when proposed rates take effect
        rates_in_effect_months: Number of months the rates will be in effect
        policy_term_months: Length of the policy term in months
        
    Returns:
        Future average accident date as a date object
        
    Example:
        >>> future_average_accident_date('1/1/2017', 12, 6)
        datetime.date(2017, 10, 1)
    """
    return future_average_earned_date(effective_date, rates_in_effect_months, policy_term_months)


__all__ = [
    'future_average_written_date',
    'future_average_earned_date', 
    'future_average_accident_date'
]
