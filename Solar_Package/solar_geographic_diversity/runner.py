# GeographicDiversity_Package/Solar_Package/solar_geographic_diversity/runner.py

import os
import hashlib
import calendar
import pandas as pd

from .data_loading import (
    load_credentials,
    load_locations,
    load_config,
    fetch_nsrdb_data
)
from .data_cleaning import prepare_dataframe, filter_dataframe
from .analysis_production import filter_and_compare_zero_output
from .analysis_correlation import correlation_analysis
from .analysis_absolute_difference import filter_and_compare_abs_dif
from .utils import calculate_distance
from .visualization import create_map

# Now import the aggregator & single-scale approach
from .heatmaps import (
    aggregate_solar_data,
    create_interactive_heatmap
)

class GeographicDiversityAnalyzer:
    def __init__(self, locations_file, reports_dir='reports'):
        """
        Initialize the analyzer with an Excel file containing:
         - 'API_Credentials' (API_KEY, API_URL, EMAIL)
         - 'locations' (Name, Latitude, Longitude, State)
         - 'config' (Threshold, StartYear, EndYear, StartHour, EndHour, Area, Efficiency, etc.)
        """
        self.locations_file = locations_file
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

        # data folder
        self.data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self.data_folder, exist_ok=True)

        # Load credentials
        self.api_key, self.api_url, self.email = load_credentials(self.locations_file, sheet_name="API_Credentials")

        # Load location data
        self.df_locations = load_locations(self.locations_file, sheet_name="locations")

        # Load config
        self.config = load_config(self.locations_file, sheet_name="config")

        self.dataframes_raw = {}
        self.dataframes = {}
        self.coord_dict = {}
        for _, row in self.df_locations.iterrows():
            name = row['Name']
            lat = row['Latitude']
            lon = row['Longitude']
            self.coord_dict[name] = (lat, lon)

    def fetch_and_process_data(self, expected_hash=None):
        """
        1) Fetch raw data
        2) Export raw_data_combined.csv (+ hash)
        3) Clean & filter => self.dataframes
        4) Export cleaned_data_combined.csv (+ hash)
        5) Coverage stats
        optional known-hash check
        """
        start_year = int(self.config.get("StartYear", 2018))
        end_year = int(self.config.get("EndYear", 2023))
        area = float(self.config.get("Area", 1.0))
        efficiency = float(self.config.get("Efficiency", 0.21))
        start_hour = int(self.config.get("StartHour", 7))
        end_hour = int(self.config.get("EndHour", 19))
        threshold = float(self.config.get("Threshold", 0.00005))
        years_to_fetch = range(start_year, end_year+1)

        # 1) Fetch raw
        for _, row in self.df_locations.iterrows():
            name = row['Name']
            lat = row['Latitude']
            lon = row['Longitude']
            df_loc_raw = pd.DataFrame()

            for year in years_to_fetch:
                try:
                    df_fetched = fetch_nsrdb_data(
                        lat=lat,
                        lon=lon,
                        year=year,
                        api_key=self.api_key,
                        api_url=self.api_url,
                        email=self.email
                    )
                    df_loc_raw = pd.concat([df_loc_raw, df_fetched], ignore_index=True)
                    print(f"[RAW] Fetched data for {name} - {year}")
                except Exception as e:
                    print(f"[ERROR] Could not fetch {name} - {year}: {e}")

            self.dataframes_raw[name] = df_loc_raw

        # 2) Export combined RAW
        combined_raw = pd.DataFrame()
        for nm, df_loc_raw in self.dataframes_raw.items():
            df_loc_raw['Location'] = nm
            combined_raw = pd.concat([combined_raw, df_loc_raw], ignore_index=True)

        raw_csv_path = os.path.join(self.data_folder, 'raw_data_combined.csv')
        combined_raw.to_csv(raw_csv_path, index=False)
        raw_hash = self._compute_sha256(raw_csv_path)
        print(f"raw_data_combined.csv -> {raw_csv_path}, SHA256: {raw_hash}")

        if expected_hash and raw_hash != expected_hash:
            raise ValueError(f"Raw data hash mismatch! Expected {expected_hash}, got {raw_hash}")

        # 3) Clean
        for nm, df_loc_raw in self.dataframes_raw.items():
            df_prepared = prepare_dataframe(df_loc_raw, area=area, efficiency=efficiency)
            df_filtered = filter_dataframe(df_prepared, start_year, end_year, start_hour, end_hour)
            self._validity_checks(df_filtered, location_name=nm)
            self.dataframes[nm] = df_filtered

        # 4) Export cleaned
        combined_cleaned = pd.DataFrame()
        for nm, df_cleaned in self.dataframes.items():
            df_cleaned['Location'] = nm
            combined_cleaned = pd.concat([combined_cleaned, df_cleaned], ignore_index=True)

        cleaned_csv_path = os.path.join(self.data_folder, 'cleaned_data_combined.csv')
        combined_cleaned.to_csv(cleaned_csv_path, index=False)
        cleaned_hash = self._compute_sha256(cleaned_csv_path)
        print(f"cleaned_data_combined.csv -> {cleaned_csv_path}, SHA256: {cleaned_hash}")

        # 5) Coverage stats
        coverage_df = self._compute_coverage_stats(combined_cleaned, start_year, end_year, start_hour, end_hour)
        coverage_path = os.path.join(self.data_folder, 'yearly_coverage_stats.csv')
        coverage_df.to_csv(coverage_path, index=False)
        print(f"yearly_coverage_stats.csv -> {coverage_path}")

    def _compute_sha256(self, file_path):
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _validity_checks(self, df, location_name):
        if 'DNI' in df.columns:
            invalid_count = (df['DNI'] > 1500).sum()
            if invalid_count > 0:
                print(f"[WARNING] {invalid_count} rows of DNI > 1500 in {location_name}.")

    def _compute_coverage_stats(self, df_combined, start_year, end_year, start_hour, end_hour):
        import calendar
        results = []

        def hours_in_year(yr, sh, eh):
            days_in_yr = 366 if calendar.isleap(yr) else 365
            daily_hrs = eh - sh
            return days_in_yr * daily_hrs

        for yr in range(start_year, end_year+1):
            exp_hrs = hours_in_year(yr, start_hour, end_hour)
            df_year = df_combined[df_combined['Datetime'].dt.year == yr]

            for loc in df_year['Location'].unique():
                sub = df_year[df_year['Location'] == loc]
                actual = len(sub)
                coverage_pct = (actual/exp_hrs)*100 if exp_hrs else 0
                if coverage_pct < 80:
                    print(f"[WARNING] Coverage <80% for {loc} in {yr}: "
                          f"{coverage_pct:.2f}% ({actual}/{exp_hrs} hrs)")

                results.append({
                    'Location': loc,
                    'Year': yr,
                    'ActualHours': actual,
                    'ExpectedHours': exp_hrs,
                    'CoveragePercent': coverage_pct
                })
        return pd.DataFrame(results)

    def create_location_map(self):
        map_path = os.path.join(self.reports_dir, 'map_with_labels.html')
        create_map(self.df_locations, output_path=map_path)
        print(f"Map with labels -> {map_path}")

    def _generate_pairs(self):
        loc_names = self.df_locations['Name'].tolist()
        state_map = dict(zip(self.df_locations['Name'], self.df_locations['State']))
        pairs = []
        for i in range(len(loc_names)):
            for j in range(i+1, len(loc_names)):
                n1 = loc_names[i]
                n2 = loc_names[j]
                if state_map[n1] != state_map[n2]:
                    df1 = self.dataframes.get(n1)
                    df2 = self.dataframes.get(n2)
                    if df1 is not None and df2 is not None:
                        pairs.append((n1, n2, df1, df2))
        return pairs

    def production_analysis(self):
        s_yr = int(self.config.get("StartYear", 2018))
        e_yr = int(self.config.get("EndYear", 2023))

        pairs = self._generate_pairs()
        results = []
        for l1, l2, df1, df2 in pairs:
            z_hrs, pct_z, tot_hrs = filter_and_compare_zero_output(df1, df2, start_year=s_yr, end_year=e_yr)
            dist = calculate_distance(l1, l2, self.coord_dict)
            results.append({
                'Pair': f"{l1} & {l2}",
                'Hours With Zero Output': z_hrs,
                'Percentage': pct_z,
                'Total Hours': tot_hrs,
                'Distance (mi)': dist
            })
        df_out = pd.DataFrame(results).sort_values('Hours With Zero Output', ascending=False)
        out_path = os.path.join(self.reports_dir, 'production_analysis_results.csv')
        df_out.to_csv(out_path, index=False)
        print(f"Production analysis -> {out_path}")

    def correlation_analysis(self):
        s_yr = int(self.config.get("StartYear", 2018))
        e_yr = int(self.config.get("EndYear", 2023))

        pairs = self._generate_pairs()
        results = []
        for l1, l2, df1, df2 in pairs:
            c_val = correlation_analysis(df1, df2, start_year=s_yr, end_year=e_yr)
            dist = calculate_distance(l1, l2, self.coord_dict)
            results.append({
                'Pair': f"{l1} & {l2}",
                'Correlation': c_val,
                'Distance (mi)': dist
            })
        df_corr = pd.DataFrame(results).sort_values('Correlation', ascending=True)
        out_path = os.path.join(self.reports_dir, 'correlation_analysis_results.csv')
        df_corr.to_csv(out_path, index=False)
        print(f"Correlation analysis -> {out_path}")

    def absolute_difference_analysis(self):
        s_yr = int(self.config.get("StartYear", 2018))
        e_yr = int(self.config.get("EndYear", 2023))
        threshold = float(self.config.get("Threshold", 0.00005))

        pairs = self._generate_pairs()
        results = []
        for l1, l2, df1, df2 in pairs:
            hrs_above, perc_above, tot_hrs = filter_and_compare_abs_dif(df1, df2, start_year=s_yr, end_year=e_yr, threshold=threshold)
            dist = calculate_distance(l1, l2, self.coord_dict)
            results.append({
                'Pair': f"{l1} & {l2}",
                'Hours Above Threshold': hrs_above,
                'Percentage': perc_above,
                'Total Hours': tot_hrs,
                'Distance (mi)': dist
            })
        df_abs = pd.DataFrame(results).sort_values('Hours Above Threshold', ascending=False)
        out_path = os.path.join(self.reports_dir, 'absolute_difference_analysis_results.csv')
        df_abs.to_csv(out_path, index=False)
        print(f"Absolute difference analysis -> {out_path}")

    def aggregate_pair_analysis(self):
        """
        Performs an aggregate production analysis on each pair of sites.
        For each pair, it computes aggregated production metrics and saves the results to a CSV.
        """
        from .analysis_aggregate import aggregate_pair_analysis as agg_pair_analysis
        results = []
        pairs = self._generate_pairs()
        for site1, site2, df1, df2 in pairs:
            metrics = agg_pair_analysis(df1, df2)
            dist = calculate_distance(site1, site2, self.coord_dict)
            metrics['Pair'] = f"{site1} & {site2}"
            metrics['Distance (mi)'] = dist
            results.append(metrics)
        df_results = pd.DataFrame(results)
        out_path = os.path.join(self.reports_dir, 'aggregate_pair_analysis_results.csv')
        df_results.to_csv(out_path, index=False)
        print(f"Aggregate pair analysis results saved to {out_path}")

    def generate_heatmaps(self):
        """
        Aggregates daily/weekly/monthly/yearly, finds a single cmin/cmax for each category,
        and produces 4 interactive HTML maps that share that scale across all years.
        """
        if not self.dataframes:
            print("[Heatmaps] No data found. Run fetch_and_process_data first.")
            return

        from .heatmaps import (
            aggregate_solar_data,
            calculate_min_max_by_category,
            create_interactive_heatmap
        )

        # 1) Aggregate
        df_daily, df_weekly, df_monthly, df_yearly = aggregate_solar_data(
            locations=self.coord_dict,
            dataframes=self.dataframes
        )

        # 2) Compute min/max for each category across all years
        cat_stats = calculate_min_max_by_category(
            df_daily, df_weekly, df_monthly, df_yearly
        )

        # 3) Create daily map
        d_html = os.path.join(self.reports_dir, 'interactive_heatmap_daily.html')
        create_interactive_heatmap(
            df_combined=df_daily,
            frequency='D',
            cmin=cat_stats['daily_min'],
            cmax=cat_stats['daily_max'],
            output_path=d_html,
            title_prefix="Solar Irradiance"
        )

        # 4) Weekly
        w_html = os.path.join(self.reports_dir, 'interactive_heatmap_weekly.html')
        create_interactive_heatmap(
            df_combined=df_weekly,
            frequency='W',
            cmin=cat_stats['weekly_min'],
            cmax=cat_stats['weekly_max'],
            output_path=w_html,
            title_prefix="Solar Irradiance"
        )

        # 5) Monthly
        m_html = os.path.join(self.reports_dir, 'interactive_heatmap_monthly.html')
        create_interactive_heatmap(
            df_combined=df_monthly,
            frequency='M',
            cmin=cat_stats['monthly_min'],
            cmax=cat_stats['monthly_max'],
            output_path=m_html,
            title_prefix="Solar Irradiance"
        )

        # 6) Yearly
        y_html = os.path.join(self.reports_dir, 'interactive_heatmap_yearly.html')
        create_interactive_heatmap(
            df_combined=df_yearly,
            frequency='Y',
            cmin=cat_stats['yearly_min'],
            cmax=cat_stats['yearly_max'],
            output_path=y_html,
            title_prefix="Solar Irradiance"
        )

        print("[Heatmaps] Daily/Weekly/Monthly/Yearly interactive maps created with single scale per category.")

    def run_all(self):
        """
        1) fetch_and_process_data
        2) create_location_map
        3) production, correlation, absolute diff
        4) generate_heatmaps
        """
        self.fetch_and_process_data()
        self.create_location_map()
        self.production_analysis()
        self.correlation_analysis()
        self.absolute_difference_analysis()
        self.aggregate_pair_analysis()
        self.generate_heatmaps()
        print("All analyses and visualizations have been completed.")