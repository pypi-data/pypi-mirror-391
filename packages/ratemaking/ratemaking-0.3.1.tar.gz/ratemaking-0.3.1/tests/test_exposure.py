import pytest
import pandas as pd
import numpy as np
from ratemaking.exposure import written_to_earned


def test_written_to_earned_annual_policies():
    """Test written to earned conversion for annual policies with straight-line earning."""
    df = pd.DataFrame({
        'calendar_year': ['2010', '2011'],
        'exposures_written': [2880, 0]
    })
    df['calendar_year'] = pd.to_datetime(df['calendar_year'])
    
    result = written_to_earned(
        df=df,
        value_col='exposures_written',
        date_col='calendar_year',
        term_months=12,
        freq='YS'
    )
    
    expected_earned = [1440, 1440]
    
    assert result['earned'].iloc[0] == expected_earned[0]
    assert result['earned'].iloc[1] == expected_earned[1]
    assert result['written'].iloc[0] == 2880
    assert result['written'].iloc[1] == 0


def test_written_to_earned_semester_annual_policies():
    """Test written to earned for semi-annual reporting with annual policies."""
    df = pd.DataFrame({
        'calendar_semester': ['2023-01-01', '2023-07-01', '2024-01-01'],
        'written_exposure': [5283327, 5547493, 5824868]
    })
    df['calendar_semester'] = pd.to_datetime(df['calendar_semester'])
    
    result = written_to_earned(
        df=df,
        value_col='written_exposure',
        date_col='calendar_semester',
        term_months=12,
        freq='2QS'
    )
    
    assert abs(result['earned'].iloc[0] - 1320832) < 100
    assert abs(result['earned'].iloc[1] - 4028537) < 100
    assert abs(result['earned'].iloc[2] - 5550795) < 100
    assert result['written'].iloc[0] == 5283327
    assert result['written'].iloc[1] == 5547493
    assert result['written'].iloc[2] == 5824868


def test_written_to_earned_semester_6month_policies():
    """Test written to earned for semi-annual reporting with 6-month policies."""
    df = pd.DataFrame({
        'calendar_semester': ['2023-01-01', '2023-07-01', '2024-01-01'],
        'written_exposure': [5283327, 5547493, 5824868]
    })
    df['calendar_semester'] = pd.to_datetime(df['calendar_semester'])
    
    result = written_to_earned(
        df=df,
        value_col='written_exposure',
        date_col='calendar_semester',
        term_months=6,
        freq='2QS'
    )
    
    assert abs(result['earned'].iloc[0] - 2641664) < 100
    assert abs(result['earned'].iloc[1] - 5415410) < 100
    assert abs(result['earned'].iloc[2] - 5686181) < 100
    assert result['written'].iloc[0] == 5283327
    assert result['written'].iloc[1] == 5547493
    assert result['written'].iloc[2] == 5824868


def test_written_to_earned_annual_6month_policies():
    """Test written to earned for annual reporting with 6-month policies."""
    df = pd.DataFrame({
        'calendar_year': ['2010', '2011'],
        'written': [2880, 0]
    })
    df['calendar_year'] = pd.to_datetime(df['calendar_year'])
    
    result = written_to_earned(
        df=df,
        value_col='written',
        date_col='calendar_year',
        term_months=6,
        freq='YS'
    )
    
    assert result['earned'].iloc[0] == 2160
    assert result['earned'].iloc[1] == 720
    assert result['written'].iloc[0] == 2880
    assert result['written'].iloc[1] == 0


def test_written_to_earned_quarterly_annual_policies():
    """Test written to earned for quarterly reporting with annual policies."""
    df = pd.DataFrame({
        'calendar_quarter': ['2024-01-01', '2024-04-01', '2024-07-01', '2024-10-01'],
        'written_exposure': [1423, 1565, 1722, 1894]
    })
    df['calendar_quarter'] = pd.to_datetime(df['calendar_quarter'])
    
    result = written_to_earned(
        df=df,
        value_col='written_exposure',
        date_col='calendar_quarter',
        term_months=12,
        freq='QS'
    )
    
    assert abs(result['earned'].iloc[0] - 178) < 1
    assert abs(result['earned'].iloc[1] - 551) < 1
    assert abs(result['earned'].iloc[2] - 962) < 1
    assert abs(result['earned'].iloc[3] - 1414) < 1
    assert result['written'].iloc[0] == 1423
    assert result['written'].iloc[1] == 1565
    assert result['written'].iloc[2] == 1722
    assert result['written'].iloc[3] == 1894


