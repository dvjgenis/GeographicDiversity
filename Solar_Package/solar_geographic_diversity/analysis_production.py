# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/analysis_production.py

def filter_and_compare_zero_output(df1, df2, start_year=2018, end_year=2023):
    """
    Compare two DataFrames for hours where one location has zero output while the other does not.
   
    Parameters:
        df1 (pd.DataFrame): First DataFrame with 'Datetime', 'Power_Output', and 'Power_Output_Baseline'.
        df2 (pd.DataFrame): Second DataFrame with 'Datetime', 'Power_Output', and 'Power_Output_Baseline'.
        start_year (int): Start year for filtering.
        end_year (int): End year for filtering.
   
    Returns:
        tuple: Total hours with zero output, percentage of such hours, total possible hours.
    """
    # Filter by year
    df1_filtered = df1[(df1['Datetime'].dt.year >= start_year) & (df1['Datetime'].dt.year <= end_year)].set_index('Datetime')
    df2_filtered = df2[(df2['Datetime'].dt.year >= start_year) & (df2['Datetime'].dt.year <= end_year)].set_index('Datetime')

    # Align the DataFrames by their datetime index
    df1_aligned, df2_aligned = df1_filtered.align(df2_filtered, join='inner')

    # Define the condition for one meeting baseline and the other not
    condition = (
        ((df1_aligned['Power_Output'] == df1_aligned['Power_Output_Baseline']) & (df2_aligned['Power_Output'] < df2_aligned['Power_Output_Baseline'])) |
        ((df1_aligned['Power_Output'] < df1_aligned['Power_Output_Baseline']) & (df2_aligned['Power_Output'] == df2_aligned['Power_Output_Baseline']))
    )

    # Calculate results
    total_hours_with_zero_output = condition.sum()
    total_possible_hours = len(condition)
    percentage_hours = (total_hours_with_zero_output / total_possible_hours * 100) if total_possible_hours > 0 else 0

    return total_hours_with_zero_output, percentage_hours, total_possible_hours