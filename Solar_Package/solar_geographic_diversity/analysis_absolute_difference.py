# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/analysis_absolute_difference.py

def filter_and_compare_abs_dif(df1, df2, start_year=2018, end_year=2023, threshold=0.00005):
    """
    Calculate the number and percentage of hours where the absolute power difference
    between two locations exceeds a threshold.
   
    Parameters:
        df1 (pd.DataFrame): First DataFrame with 'Datetime' and 'Power_Output'.
        df2 (pd.DataFrame): Second DataFrame with 'Datetime' and 'Power_Output'.
        start_year (int): Start year for filtering.
        end_year (int): End year for filtering.
        threshold (float): Threshold for the absolute difference in power output (MW).
   
    Returns:
        tuple: (hours_above_threshold, percentage_above_threshold, total_possible_hours)
    """
    # Filter by year and set index to Datetime
    df1_filtered = df1[(df1['Datetime'].dt.year >= start_year) & (df1['Datetime'].dt.year <= end_year)].set_index('Datetime')
    df2_filtered = df2[(df2['Datetime'].dt.year >= start_year) & (df2['Datetime'].dt.year <= end_year)].set_index('Datetime')

    # Align the DataFrames by their datetime index
    df1_aligned, df2_aligned = df1_filtered.align(df2_filtered, join='inner')

    # Calculate absolute power difference
    power_diff = abs(df1_aligned['Power_Output'] - df2_aligned['Power_Output'])

    # Calculate results
    hours_above_threshold = (power_diff > threshold).sum()
    total_possible_hours = len(power_diff)
    percentage_above_threshold = (hours_above_threshold / total_possible_hours * 100) if total_possible_hours > 0 else 0

    return hours_above_threshold, percentage_above_threshold, total_possible_hours