# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/analysis_correlation.py

def correlation_analysis(df1, df2, start_year=2018, end_year=2023):
    """
    Calculate the cumulative Pearson correlation between two sites' power outputs
    within the specified start_year to end_year range.
    """
    # Filter each DataFrame to the target years
    df1_filtered = df1[(df1.index.year >= start_year) & (df1.index.year <= end_year)]
    df2_filtered = df2[(df2.index.year >= start_year) & (df2.index.year <= end_year)]
   
    # Align on common timestamps
    df1_aligned, df2_aligned = df1_filtered.align(df2_filtered, join='inner', axis=0)
   
    # Compute correlation on 'power' column
    correlation = df1_aligned['power'].corr(df2_aligned['power'])
   
    return correlation
