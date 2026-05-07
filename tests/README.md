# Tests

This directory contains the test suite for the Geographic Diversity Analysis framework.

## Test Structure

```
tests/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── unit/                        # Unit tests
│   ├── test_data_loading.py
│   ├── test_data_cleaning.py
│   ├── test_analysis_*.py
│   └── test_utils.py
├── integration/                 # Integration tests
│   ├── test_pipeline.py
│   └── test_runner.py
└── fixtures/                    # Test data
    └── sample_data.csv
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=solar_geographic_diversity --cov=wind_geographic_diversity

# Run specific test file
pytest tests/unit/test_data_loading.py

# Run with verbose output
pytest -v
```

## Writing Tests

### Unit Tests

Test individual functions and classes:

```python
# tests/unit/test_analysis_correlation.py
import pytest
import pandas as pd
from solar_geographic_diversity.analysis_correlation import correlation_analysis

def test_correlation_analysis():
    dates = pd.date_range('2020-01-01', '2020-12-31', freq='h')
    df1 = pd.DataFrame({'power': [1.0] * len(dates)}, index=dates)
    df2 = pd.DataFrame({'power': [0.8] * len(dates)}, index=dates)
    
    result = correlation_analysis(df1, df2)
    
    assert isinstance(result, float)
    assert -1 <= result <= 1
```

### Integration Tests

Test the full pipeline:

```python
# tests/integration/test_pipeline.py
import pytest
from solar_geographic_diversity.runner import GeographicDiversityAnalyzer

def test_full_analysis_pipeline():
    analyzer = GeographicDiversityAnalyzer(
        locations_file='tests/fixtures/sample_locations.xlsx',
        reports_dir='tests/output/reports'
    )
    
    analyzer.fetch_and_process_data()
    analyzer.correlation_analysis()
    
    # Verify outputs exist
    assert os.path.exists('tests/output/reports/correlation_analysis_results.csv')
```

## Test Data

Use the `fixtures/` directory for sample test data:
- Small datasets for fast testing
- Known expected results
- Edge cases and error conditions

## Coverage Goals

- **Target**: 80% code coverage
- **Critical**: 100% for data loading and analysis functions
- **Nice to have**: 100% for utility functions

## Continuous Integration

Tests should run automatically:
- On pull requests
- Before merging to main
- On commit (optional, for faster feedback)

## Notes

- Tests should be independent (no shared state)
- Use fixtures for common test data
- Mock external API calls in unit tests
- Use real data (cached) for integration tests
