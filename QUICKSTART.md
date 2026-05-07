# Quick Start Guide

Use this guide to go from clone to reproducible results quickly.

## 1) Environment Setup

```bash
cd GeographicDiversity
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Install package dependencies:

```bash
cd Solar_Package && pip install -e . && cd ..
cd Wind_Package && pip install -e . && cd ..
```

## 2) Configure Inputs

- Solar config file: `Solar_Package/locations_solar.xlsx`
  - `API_Credentials` sheet (NREL key, email, URL)
  - `locations` sheet (Name, Latitude, Longitude, State)
  - `config` sheet (Threshold, years, hours, area, efficiency)
- Wind config file: `Wind_Package/locations.xlsx`
  - `locations` sheet
  - `config` sheet (Threshold and years)

## 3) Run Pipelines

Solar:

```bash
cd Solar_Package
python scripts/run_all_analyses.py
```

Wind:

```bash
cd Wind_Package
python scripts/run_all_analyses.py
```

## 4) Understand Outputs

Each package writes:

- `data/raw_data_combined.csv` and `data/cleaned_data_combined.csv`
- `data/yearly_coverage_stats.csv` for data quality and completeness
- `reports/production_analysis_results.csv` for simultaneous low-output behavior
- `reports/correlation_analysis_results.csv` for inter-site dependence
- `reports/absolute_difference_analysis_results.csv` for divergence intensity
- `reports/aggregate_pair_analysis_results.csv` for smoothing/portfolio behavior
- `reports/map_with_labels.html` and `reports/interactive_heatmap_*.html`

Interpretation shorthand:
- Lower simultaneous-zero percentage is better.
- Correlation closer to 0 (or negative) is better for diversity.
- Higher significant-difference percentage indicates stronger complementarity.

## 5) Publish Interactive Visuals to GitHub Pages

From repository root:

```bash
python scripts/publish_interactive_assets.py
```

This copies selected HTML artifacts into `docs/interactive/`.  
On push to `main`, `.github/workflows/deploy-pages.yml` deploys them to GitHub Pages.

## 6) Research and Presentation Assets

- Draft paper: `DulfVincent_GeoDiv_ResearchPaper_Spring2025 (2).pdf`
- Comparative notebook: `notebooks/Combined_Visualizations.ipynb`
- Root story + links: `README.md`

## Troubleshooting

- Solar API errors: verify NSRDB credentials in `API_Credentials`.
- Low wind data coverage: adjust coordinates or years.
- Missing report files: rerun pipeline and inspect package `reports/`.
- Additional issues: `docs/TROUBLESHOOTING.md`.

