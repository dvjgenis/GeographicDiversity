# Interactive Visuals (GitHub Pages)

This directory is the publication target for interactive HTML visualizations.

GitHub renders Markdown in README but does not execute Plotly JavaScript inline.  
To keep interactive maps and heatmaps available publicly, this project publishes HTML artifacts through GitHub Pages.

## Publish Workflow

1. Generate report HTML files:
   - `Solar_Package/reports/map_with_labels.html`
   - `Solar_Package/reports/interactive_heatmap_monthly.html`
   - `Wind_Package/reports/map_with_labels.html`
   - `Wind_Package/reports/interactive_heatmap_monthly.html`
2. Copy selected artifacts into this folder:
   - `python scripts/publish_interactive_assets.py`
3. Commit and push to `main`.
4. GitHub Actions deploys `docs/` to Pages through `.github/workflows/deploy-pages.yml`.

## Expected Public URLs

After GitHub Pages is enabled, interactive files are available at:

- `https://<your-github-username>.github.io/GeographicDiversity/interactive/solar_map_with_labels.html`
- `https://<your-github-username>.github.io/GeographicDiversity/interactive/solar_heatmap_monthly.html`
- `https://<your-github-username>.github.io/GeographicDiversity/interactive/wind_map_with_labels.html`
- `https://<your-github-username>.github.io/GeographicDiversity/interactive/wind_heatmap_monthly.html`

## Preview Assets

Use `docs/interactive/previews/` for static screenshots referenced by the root README.
Keep image names stable for reusable links:

- `solar_map_preview.png`
- `solar_heatmap_preview.png`
- `wind_map_preview.png`
- `wind_heatmap_preview.png`
