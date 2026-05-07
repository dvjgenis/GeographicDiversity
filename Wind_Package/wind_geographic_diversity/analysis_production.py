# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/analysis_production.py

import pandas as pd

def filter_and_compare_zero_output(df1, df2, start_year=2018, end_year=2023):
    """
    Calculate the number and percentage of hours where one site has zero output
    and the other has more than zero output, and vice versa,
    within the specified start_year to end_year range.
    """
    # Build the date range from start_year to end_year
    start_date = pd.Timestamp(f'{start_year}-01-01 00:00')
    end_date = pd.Timestamp(f'{end_year}-12-31 23:00')
    full_date_range = pd.date_range(start=start_date, end=end_date, freq='H')

    # Reindex df1 and df2 to this full hourly range
    df1_full = df1.reindex(full_date_range)
    df2_full = df2.reindex(full_date_range)

    total_possible_hours = len(full_date_range)

    # Identify hours where one site is zero and the other is nonzero
    zero_and_nonzero = (
        ((df1_full['power'] == 0) & (df2_full['power'] > 0)) |
        ((df1_full['power'] > 0) & (df2_full['power'] == 0))
    ).fillna(False)

    total_hours_with_zero_output = zero_and_nonzero.sum()
    percentage_hours = (
        (total_hours_with_zero_output / total_possible_hours) * 100
        if total_possible_hours > 0 else 0
    )

    return total_hours_with_zero_output, percentage_hours, total_possible_hours
