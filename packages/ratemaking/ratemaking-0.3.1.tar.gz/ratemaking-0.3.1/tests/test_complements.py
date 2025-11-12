# pytest tests for complement tools

import pytest
import pandas as pd
from datetime import date, datetime
from ratemaking.complements import (
    trended_present_rates_loss_cost,
    trended_present_rates_rate_change_factor,
    larger_group_applied_rate_change_to_present_rate,
    HarwayneInputs,
    harwayne_complement,
)
from ratemaking.complements.first_dollar import _to_years


# -----------------------------
# Helper function tests
# -----------------------------
def test_to_years():
    """Test the _to_years helper function."""
    # Test with date objects
    start_date = date(2023, 1, 1)
    end_date = date(2024, 1, 1)
    years = _to_years(start_date, end_date)
    
    # Should be approximately 1 year (365 days / 365.2425)
    assert abs(years - 1.0) < 0.01
    
    # Test with datetime objects
    start_dt = datetime(2023, 6, 15, 10, 30)
    end_dt = datetime(2025, 6, 15, 15, 45)
    years_dt = _to_years(start_dt, end_dt)
    
    # Should be approximately 2 years
    assert abs(years_dt - 2.0) < 0.01
    
    # Test mixed date and datetime
    mixed_years = _to_years(start_date, end_dt)
    assert isinstance(mixed_years, float)
    assert mixed_years > 2.0


# -----------------------------
# Trended Present Rates - Loss Cost
# -----------------------------
def test_trended_present_rates_loss_cost_basic():
    """Test basic trended present rates complement calculation."""
    present_rate = 100.0
    prior_indicated_factor = 1.10  # 10% indicated increase
    prior_implemented_factor = 1.06  # 6% implemented increase
    loss_trend_annual = 0.05  # 5% annual loss trend
    trend_years = 2.0
    
    result = trended_present_rates_loss_cost(
        present_rate=present_rate,
        prior_indicated_factor=prior_indicated_factor,
        prior_implemented_factor=prior_implemented_factor,
        loss_trend_annual=loss_trend_annual,
        trend_years=trend_years
    )
    
    # Manual calculation: 100 * (1.05)^2 * (1.10/1.06)
    expected = 100.0 * (1.05 ** 2) * (1.10 / 1.06)
    assert abs(result - expected) < 0.001


def test_trended_present_rates_loss_cost_with_dates():
    """Test trended present rates with date-based trend calculation."""
    present_rate = 150.0
    prior_indicated_factor = 1.15
    prior_implemented_factor = 1.12
    loss_trend_annual = 0.03
    trend_from = date(2022, 1, 1)
    trend_to = date(2024, 1, 1)  # 2 years
    
    result = trended_present_rates_loss_cost(
        present_rate=present_rate,
        prior_indicated_factor=prior_indicated_factor,
        prior_implemented_factor=prior_implemented_factor,
        loss_trend_annual=loss_trend_annual,
        trend_from=trend_from,
        trend_to=trend_to
    )
    
    # Should be close to manual calculation with 2 years trend
    expected = 150.0 * (1.03 ** 2) * (1.15 / 1.12)
    assert abs(result - expected) < 0.1  # Allow for leap year approximation


def test_trended_present_rates_loss_cost_zero_trend():
    """Test with zero trend."""
    result = trended_present_rates_loss_cost(
        present_rate=100.0,
        prior_indicated_factor=1.20,
        prior_implemented_factor=1.15,
        loss_trend_annual=0.0,
        trend_years=5.0
    )
    
    # With zero trend, result should just be present_rate * residual_ratio
    expected = 100.0 * (1.20 / 1.15)
    assert abs(result - expected) < 0.001


