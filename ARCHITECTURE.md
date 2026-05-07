# Architecture Overview

This document describes the high-level architecture and design decisions for the Geographic Diversity Analysis framework.

## Repository Structure

```
GeographicDiversity/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── requirements.txt             # Root-level dependencies
├── .gitignore                   # Git ignore patterns
│
├── docs/                        # Additional documentation
│   └── (future: detailed guides)
│
├── notebooks/                   # Jupyter notebooks
│   └── Combined_Visualizations.ipynb  # Comparative analysis
│
├── tests/                       # Test suite (to be implemented)
│   └── (future: unit and integration tests)
│
├── Solar_Package/               # Solar energy analysis package
│   ├── README.md                # Solar-specific documentation
│   ├── setup.py                 # Package installation
│   ├── requirements.txt         # Solar dependencies
│   ├── locations_solar.xlsx     # Configuration file
│   ├── scripts/
│   │   └── run_all_analyses.py  # Main execution script
│   ├── solar_geographic_diversity/  # Core package
│   │   ├── __init__.py
│   │   ├── runner.py            # Main orchestrator class
│   │   ├── data_loading.py      # NSRDB API integration
│   │   ├── data_cleaning.py     # Data preprocessing
│   │   ├── analysis_*.py        # Analysis modules
│   │   ├── heatmaps.py          # Interactive visualizations
│   │   ├── visualization.py     # Static plots and maps
│   │   └── utils.py             # Helper functions
│   ├── data/                    # Generated data files
│   └── reports/                 # Analysis outputs
│
└── Wind_Package/                # Wind energy analysis package
    └── (parallel structure to Solar_Package)
```

## Design Philosophy

### 1. Parallel Package Structure

The repository uses parallel `Solar_Package` and `Wind_Package` structures to:
- **Separate concerns**: Each resource type has unique data sources and processing needs
- **Independent development**: Teams can work on solar/wind independently
- **Resource-specific optimization**: Tailor algorithms to each resource type
- **Clear boundaries**: Avoid coupling between different resource types

### 2. Configuration-Driven Analysis

All configuration is externalized to Excel files:
- **No code changes needed**: Users can modify analyses via Excel
- **Reproducibility**: Configuration files can be version-controlled
- **Accessibility**: Non-programmers can use the framework
- **Flexibility**: Easy to test different parameter combinations

### 3. Modular Analysis Pipeline

Each package follows a consistent analysis pipeline:

```
Data Loading → Data Cleaning → Analysis Modules → Visualization → Reporting
```

**Data Loading (`data_loading.py`)**
- Fetches raw data from APIs
- Handles authentication and API requests
- Returns standardized DataFrame format

**Data Cleaning (`data_cleaning.py`)**
- Converts raw data to power output
- Applies filters (time ranges, thresholds)
- Validates data quality
- Computes coverage statistics

**Analysis Modules (`analysis_*.py`)**
- Independent analysis functions
- Accept DataFrames as input
- Return structured results
- No side effects (pure functions)

**Visualization (`visualization.py`, `heatmaps.py`)**
- Static plots and maps
- Interactive HTML visualizations
- Time-series analysis views

**Reporting (`runner.py`)**
- Orchestrates the full pipeline
- Saves results to CSV/HTML
- Manages file I/O and organization

## Key Design Patterns

### 1. Factory Pattern (Runner Class)

The `GeographicDiversityAnalyzer` class acts as a factory that:
- Initializes from configuration files
- Manages data loading and caching
- Coordinates analysis execution
- Handles output generation

### 2. Strategy Pattern (Analysis Modules)

Each analysis type is implemented as a separate module:
- `analysis_production.py`: Zero-output analysis
- `analysis_correlation.py`: Correlation metrics
- `analysis_absolute_difference.py`: Difference quantification
- `analysis_aggregate.py`: Aggregate statistics

This allows easy addition of new analysis types without modifying existing code.

### 3. Template Method (Data Processing)

Both packages follow the same data processing template:
1. Load configuration
2. Fetch raw data (resource-specific)
3. Clean and process (resource-specific conversion)
4. Apply standard analyses (shared logic patterns)
5. Generate visualizations (shared visualization patterns)

