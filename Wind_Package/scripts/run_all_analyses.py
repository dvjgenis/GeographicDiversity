# GeographicDiversity_Package/Wind_Package/scripts/run_all_analyses.py

import warnings
import argparse
import sys
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wind_geographic_diversity.runner import GeographicDiversityAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description="Run Wind Geographic Diversity Analyses using an Excel file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (uses default locations.xlsx)
  python scripts/run_all_analyses.py
  
  # Specify custom locations file
  python scripts/run_all_analyses.py --locations_file my_locations.xlsx
  
  # Override threshold from config
  python scripts/run_all_analyses.py --threshold 0.1

Note: Make sure your locations.xlsx file has:
  - locations sheet (with Name, Latitude, Longitude, State)
  - config sheet (with Threshold, StartYear, EndYear)

For detailed instructions, see README.md or QUICKSTART.md
        """
    )
    parser.add_argument('--locations_file', type=str, default='locations.xlsx',
                        help='Excel file with location data and config (default: locations.xlsx)')
    parser.add_argument('--reports_dir', type=str, default='reports',
                        help='Directory to save reports and visualizations (default: reports)')
    parser.add_argument('--threshold', type=float, default=None,
                        help='Threshold override for absolute difference analysis (overrides Excel config)')
    args = parser.parse_args()

    print("=" * 70)
    print("Wind Geographic Diversity Analysis")
    print("=" * 70)
    print(f"Locations file: {args.locations_file}")
    print(f"Output directory: {args.reports_dir}")
    if args.threshold is not None:
        print(f"Threshold override: {args.threshold}")
    print()
    
    try:
        analyzer = GeographicDiversityAnalyzer(
            locations_file=args.locations_file,
            reports_dir=args.reports_dir
        )
        
        print("Starting analysis pipeline...")
        print()
        
        # If threshold is not None, it overrides Excel config threshold
        analyzer.run_all(threshold=args.threshold)
        
        print()
        print("=" * 70)
        print("Analysis complete! Check the reports/ directory for results.")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: File not found - {e}")
        print("\n💡 Tip: Make sure you're running this script from the Wind_Package directory")
        print("   and that locations.xlsx exists in the current directory.")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ ERROR: Configuration error - {e}")
        print("\n💡 Tip: Check your Excel file has all required sheets and columns.")
        print("   See README.md for the correct Excel file format.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error - {e}")
        print("\n💡 Tip: Check the troubleshooting guide at docs/TROUBLESHOOTING.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
