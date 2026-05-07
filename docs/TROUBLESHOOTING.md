# Troubleshooting Guide

Common issues and solutions for the Geographic Diversity Analysis framework.

## Installation Issues

### "Module not found" or Import Errors

**Problem**: `ImportError: No module named 'solar_geographic_diversity'`

**Solutions**:
1. Make sure you've installed the package:
   ```bash
   cd Solar_Package
   pip install -e .
   ```

2. Check you're in the correct virtual environment:
   ```bash
   which python  # Should show venv path
   source venv/bin/activate  # Activate if needed
   ```

3. Verify installation:
   ```bash
   pip list | grep geographic
   ```

### Package Installation Fails

**Problem**: `pip install -e .` fails with dependency errors

**Solutions**:
1. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

2. Install dependencies first:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python version (requires 3.7+):
   ```bash
   python --version
   ```

## API Issues

### Solar: "API Key Invalid" or Authentication Errors

**Problem**: NSRDB API returns authentication errors

**Solutions**:
1. Verify API key in `locations_solar.xlsx`:
   - Check `API_Credentials` sheet
   - Ensure key is correct (no extra spaces)
   - Get new key at https://developer.nrel.gov/signup/

2. Check email format:
   - Must be valid email address
   - No typos or spaces

3. Verify API URL:
   - Default: `https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.csv`
   - Check if URL has changed

### Wind: "No Data Found" or Station Not Found

**Problem**: Meteostat can't find nearby weather station

**Solutions**:
1. Try different coordinates (nearby city):
   - Meteostat uses nearest available station
   - Try major city coordinates if rural area fails

2. Check location validity:
   - Latitude: -90 to 90
   - Longitude: -180 to 180

3. Try different time range:
   - Some stations have limited historical data
   - Reduce StartYear/EndYear range

### API Rate Limiting

**Problem**: "Too many requests" or slow data fetching

**Solutions**:
1. Reduce number of locations per run
2. Increase delays between requests (modify `data_loading.py`)
3. Fetch data in batches over multiple days
4. Use cached data when possible

## Data Issues

### Low Coverage Warnings (< 80%)

**Problem**: `yearly_coverage_stats.csv` shows coverage < 80%

**Causes**:
- Missing API data for certain years/locations
- Station outages or data gaps
- Time range extends beyond available data

**Solutions**:
1. Check `yearly_coverage_stats.csv` for specific gaps
2. Adjust StartYear/EndYear to match available data
3. Accept lower coverage if unavoidable (document in analysis)
4. Verify API responses are complete

### "Memory Error" or Out of Memory

**Problem**: Python runs out of memory during processing

**Solutions**:
1. Reduce time range:
   - Process fewer years at once
   - Use StartYear/EndYear to limit range

2. Reduce number of locations:
   - Process subsets of locations separately
   - Combine results manually if needed

3. Increase system memory (if possible)

4. Process in chunks (modify code to use chunked processing)

### SHA256 Hash Mismatch

**Problem**: Data integrity check fails

**Causes**:
- Data file was modified
- Different data fetched than expected

**Solutions**:
1. Re-fetch data if hash verification is critical
2. Update expected hash if data source changed
3. Verify Excel configuration matches previous runs

## Configuration Issues

### Excel File Format Errors

**Problem**: "Missing columns" or "Invalid format"

**Solutions**:
1. Verify sheet names are exact:
   - Solar: `API_Credentials`, `locations`, `config`
   - Wind: `locations`, `config`

2. Check column names:
   - `locations`: Name, Latitude, Longitude, State
   - `config`: Parameter, Value

3. Ensure no empty rows in header area
4. Save Excel file as `.xlsx` (not `.xls`)

### Configuration Values Not Applied

**Problem**: Changes to Excel config don't affect analysis

**Solutions**:
1. Close Excel file before running script
2. Verify parameter names match exactly (case-sensitive)
3. Check Value column has correct data types:
   - Numbers: numeric (not text)
   - Years: integers
   - Thresholds: floats

4. Restart Python process after config changes

## Analysis Issues

### No Results Generated

**Problem**: Analysis runs but no output files created

**Solutions**:
1. Check `reports_dir` path is valid
2. Verify write permissions in reports directory
3. Check for errors in console output
4. Ensure data was successfully loaded (`data/` directory has files)

### Unexpected Analysis Results

