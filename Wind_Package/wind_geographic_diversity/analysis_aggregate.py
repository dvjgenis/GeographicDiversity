# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/analysis_aggregate.py

import pandas as pd

def aggregate_pair_analysis(df1, df2):
    """
    Computes aggregate production metrics for two wind sites.
    
    Parameters:
        df1 (pd.DataFrame): DataFrame for site 1. Must have a time index and a 'power' column.
        df2 (pd.DataFrame): DataFrame for site 2. Must have a time index and a 'power' column.
       
    Returns:
        dict: Metrics including counts of nonzero production hours, means, standard deviations,
              coefficients of variation (CV), ratios of aggregate to individual averages, percentage differences,
              and the total number of hours.
    """
    # Align the two DataFrames on the time index
    df1_aligned, df2_aligned = df1.align(df2, join='inner', axis=0)
    
    # Calculate aggregate production (sum of the two sites)
    agg_production = df1_aligned['power'] + df2_aligned['power']
    
    # Count hours with nonzero output for each site and for the aggregate
    count_site1 = (df1_aligned['power'] > 0).sum()
    count_site2 = (df2_aligned['power'] > 0).sum()
    count_agg = (agg_production > 0).sum()
    
    # Total number of hours
    total_hours = len(agg_production)
    
    # Calculate means
    mean_site1 = df1_aligned['power'].mean()
    mean_site2 = df2_aligned['power'].mean()
    mean_agg = agg_production.mean()
    
    # Calculate standard deviations
    std_site1 = df1_aligned['power'].std()
    std_site2 = df2_aligned['power'].std()
    std_agg = agg_production.std()
    
    # Compute coefficients of variation (CV = std / mean)
    cv_site1 = std_site1 / mean_site1 if mean_site1 != 0 else None
    cv_site2 = std_site2 / mean_site2 if mean_site2 != 0 else None
    cv_agg = std_agg / mean_agg if mean_agg != 0 else None
    
    # Compute average metrics for individual sites for comparison
    mean_indiv = (mean_site1 + mean_site2) / 2
    std_indiv = (std_site1 + std_site2) / 2
    cv_indiv = (cv_site1 + cv_site2) / 2 if cv_site1 is not None and cv_site2 is not None else None
    count_indiv = (count_site1 + count_site2) / 2
    
    # Compute ratios: aggregate metric divided by average individual metric
    mean_ratio = mean_agg / mean_indiv if mean_indiv != 0 else None
    std_ratio = std_agg / std_indiv if std_indiv != 0 else None
    cv_ratio = cv_agg / cv_indiv if cv_indiv != 0 else None
    count_ratio = count_agg / count_indiv if count_indiv != 0 else None
    
    # Calculate percentage differences (relative difference from the individual average)
    mean_percent = (mean_ratio - 1) * 100 if mean_ratio is not None else None
    std_percent = (std_ratio - 1) * 100 if std_ratio is not None else None
    cv_percent = (cv_ratio - 1) * 100 if cv_ratio is not None else None
    count_percent = (count_ratio - 1) * 100 if count_ratio is not None else None

    # Calculate difference of Output mean vs. mean of individual means
    count_difference = count_agg - ((count_site1 + count_site2) / 2)
    
    return {
        'Count_Site1': count_site1,
        'Count_Site2': count_site2,
        'Count_Aggregate': count_agg,
        'Mean_Site1': mean_site1,
        'Mean_Site2': mean_site2,
        'Mean_Aggregate': mean_agg,
        'Count_Difference': count_difference,
        'Std_Site1': std_site1,
        'Std_Site2': std_site2,
        'Std_Aggregate': std_agg,
        'CV_Site1': cv_site1,
        'CV_Site2': cv_site2,
        'CV_Aggregate': cv_agg,
        'Mean_Ratio': mean_ratio,
        'Std_Ratio': std_ratio,
        'CV_Ratio': cv_ratio,
        'Count_Ratio': count_ratio,
        'Mean_Percent': mean_percent,
        'Std_Percent': std_percent,
        'CV_Percent': cv_percent,
        'Count_Percent': count_percent,
        'Total_Hours': total_hours
    }