# -----------------------------
# Trended Present Rates - Rate Change Factor
# -----------------------------
def test_trended_present_rates_rate_change_factor_basic():
    """Test rate change factor form of trended present rates."""
    prior_indicated_factor = 1.08
    prior_implemented_factor = 1.05
    loss_trend_annual = 0.04
    premium_trend_annual = 0.02
    trend_years = 1.5
    
    result = trended_present_rates_rate_change_factor(
        prior_indicated_factor=prior_indicated_factor,
        prior_implemented_factor=prior_implemented_factor,
        loss_trend_annual=loss_trend_annual,
        premium_trend_annual=premium_trend_annual,
        trend_years=trend_years
    )
    
    # Manual calculation: (1.08/1.05) * ((1.04/1.02)^1.5)
    residual_ratio = prior_indicated_factor / prior_implemented_factor
    net_trend = ((1.0 + loss_trend_annual) / (1.0 + premium_trend_annual)) ** trend_years
    expected = residual_ratio * net_trend
    
    assert abs(result - expected) < 0.001
    assert result > 0  # Should always be positive


def test_trended_present_rates_rate_change_factor_with_dates():
    """Test rate change factor with date inputs."""
    result = trended_present_rates_rate_change_factor(
        prior_indicated_factor=1.12,
        prior_implemented_factor=1.10,
        loss_trend_annual=0.06,
        premium_trend_annual=0.03,
        trend_from=date(2023, 3, 15),
        trend_to=date(2024, 3, 15)  # ~1 year
    )
    
    # Should be approximately (1.12/1.10) * ((1.06/1.03)^1)
    expected_approx = (1.12 / 1.10) * (1.06 / 1.03)
    assert abs(result - expected_approx) < 0.01


# -----------------------------
# Larger Group Applied Rate Change
# -----------------------------
def test_larger_group_applied_rate_change():
    """Test larger group rate change application."""
    present_rate = 85.0
    larger_group_indicated_factor = 1.18
    
    result = larger_group_applied_rate_change_to_present_rate(
        present_rate=present_rate,
        larger_group_indicated_factor=larger_group_indicated_factor
    )
    
    # Should simply be present_rate * factor
    expected = 85.0 * 1.18
    assert abs(result - expected) < 0.001


# -----------------------------
# Harwayne Complement
# -----------------------------
def test_harwayne_complement_basic():
    """Test Harwayne's method with simple multi-state scenario."""
    # Subject state (State A) class exposures
    target_exposures = pd.Series({
        'Class1': 1000,
        'Class2': 500,
        'Class3': 200
    })
    
    # Subject state average pure premium
    target_avg_pp = 120.0
    
    # Related states' class pure premiums
    related_state_pp = {
        'StateB': pd.Series({
            'Class1': 100,
            'Class2': 150,
            'Class3': 80
        }),
        'StateC': pd.Series({
            'Class1': 110,
            'Class2': 140,
            'Class3': 90
        })
    }
    
    # Related states' class exposures
    related_state_exposures = {
        'StateB': pd.Series({
            'Class1': 800,
            'Class2': 600,
            'Class3': 300
        }),
        'StateC': pd.Series({
            'Class1': 1200,
            'Class2': 400,
            'Class3': 100
        })
    }
    
    inputs = HarwayneInputs(
        target_class_exposures=target_exposures,
        target_avg_pure_premium=target_avg_pp,
        related_state_class_pp=related_state_pp,
        related_state_class_exposures=related_state_exposures,
        class_of_interest='Class2'
    )
    
    result = harwayne_complement(inputs)
    
    # Result should be a positive number
    assert isinstance(result, float)
    assert result > 0
    
    # Should be reasonable relative to the class pure premiums
    assert 100 < result < 200  # Between the range of Class2 PP values


def test_harwayne_complement_single_related_state():
    """Test Harwayne method with only one related state."""
    target_exposures = pd.Series({
        'ClassA': 100,
        'ClassB': 200
    })
    
    related_state_pp = {
        'RelatedState': pd.Series({
            'ClassA': 50,
            'ClassB': 75
        })
    }
    
    related_state_exposures = {
        'RelatedState': pd.Series({
            'ClassA': 150,
            'ClassB': 250
        })
    }
    
    inputs = HarwayneInputs(
        target_class_exposures=target_exposures,
        target_avg_pure_premium=60.0,
        related_state_class_pp=related_state_pp,
        related_state_class_exposures=related_state_exposures,
        class_of_interest='ClassA'
    )
    
    result = harwayne_complement(inputs)
    
    # Manual verification for single state case
    w_A = target_exposures / target_exposures.sum()  # [1/3, 2/3]
    L_s = related_state_pp['RelatedState']  # [50, 75]
    Lhat_s = (w_A * L_s).sum()  # (1/3)*50 + (2/3)*75 = 66.67
    F_s = 60.0 / Lhat_s  # adjustment factor
    expected = F_s * 50  # adjusted ClassA PP
    
    assert abs(result - expected) < 0.001