**Problem**: Results don't match expectations

**Solutions**:
1. Verify data quality:
   - Check `yearly_coverage_stats.csv`
   - Inspect `cleaned_data_combined.csv`
   - Look for outliers or missing data

2. Check configuration parameters:
   - Threshold values may be too high/low
   - Time filters may exclude important data
   - StartHour/EndHour may be filtering incorrectly

3. Review data cleaning:
   - Power conversion formulas
   - Filtering logic
   - Time zone handling

### Correlation Values Always Near 1.0

**Problem**: All site pairs show high correlation

**Possible Causes**:
- Sites are too close together
- Data hasn't been properly normalized
- Time range is too short
- Data source issue (same station used for multiple sites)

**Solutions**:
1. Verify locations are actually different
2. Check distance calculations
3. Increase time range
4. Verify data source independence

## Visualization Issues

### Maps Not Displaying

**Problem**: HTML map files won't open or are blank

**Solutions**:
1. Open with web browser (not Excel/other apps)
2. Check file size (should be > 0 bytes)
3. Verify Folium library is installed:
   ```bash
   pip install folium
   ```

4. Check browser console for JavaScript errors
5. Try different browser (Chrome, Firefox, Safari)

### Heatmaps Missing Data

**Problem**: Heatmaps show all zeros or missing values

**Solutions**:
1. Verify data was loaded correctly
2. Check time range overlaps with data
3. Verify aggregation function is correct
4. Check data cleaning didn't filter out all data

### Plotly Figures Not Interactive

**Problem**: HTML visualizations are static

**Solutions**:
1. Ensure Plotly is installed:
   ```bash
   pip install plotly
   ```

2. Open HTML in web browser (not in IDE)
3. Check browser supports JavaScript
4. Verify Plotly version is current

## Performance Issues

### Very Slow Data Fetching

**Problem**: Fetching takes hours/days

**Solutions**:
1. Reduce time range (fewer years)
2. Reduce number of locations
3. Check internet connection speed
4. Use cached data when possible (don't re-fetch)

### Analysis Takes Too Long

**Problem**: Analysis computation is slow

**Solutions**:
1. Reduce time range
2. Reduce number of location pairs
3. Check for inefficient code (loops instead of vectorization)
4. Consider parallel processing (future improvement)

## General Debugging Tips

### Enable Verbose Output

Add debug prints to understand what's happening:

```python
# In runner.py or scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Intermediate Files

Inspect generated files:
- `data/raw_data_combined.csv`: Raw API data
- `data/cleaned_data_combined.csv`: Processed data
- `data/yearly_coverage_stats.csv`: Data quality

### Verify Data Manually

Load and inspect data:
```python
import pandas as pd
df = pd.read_csv('data/cleaned_data_combined.csv')
print(df.head())
print(df.describe())
```

### Check Error Messages Carefully

- Read full error traceback
- Look for specific error type (ValueError, KeyError, etc.)
- Check line numbers in error message

### Test with Small Dataset

Use small test case first:
- 2-3 locations
- 1 year of data
- Verify pipeline works before scaling up

## Getting Help

### Before Asking for Help

1. **Check documentation**: README.md, QUICKSTART.md
2. **Review error messages**: Full traceback
3. **Verify configuration**: Excel files, parameters
4. **Test with minimal case**: Reduce scope to isolate issue

### Provide When Asking for Help

1. **Error messages**: Full traceback
2. **Configuration**: Relevant Excel config (redact API keys)
3. **System info**: Python version, OS, package versions
4. **Steps to reproduce**: What you did to cause the issue

### Contact

- **Email**: Dulf Vincent Genis (e1818585@ameren.com)
- **Documentation**: Check README files first
- **Issues**: Create detailed issue report with above information

## Common Error Messages

### "ValueError: Missing columns in Excel file"

→ Check Excel sheet names and column headers match exactly

### "KeyError: 'API_KEY'"

→ Verify `API_Credentials` sheet exists and has `API_KEY` column

### "FileNotFoundError: locations_solar.xlsx"

→ Check file path is correct, file exists, and is readable

### "ConnectionError" or "Timeout"

→ Check internet connection, API service status

### "MemoryError"

→ Reduce dataset size (fewer locations or years)

---

**Still having issues?** Review the error message carefully, check this guide, verify your configuration, and contact support with detailed information.
