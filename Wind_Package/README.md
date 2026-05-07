# Wind Geographic Diversity Analysis Package

Python package for analyzing geographic diversity effects in wind energy production using Meteostat weather data.

This package is part of the broader GeographicDiversity research repository authored by Dulf Vincent Genis during his time at the Ameren Innovation Center in Champaign, IL.

## Overview

This package analyzes **geographic diversity** in wind energy production. It fetches hourly wind speed data from Meteostat and compares production patterns across multiple geographic locations to quantify diversity benefits.

### What Does This Package Do?

When you have wind farms in different locations (e.g., Texas and Illinois), they often don't produce power at the same times due to weather pattern differences. This package:
1. **Fetches** wind speed data for multiple locations from Meteostat weather stations
2. **Calculates** power output using wind power curves
3. **Compares** production patterns between location pairs  
4. **Quantifies** diversity benefits (how much one site compensates when another has low output)
5. **Visualizes** results with interactive maps and heatmaps

### Key Benefit

Geographic diversity reduces variability: when one site has low production (no wind), other distant sites might still be windy, providing more stable combined output than any single site alone.

## Installation

### From Source

```bash
cd Wind_Package
pip install -e .
```

### Requirements

```bash
pip install -r requirements.txt
```

**Dependencies:**
- pandas
- numpy
- meteostat
- matplotlib
- folium
- plotly
- haversine
- fpdf
- seaborn
- requests
- openpyxl

## Configuration

### Excel File Setup

The package uses an Excel file (`locations.xlsx`) with two required sheets:

#### 1. locations Sheet

| Name | Latitude | Longitude | State |
|------|----------|-----------|-------|
| Chicago | 41.8781 | -87.6298 | IL |
| Seattle | 47.6062 | -122.3321 | WA |
| Minneapolis | 44.9778 | -93.2650 | MN |

**Requirements:**
- Name: Unique identifier for each location
- Latitude: Decimal degrees
- Longitude: Decimal degrees
- State: Two-letter state code

**Note:** Meteostat will automatically find the nearest weather station to the provided coordinates.

#### 2. config Sheet

| Parameter | Value | Description |
|-----------|-------|-------------|
| Threshold | 0.05 | Minimum power difference for diversity analysis (normalized) |
| StartYear | 2018 | First year of data to fetch |
| EndYear | 2023 | Last year of data to fetch |

**Notes:**
- Unlike solar, wind analysis runs 24/7 (no hourly filtering)
- Threshold represents normalized power difference
- Wind speed is converted from km/h to m/s automatically

## Usage

### Command Line

```bash
# Basic usage (uses locations.xlsx by default)
python scripts/run_all_analyses.py

# Or specify paths explicitly
cd Wind_Package
python scripts/run_all_analyses.py
```

### Python API

```python
from wind_geographic_diversity.runner import GeographicDiversityAnalyzer

# Initialize analyzer
analyzer = GeographicDiversityAnalyzer(
    locations_file='locations.xlsx',
    reports_dir='reports'
)

# Run complete analysis pipeline
analyzer.run_all()
```

### Individual Analysis Steps

```python
# 1. Load and clean weather data
analyzer.load_and_clean_data()

# 2. Create interactive map
analyzer.create_map()

# 3. Analyze zero-output hours
analyzer.perform_production_analysis()

# 4. Calculate correlation coefficients
analyzer.perform_correlation_analysis()

# 5. Quantify production differences
analyzer.perform_absolute_difference_analysis()

# 6. Aggregate pair statistics
analyzer.aggregate_pair_analysis()

# 7. Generate temporal heatmaps
analyzer.generate_heatmaps()
```

## Outputs

### Data Files (`data/` directory)

- **`raw_data_combined.csv`**: Original Meteostat data for all locations
  - Columns: time, temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres, tsun, coco, Location
  - SHA256 hash printed to console for verification

- **`cleaned_data_combined.csv`**: Processed data with power calculations
  - Columns: time (index), wspd, power, Location
  - Wind speed converted from km/h to m/s
  - Power calculated using wind power curve

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
   - Daily aggregated wind speed
   - Color scale: min to max daily wind speed
   - Interactive timeline slider

3. **`interactive_heatmap_weekly.html`**
   - Weekly aggregated wind speed
   - Smooths out daily variability

4. **`interactive_heatmap_monthly.html`**
   - Monthly aggregated wind speed
   - Shows seasonal patterns clearly

5. **`interactive_heatmap_yearly.html`**
   - Yearly aggregated wind speed
   - Long-term trends across locations

## Publishing Interactive Outputs to GitHub Pages

GitHub README cannot execute Plotly JavaScript inline. To share interactive results publicly:

1. Generate report HTML files in `Wind_Package/reports/`.
2. From repository root, run `python scripts/publish_interactive_assets.py`.
3. Push to `main` to trigger GitHub Pages deployment.

Published targets are copied into `docs/interactive/` with stable names for README links.

## Module Reference

### `runner.py`
Main `GeographicDiversityAnalyzer` class that orchestrates all analyses.

**Key Methods:**
- `load_and_clean_data()`: Fetch from Meteostat, clean, and export
- `run_all()`: Execute complete analysis pipeline

### `data_loading.py`
Handles Meteostat API interactions.

**Key Functions:**
- `get_weather_data()`: Download hourly wind data from nearest station
  - Automatically finds nearest weather station
  - Returns data, station info, and hash

### `data_cleaning.py`
Wind speed processing and power calculations.

**Key Functions:**
- `filter_data()`: Apply temporal filters
- `power_generation()`: Calculate power from wind speed using power curve

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
- `aggregate_windspeed_data()`: Create daily/weekly/monthly/yearly aggregations
- `create_interactive_heatmap()`: Generate Plotly-based HTML heatmaps

