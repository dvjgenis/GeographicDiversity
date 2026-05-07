# Geographic Diversity Analysis for Renewable Energy

Reproducible data science framework for quantifying how geographic dispersion improves renewable generation reliability across solar and wind portfolios.

**Project lead:** Dulf Vincent Genis  
**Project context:** Developed during my time at the Ameren Innovation Center in Champaign, IL (2025)

## Quick Navigation

[Research Paper](#research-output) • [Interactive Heatmaps](#interactive-heatmaps) • [Quick Start](#quick-run-flow) • [Data Science Highlights](#data-science-highlights) • [Citation](#citation)

**At a glance**
- Scope: Solar + wind geographic diversity analytics (hourly, multi-year)
- Methods: Complementarity, correlation, absolute difference, portfolio smoothing
- Output: Reproducible CSV metrics + interactive Plotly/Folium visualizations
- Research artifact: Draft paper linked below

## Research Output

The analysis in this repository produced a draft research paper:

- [DulfVincent_GeoDiv_ResearchPaper_Spring2025 (2).pdf](DulfVincent_GeoDiv_ResearchPaper_Spring2025%20(2).pdf)

The code, data transformations, and exported artifacts here are the reproducible backbone for that draft.

## Why This Work Matters

Renewables are variable in space and time. Geographic diversity can smooth output when sites are weakly correlated or complementary, improving planning confidence for grid operators and energy portfolio designers.

This project operationalizes that idea with:
- Pairwise temporal complementarity metrics
- Correlation and absolute-difference analytics
- Aggregate variability reduction analysis
- Interactive geospatial and temporal visualizations

## Analytical Depth

Core analytical techniques implemented in this repository:

- **Pairwise production complementarity**: Simultaneous zero-output percentages by site pair
- **Correlation structure analysis**: Pearson coefficients across multi-year hourly timeseries
- **Difference intensity analysis**: Thresholded absolute output divergence
- **Portfolio smoothing analysis**: Aggregate pair statistics and variance behavior
- **Spatiotemporal visual analytics**: Interactive maps and multi-granularity heatmaps
- **Reproducibility controls**: Coverage diagnostics and SHA256 checks for generated datasets

## Data Science Highlights

- Built paired-site analytical pipelines for two resource classes (solar and wind) using hourly multi-year datasets.
- Combined geospatial context with statistical diagnostics to translate raw weather/irradiance signals into decision-relevant reliability metrics.
- Structured outputs for both research interpretation (paper draft) and communication-ready artifacts (interactive maps, heatmaps, and summary tables).

## Interactive Visuals on GitHub

GitHub README cannot run embedded Plotly JavaScript directly.  
Interactive Plotly outputs are therefore published through **GitHub Pages** and linked from this README.

- Interactive artifacts live under `docs/interactive/`
- Deployment is handled by `.github/workflows/deploy-pages.yml`
- Publishing instructions: [`docs/interactive/README.md`](docs/interactive/README.md)

After Pages is enabled in repository settings, the interactive heatmap URLs follow this pattern:
- `https://<your-github-username>.github.io/GeographicDiversity/interactive/solar_heatmap_monthly.html`
- `https://<your-github-username>.github.io/GeographicDiversity/interactive/wind_heatmap_monthly.html`

## Interactive Heatmaps

Open the live Plotly heatmaps:

- [Solar Monthly Interactive Heatmap](https://dvjgenis.github.io/GeographicDiversity/interactive/solar_heatmap_monthly.html)
- [Wind Monthly Interactive Heatmap](https://dvjgenis.github.io/GeographicDiversity/interactive/wind_heatmap_monthly.html)

Optional direct path references:
- `interactive/solar_heatmap_monthly.html`
- `interactive/wind_heatmap_monthly.html`

For the full publishing workflow, see [`docs/interactive/README.md`](docs/interactive/README.md).

## Project Structure

```
GeographicDiversity/
├── README.md
├── QUICKSTART.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── ARCHITECTURE.md
├── requirements.txt
├── docs/
│   ├── TROUBLESHOOTING.md
│   └── interactive/                  # GitHub Pages-served interactive HTML artifacts
├── scripts/
│   └── publish_interactive_assets.py # Copies selected reports into docs/interactive
├── notebooks/
│   └── Combined_Visualizations.ipynb
├── Solar_Package/
│   ├── scripts/run_all_analyses.py
│   └── solar_geographic_diversity/...
└── Wind_Package/
    ├── scripts/run_all_analyses.py
    └── wind_geographic_diversity/...
```

## Quick Run Flow

1. Install dependencies (`requirements.txt`, then package-level installs as needed).
2. Configure location and parameter Excel files in each package.
3. Run package pipelines to generate CSV + HTML outputs in `reports/`.
4. Publish selected interactive HTML outputs to `docs/interactive/`.
5. Push to GitHub to auto-deploy Pages.

For the step-by-step starter workflow, see [`QUICKSTART.md`](QUICKSTART.md).

## What To Run and What You Get

Run `python scripts/run_all_analyses.py` in `Solar_Package/` to get NSRDB-based solar diversity outputs including `production_analysis_results.csv`, `correlation_analysis_results.csv`, `absolute_difference_analysis_results.csv`, `aggregate_pair_analysis_results.csv`, and interactive HTML maps/heatmaps.

Run `python scripts/run_all_analyses.py` in `Wind_Package/` to get the same report structure for Meteostat-driven wind analysis.

Run `python scripts/publish_interactive_assets.py` from the repository root to copy curated interactive HTML artifacts into `docs/interactive/` for GitHub Pages publishing.

## Data Sources and Provenance

- **Solar**: NREL NSRDB hourly irradiance data (API key required)
- **Wind**: Meteostat hourly weather station data
- **Provenance artifacts**:
  - Raw and cleaned exports in each package `data/` directory
  - Coverage diagnostics in `yearly_coverage_stats.csv`
  - Analysis outputs in each package `reports/` directory

## Key Documentation

- Root setup and launch flow: [`QUICKSTART.md`](QUICKSTART.md)
- Contribution and extension guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Package specifics:
  - [`Solar_Package/README.md`](Solar_Package/README.md)
  - [`Wind_Package/README.md`](Wind_Package/README.md)
- Troubleshooting: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

## Citation

```bibtex
@software{genis2025geographic,
  author = {Genis, Dulf Vincent},
  title = {Geographic Diversity Analysis for Renewable Energy},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/dvjgenis/GeographicDiversity}
}
```

## Contact

**Dulf Vincent Genis**  
Email: dvjgenis@gmail.com  
Project affiliation (2025): Ameren Innovation Center, Champaign, IL

## License

MIT License (see [LICENSE](LICENSE)).
