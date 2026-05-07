# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/data_cleaning.py

import pandas as pd

def calculate_solar_power(row, area=1, efficiency=0.21):
    """
    Calculate the solar power output based on DNI and DHI values.
    """
    dni = row['DNI']
    dhi = row['DHI']
    total_irradiance = dni + dhi
    # Convert W/m² * area (m²) * efficiency to MW (1 W = 1e-6 MW)
    power_output = (total_irradiance * area * efficiency) / 1_000_000
    return power_output

def calculate_baseline_solar_power(row, area=1, efficiency=0.21):
    """
    Calculate the baseline solar power output based on clear sky DNI and DHI values.
    """
    cs_dni = row['Clearsky DNI']
    cs_dhi = row['Clearsky DHI']
    total_irradiance_baseline = cs_dni + cs_dhi
    power_output_baseline = (total_irradiance_baseline * area * efficiency) / 1_000_000
    return power_output_baseline

def prepare_dataframe(df, area=1, efficiency=0.21):
    """
    Prepare the DataFrame by calculating power outputs and creating a shifted Datetime column.
    Area and Efficiency come from config.
    """
    if not {'Year', 'Month', 'Day', 'Hour', 'Minute'}.issubset(df.columns):
        raise KeyError("Missing columns required to create 'Datetime' (Year, Month, Day, Hour, Minute).")
   
    # Create the Datetime column
    df['Datetime'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    # Shift time by -6 hours (if needed)
    df['Datetime'] = df['Datetime'] - pd.Timedelta(hours=6)

    # Calculate power outputs using config-based area/efficiency
    df['Power_Output'] = df.apply(calculate_solar_power, axis=1, args=(area, efficiency))
    df['Power_Output_Baseline'] = df.apply(calculate_baseline_solar_power, axis=1, args=(area, efficiency))
   
    # Keep relevant columns
    df = df[['Datetime', 'Power_Output', 'DNI', 'DHI',
             'Power_Output_Baseline', 'Clearsky DNI', 'Clearsky DHI',
             'Year', 'Month', 'Day', 'Hour', 'Minute']]
    return df

def filter_dataframe(df, start_year=2018, end_year=2023, start_hour=7, end_hour=19):
    """
    Filter the DataFrame based on year and time range.
    """
    # Filter by year
    df = df[(df['Datetime'].dt.year >= start_year) & (df['Datetime'].dt.year <= end_year)]
    # Filter by hour range
    df = df[(df['Datetime'].dt.hour >= start_hour) & (df['Datetime'].dt.hour < end_hour)]
    return df
