# Solar Geographic Diversity Analysis Package

Python package for analyzing geographic diversity effects in solar energy production using NREL's NSRDB data.

This package is part of the broader GeographicDiversity research repository authored by Dulf Vincent Genis during his time at the Ameren Innovation Center in Champaign, IL.

## Overview

This package analyzes **geographic diversity** in solar energy production. It fetches hourly solar irradiance data from the National Solar Radiation Database (NSRDB) and compares production patterns across multiple geographic locations to quantify diversity benefits.

### What Does This Package Do?

When you have solar farms in different locations (e.g., California and Massachusetts), they often don't produce power at the same times due to weather differences. This package:
1. **Fetches** solar irradiance data for multiple locations from NREL's NSRDB database
2. **Calculates** power output for each location over time
3. **Compares** production patterns between location pairs
4. **Quantifies** diversity benefits (how much one site compensates when another has low output)
5. **Visualizes** results with interactive maps and heatmaps

### Key Benefit

Geographic diversity reduces variability: when one site has low production (cloudy day), other distant sites might still produce power, providing more stable combined output than any single site alone.

## Installation

### From Source

```bash
cd Solar_Package
pip install -e .
```

### Requirements

```bash
pip install -r requirements.txt
```

**Dependencies:**
- pandas
- numpy
- requests
- haversine
- matplotlib
- seaborn
- folium
- plotly
- fpdf
- openpyxl

## Configuration

### Excel File Setup

The package uses an Excel file (`locations_solar.xlsx`) with three required sheets:

#### 1. API_Credentials Sheet

| Parameter | Description | Example |
|-----------|-------------|---------|
| API_KEY | Your NREL API key | `your_api_key_here` |
| API_URL | NSRDB API endpoint | `https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.csv` |
| EMAIL | Your email address | `your.email@domain.com` |