### 4. Singleton Pattern (Configuration)

Configuration is loaded once per analyzer instance and reused across all analyses, ensuring consistency.

## Data Flow

### Solar Data Flow

```
Excel Config → Load Credentials → NSRDB API → Raw DataFrame
    ↓
Excel Config → Load Locations → Fetch for Each Location
    ↓
Raw DataFrame → Calculate Power (Area × Efficiency × Irradiance)
    ↓
Cleaned DataFrame → Apply Time Filters → Analysis Modules
    ↓
Results → CSV Files + HTML Visualizations
```

### Wind Data Flow

```
Excel Config → Load Locations → Meteostat API → Raw DataFrame
    ↓
Raw DataFrame → Convert Wind Speed → Calculate Power (Wind Curve)
    ↓
Cleaned DataFrame → Apply Time Filters → Analysis Modules
    ↓
Results → CSV Files + HTML Visualizations
```

## Module Responsibilities

### Core Modules

**`runner.py`**
- **Purpose**: Main orchestrator and entry point
- **Responsibilities**:
  - Load configuration from Excel
  - Coordinate data fetching and processing
  - Execute analysis pipeline
  - Save results and generate reports
  - Manage data integrity (SHA256 hashing)

**`data_loading.py`**
- **Purpose**: Fetch raw data from external APIs
- **Responsibilities**:
  - Handle API authentication
  - Make API requests with error handling
  - Parse API responses into DataFrames
  - Validate API responses

**`data_cleaning.py`**
- **Purpose**: Process raw data into analysis-ready format
- **Responsibilities**:
  - Convert raw measurements to power output
  - Apply filtering and validation
  - Compute data quality metrics
  - Handle missing data

**`utils.py`**
- **Purpose**: Shared utility functions
- **Responsibilities**:
  - Distance calculations (Haversine formula)
  - Helper functions for data manipulation
  - Common transformations

### Analysis Modules

Each `analysis_*.py` module follows this pattern:

```python
def analysis_function(df1, df2, start_year, end_year, **kwargs):
    """
    Perform analysis on two location DataFrames.
    
    Returns:
        dict or float: Analysis result
    """
    # Filter by year range
    # Align timestamps
    # Compute metric
    # Return result
```

**`analysis_production.py`**
- Measures when both sites have zero output simultaneously

**`analysis_correlation.py`**
- Computes Pearson correlation coefficients

**`analysis_absolute_difference.py`**
- Quantifies hours with significant production differences

**`analysis_aggregate.py`**
- Analyzes combined production statistics

### Visualization Modules

**`visualization.py`**
- Static matplotlib plots
- Interactive Folium maps
- Publication-quality figures

**`heatmaps.py`**
- Interactive Plotly heatmaps
- Temporal aggregation (daily/weekly/monthly/yearly)
- Time-series visualizations

## Configuration Management

### Excel File Structure

**Solar (`locations_solar.xlsx`)**
- `API_Credentials`: API key, URL, email
- `locations`: Name, Latitude, Longitude, State
- `config`: Analysis parameters (thresholds, time ranges, panel specs)

**Wind (`locations.xlsx`)**
- `locations`: Name, Latitude, Longitude, State
- `config`: Analysis parameters (thresholds, time ranges)

### Configuration Loading

Configuration is loaded using pandas `read_excel()`:
- Parameters are stored as key-value pairs
- Type conversion handled in loading functions
- Default values provided for missing parameters

## Error Handling and Validation

### Data Validation

- **API Response Validation**: Check for successful HTTP responses
- **Data Completeness**: Coverage statistics (warn if < 80%)
- **Data Range Validation**: Check for reasonable values
- **SHA256 Hashing**: Verify data integrity

### Error Handling Strategy

- **API Failures**: Log error, continue with other locations/years
- **Missing Data**: Warn user, continue analysis with available data
- **Invalid Configuration**: Raise clear error messages
- **File I/O Errors**: Create directories as needed, handle permissions

## Performance Considerations

