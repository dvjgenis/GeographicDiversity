# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/analysis_absolute_difference.py

import pandas as pd

def filter_and_compare_abs_dif(df1, df2, start_year=2018, end_year=2023, threshold=0.05):
    """
    Calculate the number and percentage of hours where the absolute power difference
    between two sites exceeds a threshold within a specified date range (start_year -> end_year).
    """
    start_date = pd.Timestamp(f'{start_year}-01-01 00:00')
    end_date = pd.Timestamp(f'{end_year}-12-31 23:00')
    full_date_range = pd.date_range(start=start_date, end=end_date, freq='H')

    # Reindex both DataFrames so they have entries for every hour in [start_date, end_date]
    df1_full = df1.reindex(full_date_range)
    df2_full = df2.reindex(full_date_range)

    total_possible_hours = len(full_date_range)

    power_diff = abs(df1_full['power'] - df2_full['power']).fillna(0)
    hours_above_threshold = (power_diff > threshold).sum()
    percentage_above_threshold = (
        (hours_above_threshold / total_possible_hours) * 100
        if total_possible_hours > 0 else 0
    )

    return hours_above_threshold, percentage_above_threshold, total_possible_hours