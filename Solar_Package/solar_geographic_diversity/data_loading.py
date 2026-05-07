# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/data_loading.py

import os
import requests
import pandas as pd
from io import StringIO

def load_credentials(filepath, sheet_name="API_Credentials"):
    """
    Load API credentials (API_KEY, API_URL, EMAIL) from a specified sheet in the Excel file.
    Expected columns: API_KEY, API_URL, EMAIL
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Excel file not found at {filepath}")
   
    df_creds = pd.read_excel(filepath, sheet_name=sheet_name)
    required_cols = {'API_KEY', 'API_URL', 'EMAIL'}
    if not required_cols.issubset(df_creds.columns):
        raise ValueError(f"'{sheet_name}' must contain columns: {required_cols}")
   
    # Assume credentials are in the first row
    creds = df_creds.iloc[0].to_dict()
    api_key = creds['API_KEY']
    api_url = creds['API_URL']
    email = creds['EMAIL']
   
    if not api_key:
        raise ValueError("API_KEY is missing in the Excel file.")
    if not api_url:
        raise ValueError("API_URL is missing in the Excel file.")
    if not email:
        raise ValueError("EMAIL is missing in the Excel file.")
   
    return api_key, api_url, email

def load_locations(filepath, sheet_name="locations"):
    """
    Load locations from the specified sheet in the Excel file.
    Expected columns: Name, Latitude, Longitude, State
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Locations file not found at {filepath}")
   
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    required_cols = {'Name', 'Latitude', 'Longitude', 'State'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"'{sheet_name}' must contain columns: {required_cols}")
    return df

def load_config(filepath, sheet_name="config"):
    """
    Load config parameters from the specified sheet in the Excel file.
    Expected columns: Parameter, Value
    Example rows:
       Parameter     Value
       Threshold     0.00005
       StartYear     2018
       EndYear       2023
       StartHour     7
       EndHour       19
       Area          1
       Efficiency    0.21
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Excel file not found at {filepath}")
   
    df_config = pd.read_excel(filepath, sheet_name=sheet_name)
    required_cols = {'Parameter', 'Value'}
    if not required_cols.issubset(df_config.columns):
        raise ValueError(f"'{sheet_name}' must contain columns: {required_cols}")
   
    config_dict = {}
    for _, row in df_config.iterrows():
        param = str(row['Parameter']).strip()
        value = str(row['Value']).strip()
        # Attempt to parse numbers if possible
        try:
            # float() can handle integers and floats
            value_parsed = float(value)
            # But if it's an integer (like 7) we can keep it int
            if value_parsed.is_integer():
                value_parsed = int(value_parsed)
            config_dict[param] = value_parsed
        except ValueError:
            # fallback to string if not numeric
            config_dict[param] = value
    return config_dict

def fetch_nsrdb_data(lat, lon, year, api_key, api_url, email, attributes="dni,dhi,clearsky_dhi,clearsky_dni", interval=60):
    """
    Fetch NSRDB data for a given location (lat, lon) and year using provided API credentials.
    """
    params = {
        "api_key": api_key,
        "wkt": f"POINT({lon} {lat})",
        "attributes": attributes,
        "names": year,
        "utc": "true",
        "leap_day": "false",
        "interval": interval,
        "email": email
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data, skiprows=2)
        df['Year'] = year
        return df
    else:
        raise ConnectionError(
            f"Error fetching data for {lat}, {lon}, year {year}: "
            f"{response.status_code} {response.text}"
        )