### `visualization.py`
Static plots and maps.

**Key Functions:**
- `create_map()`: Generate Folium map with location markers
- `plot_absolute_difference()`: Visualize production differences

### `utils.py`
Helper utilities.

**Key Functions:**
- `calculate_distance()`: Compute haversine distance between locations

## Wind Power Calculation

The package uses a simplified wind turbine power curve:

```python
def power_generation(df):
    """
    Calculate wind power based on wind speed.
    
    Typical turbine characteristics:
    - Cut-in speed: 3 m/s
    - Rated speed: 12 m/s
    - Cut-out speed: 25 m/s
    """
    # Power curve implementation (see data_cleaning.py)
    if wspd < 3.0:
        power = 0
    elif 3.0 <= wspd < 12.0:
        power = cubic_relationship(wspd)
    elif 12.0 <= wspd < 25.0:
        power = rated_power
    else:  # wspd >= 25.0
        power = 0  # turbine shutdown
```

**Notes:**
- Cut-in speed: Minimum wind speed for generation (3 m/s)
- Rated speed: Speed at which turbine reaches maximum output (12 m/s)
- Cut-out speed: Maximum safe operating speed (25 m/s)
- Power increases cubically between cut-in and rated speeds

## Data Quality

### Weather Station Selection

Meteostat automatically selects the nearest weather station:
- May not be at exact coordinates
- Station quality varies by location
- Some locations have better data coverage than others

### Coverage Checks

The package automatically checks data coverage:
- Calculates expected hours per year (8760 or 8784 for leap years)
- Warns if coverage drops below 80%
- Exports detailed coverage statistics

### Data Integrity

- SHA256 hashes computed for raw and cleaned data
- Can verify data hasn't changed between runs
- Use `expected_hash` parameter to enforce specific datasets

## Troubleshooting

### No Data Available

**Problem:** "No data found" or very low coverage

**Solution:**
1. Check if weather station exists near coordinates
2. Try different years (some stations have limited historical data)
3. Adjust location slightly to find better station
4. Use Meteostat website to verify station availability

### Incomplete Data

**Problem:** Coverage < 80% warnings

**Solution:**
- Normal for many weather stations
- Consider multiple stations or data imputation
- Document gaps in your analysis
- Focus on years/locations with good coverage

### Connection Issues

**Problem:** "Connection failed" or timeout errors

**Solution:**
- Check internet connection
- Meteostat API may be temporarily unavailable
- Retry after a few minutes
- Check Meteostat status page

### Memory Issues

**Problem:** Out of memory with many locations/years

**Solution:**
- Process fewer years at a time
- Reduce number of locations
- Increase system RAM
- Process locations individually

## Wind Speed Conversion

Meteostat provides wind speed in km/h, which is converted to m/s:

```python
wind_speed_ms = wind_speed_kmh / 3.6
```

**Example:**
- Wind speed: 36 km/h
- Converted: 36 / 3.6 = 10 m/s

## Advanced Usage

### Custom Power Curve

Modify `data_cleaning.py` to use your turbine's specific power curve:

```python
def power_generation(df):
    """Custom power curve for specific turbine model"""
    # Your power curve logic
    df['power'] = df['wspd'].apply(lambda x: custom_curve(x))
```

### Custom Analysis

```python
# Access processed data
analyzer.dataframes  # Dict: {location_name: DataFrame}

# Get location coordinates
analyzer.coordinates  # Dict: {location_name: (lat, lon)}

# Run custom analysis
from itertools import combinations
for loc1, loc2 in combinations(analyzer.locations, 2):
    df1 = analyzer.dataframes[loc1['name']]
    df2 = analyzer.dataframes[loc2['name']]
    # Your analysis here
```

### Custom Visualizations

```python
from wind_geographic_diversity.heatmaps import aggregate_windspeed_data

# Get aggregated data
df_daily, df_weekly, df_monthly, df_yearly = aggregate_windspeed_data(
    locations=analyzer.coordinates,
    dataframes=analyzer.dataframes
)

# Create custom plots
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
for location in df_monthly['location'].unique():
    data = df_monthly[df_monthly['location'] == location]
    plt.plot(data['date'], data['wspd'], label=location)
plt.legend()
plt.xlabel('Date')
plt.ylabel('Wind Speed (m/s)')
plt.title('Monthly Average Wind Speed by Location')
plt.show()
```

### Batch Processing

Process multiple location sets:

```python
location_files = ['midwest_sites.xlsx', 'coastal_sites.xlsx', 'mountain_sites.xlsx']

for file in location_files:
    analyzer = GeographicDiversityAnalyzer(
        locations_file=file,
        reports_dir=f'reports_{file.split(".")[0]}'
    )
    analyzer.run_all()
```

## Comparison with Solar

**Key Differences:**
- **Data Source:** Meteostat (weather) vs NSRDB (solar irradiance)
- **Temporal Coverage:** 24/7 vs daylight hours only
- **Power Calculation:** Wind power curve vs irradiance × efficiency
- **Variability:** Wind more intermittent than solar
- **Seasonality:** Different seasonal patterns

**Similarities:**
- Same analysis framework
- Parallel package structure
- Identical output formats
- Compatible with combined visualization notebook

## Contributing

To extend this package:

1. Add new analysis modules in `wind_geographic_diversity/`
2. Import and integrate into `runner.py`
3. Update documentation
4. Test with sample data

## Support

For questions or issues:
- Check the main repository README
- Review Meteostat documentation: https://dev.meteostat.net/
- Contact: Dulf Vincent Genis (e1818585@ameren.com)

## License

MIT License - see LICENSE file in root directory

