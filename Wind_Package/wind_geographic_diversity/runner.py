import pandas as pd
import os
from datetime import datetime
from .data_loading import get_weather_data
from .data_cleaning import filter_data, power_generation
from .visualization import create_map, plot_absolute_difference
from .heatmaps import (
    aggregate_windspeed_data,
    calculate_min_max,
    create_interactive_heatmap
)
from .analysis_production import filter_and_compare_zero_output
from .analysis_correlation import correlation_analysis
from .analysis_absolute_difference import filter_and_compare_abs_dif
from .utils import calculate_distance

class GeographicDiversityAnalyzer:
    def __init__(self, locations=None, locations_file=None, reports_dir='reports'):
        """
        Initialize the analyzer with a list of locations or an Excel file containing locations.
        """
        self.threshold = 0.05
        self.start_year = 2018
        self.end_year = 2023

        if locations_file:
            self.locations = self._load_locations_from_excel(locations_file)
            self._load_config_from_excel(locations_file)
        elif locations:
            self.locations = locations
        else:
            raise ValueError("Either 'locations' or 'locations_file' must be provided.")

        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Create a separate directory for combined CSV data files.
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)

        self.dataframes = {}       # Cleaned data for each location
        self.dataframes_raw = {}   # Raw data for each location
        self.coordinates = {loc['name']: (loc['lat'], loc['lon']) for loc in self.locations}

        # Example known hashes if you check data integrity
        self.known_hashes = {
            # ...
        }

    def _load_locations_from_excel(self, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name='locations')
            required_cols = {'Name', 'Latitude', 'Longitude', 'State'}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"Missing columns in Excel file: {missing}")

            locs = df.to_dict(orient='records')
            for loc in locs:
                if not all(k in loc for k in ['Name', 'Latitude', 'Longitude', 'State']):
                    raise ValueError(f"Invalid location entry: {loc}")

            return [
                {'name': l['Name'], 'lat': l['Latitude'], 'lon': l['Longitude'], 'state': l['State']}
                for l in locs
            ]
        except Exception as e:
            raise ValueError(f"Error reading Excel file (locations sheet): {e}")

    def _load_config_from_excel(self, file_path):
        try:
            df_config = pd.read_excel(file_path, sheet_name='config')
        except Exception as e:
            print(f"No 'config' sheet found. Using defaults: threshold={self.threshold}, start_year={self.start_year}, end_year={self.end_year}")
            return

        if not {'Parameter', 'Value'}.issubset(df_config.columns):
            print("Config sheet missing 'Parameter' or 'Value' columns. Using defaults.")
            return

        def get_config_value(param_name, default_val, parse_func=float):
            row = df_config.loc[df_config['Parameter'].str.lower() == param_name.lower()]
            if not row.empty:
                val = row.iloc[0]['Value']
                try:
                    return parse_func(val)
                except ValueError:
                    print(f"Invalid value for '{param_name}'. Using default={default_val}")
                    return default_val
            return default_val

        self.threshold = get_config_value("Threshold", self.threshold, float)
        self.start_year = get_config_value("StartYear", self.start_year, int)
        self.end_year = get_config_value("EndYear", self.end_year, int)

        print(f"Config loaded -> threshold={self.threshold}, start_year={self.start_year}, end_year={self.end_year}")

    def _compute_sha256(self, file_path):
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def load_and_clean_data(self):
        """Load, clean, and store weather data for all locations.
           Also export combined raw and cleaned data, and compute coverage stats.
        """
        from .data_loading import get_weather_data

        for loc in self.locations:
            name = loc['name']
            lat = loc['lat']
            lon = loc['lon']
            try:
                # Fetch raw hourly data
                hourly_data, station, df_hash = get_weather_data(
                    lat, lon,
                    start_year=self.start_year,
                    end_year=self.end_year,
                    expected_hash=self.known_hashes.get(name)
                )
            except ValueError as e:
                print(f"Error fetching data for '{name}': {e}")
                continue

            # Store raw data in a separate dictionary
            self.dataframes_raw[name] = hourly_data.copy()

            if name not in self.known_hashes:
                self.known_hashes[name] = df_hash

            # Process data: convert wind speed units, ensure index, drop missing values
            if 'wspd' in hourly_data.columns:
                hourly_data['wspd'] = hourly_data['wspd'] / 3.6  # Convert km/h to m/s
            else:
                hourly_data['wspd'] = 0

            if hourly_data.index.name != 'time':
                hourly_data.index.name = 'time'

            hourly_data.dropna(subset=['wspd'], inplace=True)
            power_generation(hourly_data)  # Calculate power based on wind speed

            start_date = datetime(self.start_year, 1, 1)
            end_date = datetime(self.end_year, 12, 31, 23, 0)
            hourly_data = filter_data(hourly_data, start_date=start_date, end_date=end_date)

            # Save cleaned data
            self.dataframes[name] = hourly_data
            print(f"Data loaded/cleaned for {name}, hash={df_hash[:10]}...")

        # Export combined raw data
        self._export_combined_raw_data()

        # Export combined cleaned data
        self._export_combined_clean_data()

        # Compute and export coverage statistics
        self._export_coverage_stats()

    def _export_combined_raw_data(self):
        """Combine all raw data and export to a CSV file with a SHA256 hash."""
        combined_raw = pd.DataFrame()
        for name, df in self.dataframes_raw.items():
            df = df.copy()
            df['Location'] = name
            combined_raw = pd.concat([combined_raw, df], ignore_index=True)
        raw_csv_path = os.path.join(self.data_dir, 'raw_data_combined.csv')
        combined_raw.to_csv(raw_csv_path, index=False)
        raw_hash = self._compute_sha256(raw_csv_path)
        print(f"Raw data combined and saved to {raw_csv_path}, SHA256: {raw_hash}")

    def _export_combined_clean_data(self):
        """Combine all cleaned data and export to a CSV file with a SHA256 hash."""
        combined_clean = pd.DataFrame()
        for name, df in self.dataframes.items():
            df = df.copy()
            df['Location'] = name
            combined_clean = pd.concat([combined_clean, df], ignore_index=True)
        clean_csv_path = os.path.join(self.data_dir, 'cleaned_data_combined.csv')
        combined_clean.to_csv(clean_csv_path, index=False)
        clean_hash = self._compute_sha256(clean_csv_path)
        print(f"Cleaned data combined and saved to {clean_csv_path}, SHA256: {clean_hash}")

    def _export_coverage_stats(self):
        """
        Compute data coverage for each location and year by comparing the actual number of hourly records
        to the expected number. Export the results as a CSV.
        """
        import calendar
        results = []

        # For each location
        for loc in self.locations:
            name = loc['name']
            df = self.dataframes.get(name)
            if df is None:
                continue

            # Ensure the index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            # Loop over each year in the range
            for yr in range(self.start_year, self.end_year + 1):
                # Calculate expected hours in this year (account for leap years)
                days_in_year = 366 if calendar.isleap(yr) else 365
                expected_hours = days_in_year * 24  # all hours of the year
                df_year = df[df.index.year == yr]
                actual_hours = len(df_year)
                coverage_pct = (actual_hours / expected_hours) * 100 if expected_hours > 0 else 0

                if coverage_pct < 80:
                    print(f"[WARNING] Coverage <80% for {name} in {yr}: {coverage_pct:.2f}% ({actual_hours}/{expected_hours} hrs)")
                results.append({
                    'Location': name,
                    'Year': yr,
                    'ActualHours': actual_hours,
                    'ExpectedHours': expected_hours,
                    'CoveragePercent': coverage_pct
                })

        coverage_df = pd.DataFrame(results)
        coverage_path = os.path.join(self.data_dir, 'yearly_coverage_stats.csv')
        coverage_df.to_csv(coverage_path, index=False)
        print(f"Coverage statistics saved to {coverage_path}")

    def create_map(self):
        """Generate and save a Folium map of all locations."""
        from .visualization import create_map
        df_all = pd.DataFrame([
            {
                'Name': loc['name'],
                'Latitude': loc['lat'],
                'Longitude': loc['lon'],
                'State': loc['state']
            }
            for loc in self.locations
        ])
        map_output_path = os.path.join(self.reports_dir, 'map_with_labels.html')
        create_map(df_all, output_path=map_output_path)
        print(f"Map with labels -> {map_output_path}")

    def perform_production_analysis(self):
        """Analyze hours with zero output for each pair."""
        from itertools import combinations
        results = []
        for loc1, loc2 in combinations(self.locations, 2):
            n1, n2 = loc1['name'], loc2['name']
            df1 = self.dataframes.get(n1)
            df2 = self.dataframes.get(n2)
            if df1 is not None and df2 is not None:
                try:
                    zero_hours, pct_hours, total_hours = filter_and_compare_zero_output(
                        df1, df2, start_year=self.start_year, end_year=self.end_year
                    )
                    dist = calculate_distance(n1, n2, self.coordinates)
                    results.append({
                        'Pair': f"{n1} & {n2}",
                        'Hours with Zero Output': zero_hours,
                        'Percentage': f"{pct_hours:.2f}",
                        'Total Hours': total_hours,
                        'Distance (mi)': f"{dist:.2f}"
                    })
                except Exception as e:
                    print(f"Error in production analysis for {n1} & {n2}: {e}")

        if results:
            df_out = pd.DataFrame(results).sort_values(by='Hours with Zero Output', ascending=False)
            out_path = os.path.join(self.reports_dir, 'production_analysis_results.csv')
            df_out.to_csv(out_path, index=False)
            print(f"Production analysis complete -> {out_path}")

    def perform_correlation_analysis(self):
        """Compute correlation for each pair."""
        from itertools import combinations
        results = []
        for loc1, loc2 in combinations(self.locations, 2):
            n1, n2 = loc1['name'], loc2['name']
            df1 = self.dataframes.get(n1)
            df2 = self.dataframes.get(n2)
            if df1 is not None and df2 is not None:
                try:
                    corr_val = correlation_analysis(
                        df1, df2,
                        start_year=self.start_year,
                        end_year=self.end_year
                    )
                    dist = calculate_distance(n1, n2, self.coordinates)
                    results.append({
                        'Pair': f"{n1} & {n2}",
                        'Correlation': f"{corr_val:.4f}",
                        'Distance (mi)': f"{dist:.2f}"
                    })
                except Exception as e:
                    print(f"Error in correlation analysis for {n1} & {n2}: {e}")

        if results:
            df_out = pd.DataFrame(results).sort_values(by='Correlation', ascending=True)
            out_path = os.path.join(self.reports_dir, 'correlation_analysis_results.csv')
            df_out.to_csv(out_path, index=False)
            print(f"Correlation analysis complete -> {out_path}")

    def perform_absolute_difference_analysis(self, threshold=None):
        """Check hours with absolute difference above threshold for each pair."""
        if threshold is None:
            threshold = self.threshold
        from itertools import combinations
        results = []
        for loc1, loc2 in combinations(self.locations, 2):
            n1, n2 = loc1['name'], loc2['name']
            df1 = self.dataframes.get(n1)
            df2 = self.dataframes.get(n2)
            if df1 is not None and df2 is not None:
                try:
                    hrs_above, pct_hours, total_hours = filter_and_compare_abs_dif(
                        df1, df2,
                        start_year=self.start_year,
                        end_year=self.end_year,
                        threshold=threshold
                    )
                    dist = calculate_distance(n1, n2, self.coordinates)
                    results.append({
                        'Pair': f"{n1} & {n2}",
                        'Hours Above Threshold': hrs_above,
                        'Percentage': f"{pct_hours:.2f}",
                        'Total Hours': total_hours,
                        'Distance (mi)': f"{dist:.2f}"
                    })
                except Exception as e:
                    print(f"Error in absolute difference analysis for {n1} & {n2}: {e}")

        if results:
            df_out = pd.DataFrame(results).sort_values(by='Hours Above Threshold', ascending=False)
            out_path = os.path.join(self.reports_dir, 'absolute_difference_analysis_results.csv')
            df_out.to_csv(out_path, index=False)
            print(f"Absolute difference analysis complete (threshold={threshold}) -> {out_path}")

    def aggregate_pair_analysis(self):
        """
        Performs an aggregate production analysis on each pair of wind sites.
        For each pair, it computes aggregated production metrics and saves the results to a CSV.
        """
        from .analysis_aggregate import aggregate_pair_analysis as agg_pair_analysis
        import pandas as pd
        import os
        from itertools import combinations
        from .utils import calculate_distance

        results = []
        for loc1, loc2 in combinations(self.locations, 2):
            n1, n2 = loc1['name'], loc2['name']
            df1 = self.dataframes.get(n1)
            df2 = self.dataframes.get(n2)
            if df1 is not None and df2 is not None:
                metrics = agg_pair_analysis(df1, df2)
                dist = calculate_distance(n1, n2, self.coordinates)
                metrics['Pair'] = f"{n1} & {n2}"
                metrics['Distance (mi)'] = dist
                results.append(metrics)
        
        if results:
            df_results = pd.DataFrame(results)
            out_path = os.path.join(self.reports_dir, 'aggregate_pair_analysis_results.csv')
            df_results.to_csv(out_path, index=False)
            print(f"Aggregate pair analysis results saved to {out_path}")

    def generate_heatmaps(self):
        """
        Aggregate daily/weekly/monthly/yearly data, compute color scale,
        then produce 4 interactive HTML heatmaps.
        The yearly approach ensures each location is on the same trace for that year.
        """
        from .heatmaps import (
            aggregate_windspeed_data,
            calculate_min_max,
            create_interactive_heatmap
        )
        # Aggregate data
        df_daily, df_weekly, df_monthly, df_yearly = aggregate_windspeed_data(self.coordinates, self.dataframes)

        # Compute min/max for color scale
        wspd_stats = calculate_min_max(df_daily, df_weekly, df_monthly, df_yearly)

        # Daily heatmap
        daily_path = os.path.join(self.reports_dir, 'interactive_heatmap_daily.html')
        create_interactive_heatmap(
            df_combined=df_daily,
            frequency='d',
            min_wspd=wspd_stats['daily_min'],
            max_wspd=wspd_stats['daily_max'],
            output_path=daily_path
        )

        # Weekly heatmap
        weekly_path = os.path.join(self.reports_dir, 'interactive_heatmap_weekly.html')
        create_interactive_heatmap(
            df_combined=df_weekly,
            frequency='w',
            min_wspd=wspd_stats['weekly_min'],
            max_wspd=wspd_stats['weekly_max'],
            output_path=weekly_path
        )

        # Monthly heatmap
        monthly_path = os.path.join(self.reports_dir, 'interactive_heatmap_monthly.html')
        create_interactive_heatmap(
            df_combined=df_monthly,
            frequency='m',
            min_wspd=wspd_stats['monthly_min'],
            max_wspd=wspd_stats['monthly_max'],
            output_path=monthly_path
        )

        # Yearly heatmap
        yearly_path = os.path.join(self.reports_dir, 'interactive_heatmap_yearly.html')
        create_interactive_heatmap(
            df_combined=df_yearly,
            frequency='y',
            min_wspd=wspd_stats['yearly_min'],
            max_wspd=wspd_stats['yearly_max'],
            output_path=yearly_path
        )
        print("Dynamic heatmaps created (daily, weekly, monthly, yearly).")

    def run_all(self, threshold=None):
        """
        1) Load and clean data (with raw and clean export, and coverage stats)
        2) Create Folium map of locations
        3) Perform production, correlation, and absolute difference analyses
        4) Perform aggregate pair analysis
        5) Generate interactive heatmaps
        """
        self.load_and_clean_data()
        self.create_map()
        self.perform_production_analysis()
        self.perform_correlation_analysis()
        self.perform_absolute_difference_analysis(threshold=threshold)
        self.aggregate_pair_analysis()
        self.generate_heatmaps()
        print(f"All analyses complete. Reports saved to {self.reports_dir}")