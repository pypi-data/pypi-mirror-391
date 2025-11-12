import numpy as np
import pandas as pd
from typing import Optional

def written_to_earned(
    df: pd.DataFrame,
    value_col: str = "written",
    date_col: Optional[str] = None,
    term_months: int = 6,
    freq: Optional[str] = None,
    include_uepr: bool = True,
) -> pd.DataFrame:
    """
    Convert written premium to earned premium using uniform earning pattern.
    
    Assumes policies are written uniformly throughout each period and earn uniformly
    over the policy term. Works for any regular frequency (monthly, quarterly, 
    semi-annual, annual, etc.).

    Parameters
    ----------
    df : DataFrame
        Must contain either:
          - DatetimeIndex or PeriodIndex with regular frequency, or
          - a date column (date_col) convertible to datetime.
        And a numeric column 'value_col' with written premium totals per period.
    value_col : str
        Column name containing written amounts per period.
    date_col : str | None
        Name of the date column (if index is not already datetime/period).
        Dates can be any day in the period; frequency will be inferred.
    term_months : int
        Policy term length in months (e.g., 6 for half-year, 12 for annual).
    freq : str | None
        Pandas offset alias for the input (e.g., 'MS', 'QS', '2QS', 'YS').
        If None, tries to infer from the index; otherwise uses the given alias.
    include_uepr : bool
        If True, computes UEPR per period as the remaining not-yet-earned portion.

    Returns
    -------
    DataFrame
        Same frequency as the input. Always includes:
          - 'earned' (sum of monthly earned back to the input frequency)
          - 'written' (original written)
        If include_uepr=True: includes 'uepr_eop' (end-of-period UEPR at input freq).

    Notes
    -----
    - Assumes uniform writing throughout each period (equivalent to all policies 
      written at the midpoint of the period).
    - Assumes uniform (straight-line) earning over the policy term.
    - For annual policies reported annually: 50% earns in year written, 50% in next year.
    - For annual policies reported semi-annually: 25% / 50% / 25% pattern across 3 semesters.
    - UEPR at end of period is the weighted sum of the unearned tail for each cohort.
    """

    if date_col is not None:
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
    else:
        if not isinstance(df.index, (pd.DatetimeIndex, pd.PeriodIndex)):
            raise ValueError("Provide a DatetimeIndex/PeriodIndex or specify date_col.")
        df = df.copy()

    if isinstance(df.index, pd.PeriodIndex):
        idx_dt = df.index.to_timestamp(how="start")
        if freq is None:
            freq = df.index.freqstr
    else:
        idx_dt = pd.DatetimeIndex(df.index)

    if freq is None:
        freq = pd.infer_freq(idx_dt)
        if freq is None:
            freq = "MS"

    freq_map = {
        'YS': 'Y', 'AS': 'Y', 'Y': 'Y', 'A': 'Y',
        'YS-JAN': 'Y-JAN', 'AS-JAN': 'Y-JAN',
        'MS': 'M', 'M': 'M',
        'QS': 'Q', 'Q': 'Q',
        '2QS': '6M', '2Q': '6M', '2QS-JAN': '6M', '2QS-OCT': '6M'
    }
    period_freq = freq_map.get(freq, freq)

    try:
        as_periods = idx_dt.to_period(freq=period_freq)
    except Exception as e:
        raise ValueError(f"Could not convert index to PeriodIndex with freq '{freq}': {e}")

    df = df.copy()
    df.index = as_periods.to_timestamp(how="start")
    df = df.sort_index()
    full_idx = pd.period_range(df.index.min().to_period(period_freq), df.index.max().to_period(period_freq), freq=period_freq)\
               .to_timestamp(how="start")
    df = df.reindex(full_idx)
    df[value_col] = df[value_col].fillna(0.0)

    def months_between(a: pd.Timestamp, b: pd.Timestamp) -> int:
        return (b.year - a.year) * 12 + (b.month - a.month)

    if len(df.index) >= 2:
        months_per_period = max(1, months_between(df.index[0], df.index[1]))
    else:
        months_per_period = {
            "MS": 1, "M": 1,
            "QS": 3, "Q": 3,
            "2QS": 6, "2Q": 6,
            "AS": 12, "A": 12, "YS": 12, "Y": 12
        }.get(str(freq).upper(), 1)

    monthly_index = pd.period_range(
        start=df.index.min().to_period("M"),
        end=(df.index.max() + pd.offsets.MonthBegin(int(months_per_period/2) + term_months)).to_period("M"),
        freq="M"
    ).to_timestamp(how="start")

    written_m = pd.Series(0.0, index=monthly_index)

    for period_start, amt in df[value_col].items():
        num_blocks = max(1.0, months_per_period / term_months)
        amt_per_block = amt / num_blocks
        
        if num_blocks <= 1:
            midpoint_offset = months_per_period / 2.0
            if midpoint_offset == int(midpoint_offset):
                midpoint_month = period_start + pd.offsets.MonthBegin(int(midpoint_offset))
                if midpoint_month in monthly_index:
                    written_m.loc[midpoint_month] += amt
            else:
                month_before = period_start + pd.offsets.MonthBegin(int(midpoint_offset))
                month_after = period_start + pd.offsets.MonthBegin(int(midpoint_offset) + 1)
                if month_before in monthly_index:
                    written_m.loc[month_before] += amt * 0.5
                if month_after in monthly_index:
                    written_m.loc[month_after] += amt * 0.5
        else:
            for block_idx in range(int(num_blocks)):
                block_start_offset = block_idx * term_months
                block_midpoint_offset = block_start_offset + term_months / 2.0
                if block_midpoint_offset == int(block_midpoint_offset):
                    block_midpoint_month = period_start + pd.offsets.MonthBegin(int(block_midpoint_offset))
                    if block_midpoint_month in monthly_index:
                        written_m.loc[block_midpoint_month] += amt_per_block
                else:
                    month_before = period_start + pd.offsets.MonthBegin(int(block_midpoint_offset))
                    month_after = period_start + pd.offsets.MonthBegin(int(block_midpoint_offset) + 1)
                    if month_before in monthly_index:
                        written_m.loc[month_before] += amt_per_block * 0.5
                    if month_after in monthly_index:
                        written_m.loc[month_after] += amt_per_block * 0.5

    earn_curve = np.ones(term_months, dtype=float) / float(term_months)

    earned_m = pd.Series(0.0, index=written_m.index)
    for k, w in enumerate(earn_curve):
        earned_m += written_m.shift(k, fill_value=0.0) * w

    if include_uepr:
        tail_weights = np.r_[earn_curve[::-1].cumsum()[::-1][1:], 0.0]
        uepr_m = pd.Series(0.0, index=written_m.index)
        for k, tail_w in enumerate(tail_weights):
            uepr_m += written_m.shift(k, fill_value=0.0) * tail_w
    else:
        uepr_m = None

    def period_bucket_start(ts: pd.Timestamp) -> pd.Timestamp:
        return ts

    month_to_period = {}
    for period_start in df.index:
        for m in range(months_per_period):
            month = period_start + pd.offsets.MonthBegin(m)
            if month <= monthly_index.max():
                month_to_period[month] = period_start
    
    earned_m_with_period = earned_m.to_frame("earned")
    earned_m_with_period["period"] = earned_m_with_period.index.map(lambda x: month_to_period.get(x))
    
    earned = (
        earned_m_with_period[earned_m_with_period["period"].notna()]
        .groupby("period")["earned"].sum()
        .reindex(df.index, fill_value=0.0)
    )

    if include_uepr:
        last_month_in_period = {}
        for period_start in df.index:
            last_month = period_start + pd.offsets.MonthBegin(months_per_period - 1)
            if last_month in uepr_m.index:
                last_month_in_period[period_start] = last_month
        
        uepr_eop = pd.Series(index=df.index, dtype=float, name="uepr_eop")
        for period_start, last_month in last_month_in_period.items():
            uepr_eop.loc[period_start] = uepr_m.loc[last_month]
        uepr_eop = uepr_eop.fillna(0.0)
    else:
        uepr_eop = None

    out = pd.DataFrame(index=df.index)
    out["written"] = df[value_col]
    out["earned"] = earned
    if include_uepr:
        out["uepr_eop"] = uepr_eop

    return out