def test_written_to_earned_with_index():
    """Test written to earned with DatetimeIndex instead of date column."""
    index = pd.date_range(start='2010-01-01', periods=2, freq='YS')
    df = pd.DataFrame({
        'exposures_written': [2880, 0]
    }, index=index)
    
    result = written_to_earned(
        df=df,
        value_col='exposures_written',
        term_months=12,
        freq='YS'
    )
    
    assert result['earned'].iloc[0] == 1440
    assert result['earned'].iloc[1] == 1440


def test_written_to_earned_includes_uepr():
    """Test that UEPR calculation is included by default."""
    df = pd.DataFrame({
        'calendar_year': ['2010', '2011'],
        'exposures_written': [2880, 0]
    })
    df['calendar_year'] = pd.to_datetime(df['calendar_year'])
    
    result = written_to_earned(
        df=df,
        value_col='exposures_written',
        date_col='calendar_year',
        term_months=12,
        freq='YS'
    )
    
    assert 'uepr_eop' in result.columns
    assert abs(result['uepr_eop'].iloc[0] - 1440) < 1
    assert result['uepr_eop'].iloc[1] == 0


def test_written_to_earned_without_uepr():
    """Test written to earned without UEPR calculation."""
    df = pd.DataFrame({
        'calendar_year': ['2010', '2011'],
        'exposures_written': [2880, 0]
    })
    df['calendar_year'] = pd.to_datetime(df['calendar_year'])
    
    result = written_to_earned(
        df=df,
        value_col='exposures_written',
        date_col='calendar_year',
        term_months=12,
        freq='YS',
        include_uepr=False
    )
    
    assert 'uepr_eop' not in result.columns
    assert 'earned' in result.columns
    assert 'written' in result.columns


def test_written_to_earned_quarterly_frequency():
    """Test written to earned with quarterly input frequency."""
    df = pd.DataFrame({
        'quarter': pd.date_range(start='2010-01-01', periods=4, freq='QS'),
        'written': [300, 300, 300, 300]
    })
    
    result = written_to_earned(
        df=df,
        value_col='written',
        date_col='quarter',
        term_months=12,
        freq='QS'
    )
    
    assert len(result) == 4
    assert 'earned' in result.columns
    assert 'written' in result.columns


def test_written_to_earned_empty_dataframe():
    """Test written to earned with single row."""
    df = pd.DataFrame({
        'period': ['2010-01-01'],
        'written': [1200]
    })
    df['period'] = pd.to_datetime(df['period'])
    
    result = written_to_earned(
        df=df,
        value_col='written',
        date_col='period',
        term_months=12,
        freq='YS'
    )
    
    assert len(result) == 1
    assert 'earned' in result.columns


def test_written_to_earned_period_index():
    """Test written to earned with PeriodIndex."""
    index = pd.period_range(start='2010', periods=2, freq='A')
    df = pd.DataFrame({
        'written': [2880, 0]
    }, index=index)
    
    result = written_to_earned(
        df=df,
        value_col='written',
        term_months=12
    )
    
    assert result['earned'].iloc[0] == 1440
    assert result['earned'].iloc[1] == 1440


def test_written_to_earned_missing_values():
    """Test written to earned handles missing values by treating as zero."""
    df = pd.DataFrame({
        'period': pd.date_range(start='2010', periods=3, freq='YS'),
        'written': [1200, np.nan, 600]
    })
    df.set_index('period', inplace=True)
    
    result = written_to_earned(
        df=df,
        value_col='written',
        term_months=12,
        freq='YS'
    )
    
    assert len(result) == 3
    assert abs(result['earned'].iloc[1] - 600) < 0.01


def test_written_to_earned_no_date_index_raises():
    """Test that dataframe without proper date index raises error."""
    df = pd.DataFrame({
        'written': [1200, 0]
    })
    
    with pytest.raises(ValueError, match="Provide a DatetimeIndex"):
        written_to_earned(
            df=df,
            value_col='written',
            term_months=12
        )