**Get your API key:** [Sign up at NREL Developer Network](https://developer.nrel.gov/signup/)

#### 2. locations Sheet

| Name | Latitude | Longitude | State |
|------|----------|-----------|-------|
| Sacramento | 38.5816 | -121.4944 | CA |
| Boston | 42.3601 | -71.0589 | MA |
| Phoenix | 33.4484 | -112.0740 | AZ |

**Requirements:**
- Name: Unique identifier for each location
- Latitude: Decimal degrees
- Longitude: Decimal degrees
- State: Two-letter state code

#### 3. config Sheet

| Parameter | Value | Description |
|-----------|-------|-------------|
| Threshold | 0.00005 | Minimum power difference for diversity analysis (MW) |
| StartYear | 2018 | First year of data to fetch |
| EndYear | 2023 | Last year of data to fetch |
| StartHour | 7 | Start of daily analysis window (0-23) |
| EndHour | 19 | End of daily analysis window (0-23) |
| Area | 1.0 | Solar panel area in square meters |
| Efficiency | 0.21 | Solar panel efficiency (0-1) |

**Notes:**
- StartHour/EndHour filter data to daylight hours only
- Area and Efficiency convert irradiance to power output
- Threshold should be adjusted based on your system size

## Usage

### Command Line

```bash
# Basic usage
python scripts/run_all_analyses.py

# Specify custom files
python scripts/run_all_analyses.py \
    --locations_file my_locations.xlsx \
    --reports_dir my_reports
```

### Python API

```python
from solar_geographic_diversity.runner import GeographicDiversityAnalyzer

# Initialize analyzer
analyzer = GeographicDiversityAnalyzer(
    locations_file='locations_solar.xlsx',
    reports_dir='reports'
)

# Run complete analysis pipeline
analyzer.run_all()
```

### Individual Analysis Steps

```python
# 1. Fetch and process data from NSRDB
analyzer.fetch_and_process_data()

# 2. Create interactive map of locations
analyzer.create_location_map()

# 3. Analyze zero-output hours
analyzer.production_analysis()

# 4. Calculate correlation coefficients
analyzer.correlation_analysis()

# 5. Quantify production differences
analyzer.absolute_difference_analysis()

# 6. Aggregate pair statistics
analyzer.aggregate_pair_analysis()

# 7. Generate temporal heatmaps
analyzer.generate_heatmaps()
```

## Outputs

### Data Files (`data/` directory)

- **`raw_data_combined.csv`**: Original NSRDB data for all locations
  - Columns: Location, Year, Month, Day, Hour, Minute, DNI, DHI, GHI, etc.
  - SHA256 hash printed to console for verification

- **`cleaned_data_combined.csv`**: Processed data with power calculations
  - Columns: Datetime, DNI, GHI, Power_Output, Location
  - Filtered by configured time range and hours

- **`yearly_coverage_stats.csv`**: Data quality metrics
  - Columns: Location, Year, ActualHours, ExpectedHours, CoveragePercent
  - Warnings if coverage < 80%

### Reports (`reports/` directory)

#### CSV Analysis Results

1. **`production_analysis_results.csv`**
   - Pairs of locations
   - Hours with simultaneous zero output
   - Percentage of total hours
   - Geographic distance between sites

2. **`correlation_analysis_results.csv`**
   - Pairs of locations
   - Pearson correlation coefficient
   - Geographic distance

3. **`absolute_difference_analysis_results.csv`**
   - Pairs of locations
   - Hours above threshold difference
   - Percentage of total hours
   - Geographic distance

4. **`aggregate_pair_analysis_results.csv`**
   - Pairs of locations
   - Combined production statistics
   - Variance reduction metrics
   - Geographic distance

#### HTML Visualizations

1. **`map_with_labels.html`**
   - Interactive Folium map
   - Shows all location markers with labels
   - Click for location details

2. **`interactive_heatmap_daily.html`**
   - Daily aggregated solar production
   - Color scale: min to max daily production
   - Interactive timeline slider

3. **`interactive_heatmap_weekly.html`**
   - Weekly aggregated solar production
   - Smooths out daily variability

4. **`interactive_heatmap_monthly.html`**
   - Monthly aggregated solar production
   - Shows seasonal patterns clearly

5. **`interactive_heatmap_yearly.html`**
   - Yearly aggregated solar production
   - Long-term trends across locations

## Publishing Interactive Outputs to GitHub Pages

GitHub README cannot execute Plotly JavaScript inline. To share interactive results publicly:

1. Generate report HTML files in `Solar_Package/reports/`.
2. From repository root, run `python scripts/publish_interactive_assets.py`.
3. Push to `main` to trigger GitHub Pages deployment.

Published targets are copied into `docs/interactive/` with stable names for README links.

## Module Reference

### `runner.py`
Main `GeographicDiversityAnalyzer` class that orchestrates all analyses.

**Key Methods:**
- `fetch_and_process_data()`: Fetch from NSRDB, clean, and export
- `run_all()`: Execute complete analysis pipeline

### `data_loading.py`
Handles NSRDB API interactions.

**Key Functions:**
- `load_credentials()`: Read API credentials from Excel
- `load_locations()`: Read location data from Excel
- `load_config()`: Read configuration parameters from Excel
- `fetch_nsrdb_data()`: Download data from NSRDB API

### `data_cleaning.py`
Data preprocessing and power calculations.

**Key Functions:**
- `prepare_dataframe()`: Convert irradiance to power output
- `filter_dataframe()`: Apply temporal filters

### `analysis_production.py`
Zero-output analysis for geographic diversity.

**Key Functions:**
- `filter_and_compare_zero_output()`: Count hours with simultaneous zero production

### `analysis_correlation.py`
Statistical correlation analysis.

**Key Functions:**
- `correlation_analysis()`: Calculate Pearson correlation between site pairs

### `analysis_absolute_difference.py`
Production difference quantification.

**Key Functions:**
- `filter_and_compare_abs_dif()`: Count hours above difference threshold

### `analysis_aggregate.py`
Aggregate production metrics for site pairs.

**Key Functions:**
- `aggregate_pair_analysis()`: Calculate combined production statistics

### `heatmaps.py`
Interactive temporal visualizations.

**Key Functions:**
- `aggregate_solar_data()`: Create daily/weekly/monthly/yearly aggregations
- `create_interactive_heatmap()`: Generate Plotly-based HTML heatmaps

### `visualization.py`
Static plots and maps.

**Key Functions:**
- `create_map()`: Generate Folium map with location markers

### `utils.py`
Helper utilities.

**Key Functions:**
- `calculate_distance()`: Compute haversine distance between locations

## Power Calculation

The package converts solar irradiance to power output:

```python
Power (W) = DNI * Area (m²) * Efficiency
Power (MW) = Power (W) / 1,000,000
```

**Example:**
- DNI: 800 W/m²
- Area: 1.0 m²
- Efficiency: 0.21 (21%)
- Power: 800 × 1.0 × 0.21 = 168 W = 0.000168 MW

## Data Quality

### Coverage Checks

The package automatically checks data coverage:
- Calculates expected hours per year (accounting for leap years)
- Filters to configured daylight hours (StartHour to EndHour)
- Warns if coverage drops below 80%
- Exports detailed coverage statistics

### Data Integrity

- SHA256 hashes computed for raw and cleaned data
- Can verify data hasn't changed between runs
- Use `expected_hash` parameter to enforce specific datasets

## Troubleshooting

### API Key Issues

**Problem:** "API key invalid" or 403 errors

**Solution:**
1. Verify your API key at [NREL Developer Dashboard](https://developer.nrel.gov/)
2. Check API_Credentials sheet in Excel file
3. Ensure EMAIL matches your NREL account

### Missing Data

**Problem:** Coverage < 80% warnings

**Solution:**
- NSRDB may have gaps for certain years/locations
- Check NSRDB data availability for your coordinates
- Consider adjusting time range or locations

### Memory Issues

**Problem:** Out of memory with many locations/years

**Solution:**
- Process fewer years at a time
- Reduce number of locations
- Increase system RAM
- Process locations individually instead of run_all()

### Slow Performance

**Problem:** Analysis takes very long

**Solution:**
- API rate limits may slow data fetching
- Large datasets (many locations × many years) take time
- Use cached data (don't re-fetch if files exist)
- Run analyses in parallel if customizing code

## Advanced Usage

### Custom Analysis

```python
# Access processed data
analyzer.dataframes  # Dict: {location_name: DataFrame}

# Get location coordinates
analyzer.coord_dict  # Dict: {location_name: (lat, lon)}

# Run custom analysis on pairs
pairs = analyzer._generate_pairs()
for loc1, loc2, df1, df2 in pairs:
    # Your analysis here
    pass
```

### Modify Filtering

Edit `data_cleaning.py` to change filtering logic:

```python
def filter_dataframe(df, start_year, end_year, start_hour, end_hour):
    # Add custom filters
    df = df[df['some_column'] > threshold]
    return df
```

### Custom Visualizations

```python
from solar_geographic_diversity.heatmaps import aggregate_solar_data

# Get aggregated data
df_daily, df_weekly, df_monthly, df_yearly = aggregate_solar_data(
    locations=analyzer.coord_dict,
    dataframes=analyzer.dataframes
)

# Create custom plots with matplotlib/seaborn/plotly
import matplotlib.pyplot as plt
plt.plot(df_monthly['avg_power'])
plt.show()
```

## Contributing

To extend this package:

1. Add new analysis modules in `solar_geographic_diversity/`
2. Import and integrate into `runner.py`
3. Update documentation
4. Test with sample data

## Support

For questions or issues:
- Check the main repository README
- Review NSRDB documentation: https://nsrdb.nrel.gov/
- Contact: Dulf Vincent Genis (e1818585@ameren.com)

## License

MIT License - see LICENSE file in root directory

