# Changelog

All notable changes and organizational improvements to this project.

## [2026-05-06] - GitHub Launch Readiness

### Added

- Root README repositioned for portfolio/research storytelling, including Ameren Innovation Center context and explicit research draft highlight.
- GitHub Pages deployment workflow at `.github/workflows/deploy-pages.yml`.
- Interactive publishing script at `scripts/publish_interactive_assets.py` for stable Pages-bound artifact names.
- Interactive publishing documentation at `docs/interactive/README.md`.
- Shared publishing guidance in package readmes:
  - `Solar_Package/README.md`
  - `Wind_Package/README.md`

### Improved

- `QUICKSTART.md` now provides a concise runbook for setup, execution, interpretation, and Pages publishing.
- `CONTRIBUTING.md` now emphasizes reproducibility, output consistency, and review-ready contribution practices.

### GitHub Launch Checklist

- [x] Public-facing README narrative is concise and professional.
- [x] Research draft PDF is prominently linked in root docs.
- [x] Interactive Plotly/Folium outputs have a documented publish path.
- [x] GitHub Pages deployment workflow is configured.
- [x] Quickstart and contributing docs are aligned to the current repository flow.

## [2025-11-24] - Repository Organization and Documentation

### Added

#### Documentation
- **README.md** - Comprehensive root-level documentation covering:
  - Project overview and research questions
  - Complete project structure
  - Installation and quick start guides
  - Detailed analysis explanations
  - Data requirements and configuration
  - Extension guidelines for future researchers
  
- **QUICKSTART.md** - 10-minute getting started guide with:
  - Step-by-step installation
  - First analysis walkthrough
  - Results interpretation
  - Common customizations
  - Troubleshooting tips

- **CONTRIBUTING.md** - Developer guide covering:
  - How to add new analysis types
  - Code style guidelines
  - Testing procedures
  - Extension patterns (ML, optimization, new resources)
  - Performance optimization tips

- **Solar_Package/README.md** - Detailed solar-specific documentation
  - NSRDB API configuration
  - Excel file format specifications
  - Module reference
  - Power calculation formulas
  - Advanced usage examples

- **Wind_Package/README.md** - Detailed wind-specific documentation
  - Meteostat integration
  - Wind power curve explanation
  - Station selection details
  - Troubleshooting wind-specific issues

- **requirements.txt** - Root-level dependencies for combined analysis
  - Jupyter notebook support
  - Common visualization libraries
  - Optional solar/wind specific packages

- **.gitignore** - Comprehensive ignore rules for:
  - Python cache files (__pycache__)
  - Virtual environments
  - Jupyter checkpoints
  - macOS system files (.DS_Store)
  - Excel temp files (~$*.xlsx)
  - IDE configurations

### Removed

- **Temporary files:**
  - `Solar_Package/~$locations_solar.xlsx` - Excel lock file
  - `__pycache__/` directories - Python cache files
  - `.DS_Store` files - macOS system files

### Improved

- **Project Structure** - Clearly organized with:
  - Parallel Solar_Package and Wind_Package structure
  - Centralized documentation at root level
  - Separate data/ and reports/ directories per package
  - Combined visualization notebook for comparison

- **Reproducibility:**
  - SHA256 hash verification for data integrity
  - Comprehensive coverage statistics
  - Version-controlled configuration via Excel files
  - Clear dependency specifications

### Technical Details

#### Package Structure
```
Solar_Package/
  ├── setup.py (solar_geographic_diversity v0.1.0)
  ├── requirements.txt (11 dependencies)
  ├── locations_solar.xlsx (3 sheets: API_Credentials, locations, config)
  └── solar_geographic_diversity/ (10 modules)

Wind_Package/
  ├── setup.py (wind_geographic_diversity v0.1.0)
  ├── requirements.txt (12 dependencies)
  ├── locations.xlsx (2 sheets: locations, config)
  └── wind_geographic_diversity/ (10 modules)
```

#### Analysis Capabilities
Both packages provide:
1. **Production Diversity Analysis** - Zero-output hours
2. **Correlation Analysis** - Pearson coefficients
3. **Absolute Difference Analysis** - Significant production differences
4. **Aggregate Pair Analysis** - Combined production statistics
5. **Interactive Heatmaps** - Daily/weekly/monthly/yearly visualizations

#### Data Sources
- **Solar:** NREL NSRDB (requires API key)
- **Wind:** Meteostat (free access)

### Notes for Future Development

This organization establishes a solid foundation for:
- Adding new renewable resource types (hydro, tidal, etc.)
- Implementing optimization algorithms for portfolio design
- Integrating machine learning for forecasting
- Expanding to real-time monitoring dashboards
- Publishing research papers with reproducible results

### Author
Dulf Vincent Genis (e1818585@ameren.com)

### License
MIT License (see LICENSE file)