# -----------------------------
# Input Validation Tests
# -----------------------------
def test_trended_present_rates_loss_cost_validation():
    """Test input validation for trended present rates loss cost."""
    # Negative present rate
    with pytest.raises(ValueError, match="present_rate must be >= 0"):
        trended_present_rates_loss_cost(
            present_rate=-10.0,
            prior_indicated_factor=1.1,
            prior_implemented_factor=1.05,
            loss_trend_annual=0.03,
            trend_years=1.0
        )
    
    # Zero/negative prior factors
    with pytest.raises(ValueError, match="prior factors must be > 0"):
        trended_present_rates_loss_cost(
            present_rate=100.0,
            prior_indicated_factor=0.0,
            prior_implemented_factor=1.05,
            loss_trend_annual=0.03,
            trend_years=1.0
        )
    
    # Extreme negative trend
    with pytest.raises(ValueError, match="loss_trend_annual < -100% is invalid"):
        trended_present_rates_loss_cost(
            present_rate=100.0,
            prior_indicated_factor=1.1,
            prior_implemented_factor=1.05,
            loss_trend_annual=-1.5,  # -150%
            trend_years=1.0
        )
    
    # Missing trend parameters
    with pytest.raises(ValueError, match="Provide trend_years or both trend_from and trend_to"):
        trended_present_rates_loss_cost(
            present_rate=100.0,
            prior_indicated_factor=1.1,
            prior_implemented_factor=1.05,
            loss_trend_annual=0.03
        )


def test_trended_present_rates_rate_change_factor_validation():
    """Test input validation for rate change factor."""
    # Extreme negative premium trend
    with pytest.raises(ValueError, match="premium trend annual must be > -100%"):
        trended_present_rates_rate_change_factor(
            prior_indicated_factor=1.1,
            prior_implemented_factor=1.05,
            loss_trend_annual=0.03,
            premium_trend_annual=-1.2,  # -120%
            trend_years=1.0
        )


def test_larger_group_rate_change_validation():
    """Test input validation for larger group method."""
    # Negative present rate
    with pytest.raises(ValueError, match="Invalid inputs"):
        larger_group_applied_rate_change_to_present_rate(
            present_rate=-5.0,
            larger_group_indicated_factor=1.1
        )
    
    # Zero/negative factor
    with pytest.raises(ValueError, match="Invalid inputs"):
        larger_group_applied_rate_change_to_present_rate(
            present_rate=100.0,
            larger_group_indicated_factor=0.0
        )


def test_harwayne_complement_validation():
    """Test input validation for Harwayne method."""
    # Missing class in related state PP
    target_exposures = pd.Series({'ClassA': 100, 'ClassB': 200})
    
    # Missing ClassB in related state
    related_state_pp = {
        'State1': pd.Series({'ClassA': 50})  # Missing ClassB
    }
    
    related_state_exposures = {
        'State1': pd.Series({'ClassA': 150, 'ClassB': 250})
    }
    
    inputs = HarwayneInputs(
        target_class_exposures=target_exposures,
        target_avg_pure_premium=60.0,
        related_state_class_pp=related_state_pp,
        related_state_class_exposures=related_state_exposures,
        class_of_interest='ClassA'
    )
    
    with pytest.raises(ValueError, match="missing class PP for classes"):
        harwayne_complement(inputs)
    
    # Missing class of interest in related state
    good_related_pp = {
        'State1': pd.Series({'ClassA': 50, 'ClassB': 75})
    }
    
    inputs2 = HarwayneInputs(
        target_class_exposures=target_exposures,
        target_avg_pure_premium=60.0,
        related_state_class_pp=good_related_pp,
        related_state_class_exposures=related_state_exposures,
        class_of_interest='ClassC'  # Doesn't exist
    )
    
    with pytest.raises(ValueError, match="class_of_interest ClassC not in state"):
        harwayne_complement(inputs2)


if __name__ == "__main__":
    pytest.main([__file__])
