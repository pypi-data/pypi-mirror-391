import pytest
from datetime import date, datetime
from ratemaking.trending import (
    future_average_written_date,
    future_average_earned_date,
    future_average_accident_date,
)


def test_future_average_written_date_basic():
    """Test future average written date with 12 months in effect."""
    result = future_average_written_date('1/1/2017', 12)
    expected = date(2017, 7, 1)
    assert result == expected


def test_future_average_written_date_case_1():
    """Test case: 1/1/17 effective, 12 months in effect."""
    result = future_average_written_date('1/1/2017', 12)
    expected = date(2017, 7, 1)
    assert result == expected


def test_future_average_written_date_case_2():
    """Test case: 5/1/16 effective, 12 months in effect."""
    result = future_average_written_date('5/1/2016', 12)
    expected = date(2016, 11, 1)
    assert result == expected


def test_future_average_earned_date_6_month_term():
    """Test future average earned date with 6-month policy term."""
    result = future_average_earned_date('1/1/2017', 12, 6)
    expected = date(2017, 10, 1)
    assert result == expected


def test_future_average_earned_date_12_month_term_case_1():
    """Test case: 1/1/17 effective, 12 months in effect, 12 month policy term."""
    result = future_average_earned_date('1/1/2017', 12, 12)
    expected = date(2018, 1, 1)
    assert result == expected


def test_future_average_earned_date_12_month_term_case_2():
    """Test case: 5/1/16 effective, 12 months in effect, 12 month policy term."""
    result = future_average_earned_date('5/1/2016', 12, 12)
    expected = date(2017, 5, 1)
    assert result == expected


def test_future_average_accident_date_equals_earned():
    """Test that accident date equals earned date."""
    effective = '1/1/2017'
    rates_in_effect = 12
    policy_term = 6
    
    earned = future_average_earned_date(effective, rates_in_effect, policy_term)
    accident = future_average_accident_date(effective, rates_in_effect, policy_term)
    
    assert earned == accident


def test_future_average_accident_date_12_month_term_case_1():
    """Test case: 1/1/17 effective, 12 months in effect, 12 month policy term."""
    result = future_average_accident_date('1/1/2017', 12, 12)
    expected = date(2018, 1, 1)
    assert result == expected


def test_future_average_accident_date_12_month_term_case_2():
    """Test case: 5/1/16 effective, 12 months in effect, 12 month policy term."""
    result = future_average_accident_date('5/1/2016', 12, 12)
    expected = date(2017, 5, 1)
    assert result == expected


def test_date_input_formats():
    """Test various date input formats."""
    effective_str_slash = '3/15/2020'
    effective_str_dash = '2020-03-15'
    effective_date_obj = date(2020, 3, 15)
    effective_datetime_obj = datetime(2020, 3, 15, 10, 30)
    
    result1 = future_average_written_date(effective_str_slash, 6)
    result2 = future_average_written_date(effective_str_dash, 6)
    result3 = future_average_written_date(effective_date_obj, 6)
    result4 = future_average_written_date(effective_datetime_obj, 6)
    
    assert result1 == result2 == result3 == result4
    assert isinstance(result1, date)


def test_fractional_months():
    """Test handling of fractional month values."""
    result = future_average_written_date('1/1/2017', 7.5)
    assert isinstance(result, date)
    
    result2 = future_average_earned_date('1/1/2017', 12, 3.5)
    assert isinstance(result2, date)


def test_return_type_is_date():
    """Verify all functions return date objects, not datetime."""
    result1 = future_average_written_date('1/1/2017', 12)
    result2 = future_average_earned_date('1/1/2017', 12, 6)
    result3 = future_average_accident_date('1/1/2017', 12, 6)
    
    assert isinstance(result1, date)
    assert isinstance(result2, date)
    assert isinstance(result3, date)
    assert not isinstance(result1, datetime)
    assert not isinstance(result2, datetime)
    assert not isinstance(result3, datetime)


def test_invalid_date_format():
    """Test that invalid date formats raise ValueError."""
    with pytest.raises(ValueError):
        future_average_written_date('invalid-date', 12)


def test_invalid_date_type():
    """Test that invalid date types raise TypeError."""
    with pytest.raises(TypeError):
        future_average_written_date(12345, 12)


def test_leap_year_handling():
    """Test date calculations around leap year."""
    result = future_average_written_date('2/1/2016', 12)
    assert isinstance(result, date)
    assert result.year == 2016
    
    result2 = future_average_earned_date('2/1/2016', 12, 12)
    assert isinstance(result2, date)


def test_year_boundary_crossing():
    """Test calculations that cross year boundaries."""
    result = future_average_written_date('7/1/2017', 12)
    expected = date(2018, 1, 1)
    assert result == expected
    
    result2 = future_average_earned_date('10/1/2017', 6, 6)
    assert result2.year == 2018

