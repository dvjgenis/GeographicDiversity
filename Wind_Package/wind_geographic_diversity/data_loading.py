# GeographicDiversity_Package/Wind_Package/wind_geographic_diversity/data_loading.py

import datetime
import pandas as pd
import meteostat
import hashlib
from haversine import haversine, Unit

def create_dataframe(lat, lon, name, state):
    """Create a DataFrame for a specific location."""
    return pd.DataFrame({
        'Name': [name],
        'Latitude': [lat],
        'Longitude': [lon],
        'State': [state]
    })

def nan_weather(weather_df):
    """Check if the DataFrame has all NaN values in specific columns."""
    columns_used = ['temp', 'rhum', 'pres', 'wspd']
    return weather_df[columns_used].isnull().all().any()

def compute_df_hash(df: pd.DataFrame) -> str:
    """
    Compute a SHA256 hash of the DataFrame contents for a simple checksum.
    Sorts columns, converts to CSV (in-memory), and hashes that CSV with SHA256.
    """
    sorted_cols = sorted(df.columns)
    csv_bytes = df[sorted_cols].to_csv(index=False).encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()

def validity_checks(df: pd.DataFrame,
                    min_temp=-100, max_temp=60,
                    max_wspd=150.0,
                    coverage_warning_ratio=0.8):
    """
    Perform basic sanity checks on the DataFrame:
      - Temperature range check
      - Wind speed range check
      - (Optional) coverage check

    Raises a ValueError if data looks suspicious.
    """
    # 1. Temperature range check
    if 'temp' in df.columns:
        actual_min_temp = df['temp'].min(skipna=True)
        actual_max_temp = df['temp'].max(skipna=True)
        if actual_min_temp < min_temp or actual_max_temp > max_temp:
            raise ValueError(
                f"Temperature out of plausible bounds: {actual_min_temp} / {actual_max_temp} "
                f"(expected between {min_temp} and {max_temp})."
            )
   
    # 2. Wind speed range check
    if 'wspd' in df.columns:
        max_wind_observed = df['wspd'].max(skipna=True)
        if max_wind_observed > max_wspd:
            raise ValueError(
                f"Wind speed {max_wind_observed} m/s exceeds maximum of {max_wspd} m/s. Data suspect."
            )

    # 3. (Optional) coverage check
    # For example, if we expect about 8760 hours in a typical year,
    # we can issue a warning if coverage < 80% (arbitrary ratio).
    total_rows = len(df)
    # This is simplistic: for a 1-year range, we expect ~8760 hours.
    # If data covers multiple years, you'd refine the expected_hours calculation.
    expected_hours = 8760  
    if total_rows < coverage_warning_ratio * expected_hours:
        # We won't raise an error, but you *could*:
        print(f"WARNING: Data coverage is only {total_rows} rows. Expected ~{expected_hours}. Potentially incomplete data.")

def get_weather_data(lat, lon,
                     start_year=2018, end_year=2023,
                     expected_hash=None):
    """
    Fetch hourly weather data from Meteostat for a given lat/lon, from start_year to end_year.
    Performs:
      - Station selection (tries multiple if data is NaN).
      - Basic checksum if `expected_hash` is provided.
      - Basic validity checks (range checks, coverage checks).
   
    Returns:
      (hourly_data, station, df_hash)
    Raises ValueError if data fails checks or if hash mismatches.
    """
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    end_date = datetime.datetime(end_year, 12, 31, 23, 0)

    stations = meteostat.Stations().nearby(lat, lon).fetch()
    if stations.empty:
        raise ValueError("No weather stations found nearby the specified location.")

    station_idx = 0
    max_stations = len(stations)
    hourly_data = pd.DataFrame()
    station = pd.DataFrame()

    while station_idx < max_stations:
        current_station = stations.iloc[[station_idx]]
        station_id = current_station.index[0]

        hourly_data = meteostat.Hourly(current_station, start_date, end_date).fetch()

        if not nan_weather(hourly_data):
            station = current_station
            break
        station_idx += 1

    if hourly_data.empty or nan_weather(hourly_data):
        raise ValueError("All nearby weather stations returned NaN data.")

    # Compute local hash
    df_hash = compute_df_hash(hourly_data)

    # If we have a known/expected hash, compare
    if expected_hash and df_hash.lower() != expected_hash.lower():
        raise ValueError(
            f"Data hash mismatch! Expected={expected_hash}, got={df_hash}. "
            "Data may be invalid or changed."
        )

    # Run basic validity checks (temp/wspd coverage)
    validity_checks(hourly_data)

    return hourly_data, station, df_hash

def load_all_locations():
    """
    (Optional) Load & concatenate data for predefined, hardcoded locations.
    """
    locations = [
        (43.48076, -92.61346, 'Howard, IA', 'Iowa'),
        (40.43372, -95.43277, 'Atchison, MO', 'Missouri'),
        (40.39824, -92.51861, 'Schuyler, MO', 'Missouri'),
        (40.29, -88.51, 'McLean, IL', 'Illinois'),
        (40.10693, -88.59987, 'Piatt, IL', 'Illinois'),
        (38.18992, -90.2056, 'Monroe, IL', 'Illinois'),
        (36.29707, -93.35605, 'Carroll, AR', 'Arkansas')
    ]

    df_all = pd.DataFrame()
    for lat, lon, name, state in locations:
        df = create_dataframe(lat, lon, name, state)
        df_all = pd.concat([df_all, df], ignore_index=True)
    return df_all