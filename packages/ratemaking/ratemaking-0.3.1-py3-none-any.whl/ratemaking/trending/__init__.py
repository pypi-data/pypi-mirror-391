"""
Trending analysis tools for P&C ratemaking

This subpackage provides tools for:
- Future average date calculations (written, earned, accident dates)
"""

from .trend_analysis import (
    future_average_written_date,
    future_average_earned_date,
    future_average_accident_date,
)

__all__ = [
    'future_average_written_date',
    'future_average_earned_date',
    'future_average_accident_date',
]
