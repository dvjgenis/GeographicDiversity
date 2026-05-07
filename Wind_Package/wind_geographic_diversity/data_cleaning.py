# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/data_cleaning.py

import pandas as pd
import math

def power_generation(df):
    """Calculate power generation based on wind speed data using a predefined power curve."""
    power_curve = {
        0: 0, 1: -0.5, 2: -0.5, 3: 1.2, 4: 7.2, 5: 14.5, 6: 24.7, 7: 37.9,
        8: 58.7, 9: 74.8, 10: 85.1, 11: 90.2, 12: 94.7, 13: 95.3, 14: 95.1,
        15: 94.2, 16: 92.9, 17: 91.2, 18: 88.9, 19: 87.1, 20: 84.1, 21: 81.3,
        22: 78.6, 23: 75.1, 24: 74.3, 25: 71.7
    }
   
    def interpolate_power(wspd):
        if wspd <= 25:
            lower = math.floor(wspd)
            upper = math.ceil(wspd)
            if lower == upper:
                return power_curve.get(lower, 0)
            else:
                lower_power = power_curve.get(lower, 0)
                upper_power = power_curve.get(upper, 0)
                return lower_power + (upper_power - lower_power) * (wspd - lower)
        else:
            return 0
   
    df["power"] = df["wspd"].apply(interpolate_power) / 1000.0  # Convert to MW

def filter_data(df, start_date='2018-01-01', end_date=None):
    """
    Filter data to include only records between a specific start_date and (optionally) end_date.
   
    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        start_date (str or pd.Timestamp): The start date (inclusive).
        end_date (str or pd.Timestamp, optional): The end date (inclusive).
   
    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    if 'time' in df.columns:
        # If 'time' is a column, set it as the index
        df = df.reset_index(drop=True)
        df = df.set_index("time")

    if start_date:
        df = df.loc[df.index >= pd.Timestamp(start_date)]
    if end_date:
        df = df.loc[df.index <= pd.Timestamp(end_date)]

    return df