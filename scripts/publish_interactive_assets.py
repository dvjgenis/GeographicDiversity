#!/usr/bin/env python3
"""
Copy selected interactive HTML outputs into docs/interactive for GitHub Pages.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "interactive"

SOURCES = {
    "Solar_Package/reports/map_with_labels.html": "solar_map_with_labels.html",
    "Solar_Package/reports/interactive_heatmap_monthly.html": "solar_heatmap_monthly.html",
    "Wind_Package/reports/map_with_labels.html": "wind_map_with_labels.html",
    "Wind_Package/reports/interactive_heatmap_monthly.html": "wind_heatmap_monthly.html",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = []

    for source_rel, target_name in SOURCES.items():
        source = ROOT / source_rel
        target = OUTPUT_DIR / target_name
        if not source.exists():
            missing.append(source_rel)
            continue
        shutil.copy2(source, target)
        copied += 1
        print(f"Copied: {source_rel} -> docs/interactive/{target_name}")

    if missing:
        print("\nMissing source files:")
        for item in missing:
            print(f"- {item}")
        print(
            "\nRun the Solar/Wind analysis pipelines first, then rerun this script."
        )

    print(f"\nDone. Copied {copied} file(s) to docs/interactive/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
