# Contributing to Geographic Diversity Analysis

Thanks for contributing. This repository is organized as parallel solar and wind analysis packages with shared research goals and output structure.

## Development Setup

```bash
git clone <repository-url>
cd GeographicDiversity
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd Solar_Package && pip install -e . && cd ..
cd Wind_Package && pip install -e . && cd ..
```

## Contribution Priorities

- New analysis metrics that improve geographic complementarity insights
- Reproducibility improvements (validation, provenance, deterministic outputs)
- Better visual communication for interactive maps and heatmaps
- Documentation clarity for external researchers and employers/reviewers

## What to Run / What You Should Produce

Contributions that touch analytics should run both package pipelines and verify expected outputs under each package `reports/` and `data/` directories. If you change visual output behavior, also run `python scripts/publish_interactive_assets.py` and confirm artifacts in `docs/interactive/`.

## Reproducibility and Data Provenance

- Keep generated data flow explicit: raw -> cleaned -> analysis outputs.
- Preserve `yearly_coverage_stats.csv` generation and warnings.
- Avoid undocumented schema changes to CSV outputs.
- If metrics or definitions change, update docs and changelog in the same PR.

## Coding Guidelines

- Follow PEP 8 and keep public functions documented.
- Prefer small, composable functions in `analysis_*.py` modules.
- Keep package interfaces backward compatible when possible.
- Add concise comments only for non-obvious statistical or transformation logic.

## Documentation Requirements

When behavior changes, update:

- `README.md` for public-facing story and usage
- `QUICKSTART.md` for first-run workflow
- Package readmes under `Solar_Package/` and `Wind_Package/`
- `CHANGELOG.md` for user-visible changes

## Pull Request Quality Checklist

- Scope is narrow and reviewable
- Local run completed for affected package(s)
- Output files and docs remain consistent
- No credentials or sensitive data committed
- If interactive assets changed, `docs/interactive/` is updated

## Need Help

- Architecture context: `ARCHITECTURE.md`
- Runtime issues: `docs/TROUBLESHOOTING.md`
- Contact: Dulf Vincent Genis (e1818585@ameren.com)