### Data Fetching

- **API Rate Limits**: No explicit rate limiting (relies on API provider)
- **Caching**: Raw data saved to CSV files for reuse
- **Parallel Processing**: Not implemented (sequential fetching)

### Analysis Performance

- **Vectorization**: Uses pandas/numpy vectorized operations
- **Memory Management**: Loads all data into memory (scales with dataset size)
- **Computation**: O(n²) for pairwise analyses (n = number of locations)

### Optimization Opportunities

1. **Parallel Data Fetching**: Use `multiprocessing` for concurrent API calls
2. **Chunked Processing**: Process data in chunks for very large datasets
3. **Incremental Analysis**: Only recompute changed analyses
4. **Caching Intermediate Results**: Save intermediate computations

## Extension Points

### Adding New Analysis Types

1. Create new `analysis_newmetric.py` module
2. Implement function following standard signature
3. Add wrapper method to `runner.py`
4. Update documentation

### Adding New Resource Types

1. Create new `*_Package` directory
2. Copy structure from existing package
3. Implement resource-specific `data_loading.py` and `data_cleaning.py`
4. Reuse analysis modules (may need minor modifications)
5. Update `Combined_Visualizations.ipynb`

### Adding New Visualizations

1. Add function to `visualization.py` or `heatmaps.py`
2. Call from `runner.py` or script
3. Save output to reports directory

## Testing Strategy (Future)

### Unit Tests

- Test each analysis function with sample data
- Test configuration loading with various Excel formats
- Test utility functions (distance calculations, etc.)

### Integration Tests

- Test full pipeline with small datasets
- Test error handling with invalid inputs
- Test data quality checks

### Data Quality Tests

- Verify coverage statistics are correct
- Test SHA256 hash computation
- Validate data range checks

## Dependencies

### Core Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Static plotting
- **plotly**: Interactive visualizations
- **folium**: Interactive maps
- **openpyxl**: Excel file handling

### Resource-Specific Dependencies

- **Solar**: `requests` (for NSRDB API)
- **Wind**: `meteostat` (for weather data)

### Optional Dependencies

- **jupyter**: For notebook analysis
- **seaborn**: Enhanced plotting
- **haversine**: Distance calculations

## Future Architectural Improvements

### 1. Shared Common Package

Create a `common/` package with shared code:
- Analysis algorithms (many are identical)
- Visualization utilities
- Configuration loading
- Distance calculations

**Challenge**: Different data formats between solar/wind

### 2. Plugin Architecture

Implement plugin system for:
- New data sources
- Custom analysis types
- Visualization backends

### 3. Database Backend

Replace CSV files with database:
- Faster queries
- Better data integrity
- Easier data versioning

### 4. API Layer

Expose functionality via REST API:
- Web-based dashboard
- Integration with other tools
- Real-time analysis

### 5. Configuration Standardization

Move from Excel to YAML/JSON:
- Better version control
- Easier validation
- More flexible structure

## Code Quality Standards

### Style Guidelines

- **PEP 8**: Python style guide
- **Docstrings**: Google-style docstrings
- **Type Hints**: Optional but recommended
- **Line Length**: 100 characters max

### Documentation

- **Module docstrings**: Explain module purpose
- **Function docstrings**: Parameters, returns, examples
- **Inline comments**: For complex logic
- **README files**: Usage examples and guides

## Security Considerations

### API Keys

- **Storage**: In Excel files (not ideal, but practical)
- **Future**: Move to environment variables or secrets management
- **Access Control**: Excel files should not be committed with real keys

### Data Privacy

- **Location Data**: May contain sensitive site information
- **Recommendation**: Anonymize locations in public repositories

## Conclusion

The current architecture prioritizes:
1. **Ease of use**: Excel-based configuration
2. **Modularity**: Independent, reusable modules
3. **Extensibility**: Easy to add new analyses
4. **Clarity**: Clear separation of concerns

Future improvements should balance these priorities with:
- Code deduplication (shared common package)
- Performance optimization (parallel processing)
- Scalability (database backend)
- Maintainability (standardized testing)
