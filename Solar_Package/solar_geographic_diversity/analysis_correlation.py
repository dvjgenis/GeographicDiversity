# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/analysis_correlation.py

def correlation_analysis(df1, df2, start_year=2018, end_year=2023):
    """
    Calculate the Pearson correlation coefficient between the power outputs of two locations.
   
    Parameters:
        df1 (pd.DataFrame): First DataFrame with 'Datetime' and 'Power_Output'.
        df2 (pd.DataFrame): Second DataFrame with 'Datetime' and 'Power_Output'.
        start_year (int): Start year for filtering.
        end_year (int): End year for filtering.
   
    Returns:
        float: Pearson correlation coefficient between the two power outputs.
    """
    # Filter by year and set index to Datetime
    df1_filtered = df1[(df1['Datetime'].dt.year >= start_year) & (df1['Datetime'].dt.year <= end_year)].set_index('Datetime')
    df2_filtered = df2[(df2['Datetime'].dt.year >= start_year) & (df2['Datetime'].dt.year <= end_year)].set_index('Datetime')

    # Align the DataFrames by their datetime index
    df1_aligned, df2_aligned = df1_filtered.align(df2_filtered, join='inner')

    # Calculate Pearson correlation
    correlation = df1_aligned['Power_Output'].corr(df2_aligned['Power_Output'])
    return correlation