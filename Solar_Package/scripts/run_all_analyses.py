# GeographicDiversity_Package/Solar_Package/scripts/run_all_analyses.py

import warnings
import argparse
import sys
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

# Ensure the parent directory (Solar_Package) is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solar_geographic_diversity.runner import GeographicDiversityAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description="Run Solar Geographic Diversity Analyses using an Excel file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (uses default locations_solar.xlsx)
  python scripts/run_all_analyses.py
  
  # Specify custom locations file
  python scripts/run_all_analyses.py --locations_file my_locations.xlsx
  
  # Specify custom output directory
  python scripts/run_all_analyses.py --reports_dir my_reports

Note: Make sure your locations_solar.xlsx file has:
  - API_Credentials sheet (with API_KEY, API_URL, EMAIL)
  - locations sheet (with Name, Latitude, Longitude, State)
  - config sheet (with analysis parameters)

For detailed instructions, see README.md or QUICKSTART.md
        """
    )
    parser.add_argument('--locations_file', type=str, default='locations_solar.xlsx',
                        help='Excel file with location data, API credentials, and config (default: locations_solar.xlsx)')
    parser.add_argument('--reports_dir', type=str, default='reports',
                        help='Directory to save output CSVs and HTML files (default: reports)')
   
    args = parser.parse_args()
   
    print("=" * 70)
    print("Solar Geographic Diversity Analysis")
    print("=" * 70)
    print(f"Locations file: {args.locations_file}")
    print(f"Output directory: {args.reports_dir}")
    print()
    
    try:
        # Initialize the analyzer with the Excel file
        analyzer = GeographicDiversityAnalyzer(
            locations_file=args.locations_file,
            reports_dir=args.reports_dir
        )
        
        print("Starting analysis pipeline...")
        print()
        
        # Run all analyses (parameters come from config sheet in the Excel file)
        analyzer.run_all()
        
        print()
        print("=" * 70)
        print("Analysis complete! Check the reports/ directory for results.")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: File not found - {e}")
        print("\n💡 Tip: Make sure you're running this script from the Solar_Package directory")
        print("   and that locations_solar.xlsx exists in the current directory.")
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