"""
House Search Automation

A modular property search automation tool that supports multiple property websites.

Usage:
    python main.py grab-home [--site SITE]      # Grab homepage HTML
    python main.py grab-filters [--site SITE]   # Open filters modal and grab HTML
    python main.py search [--site SITE]         # Perform a property search
    python main.py parse [--site SITE]          # Parse search results to CSV
    python main.py parse --enrich               # Parse and add driving distances
    python main.py parse --enrich --html        # Parse, enrich, and generate HTML page
    python main.py list-sites                   # List available sites

Arguments:
    --site SITE    The property website to use (default: domain)
    --enrich       Calculate driving distances to key locations (requires GOOGLE_MAPS_API_KEY)
    --html         Generate a mobile-friendly HTML webpage with listings

Examples:
    python main.py search --site domain
    python main.py parse --site domain
    python main.py parse --site domain --enrich
    python main.py parse --site domain --enrich --html
    python main.py parse --site domain --input output/domain/search --output results.csv
    python main.py list-sites

Environment Variables:
    GOOGLE_MAPS_API_KEY    Required for --enrich flag to calculate driving distances
"""

import argparse
import logging
import sys

from config import SEARCH_CRITERIA
from engine import PropertySearchEngine
from parsers import get_parser, list_available_parsers
from sites import get_site_config, list_available_sites

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Property search automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # grab-home command
    grab_home = subparsers.add_parser("grab-home", help="Grab homepage HTML")
    grab_home.add_argument(
        "--site", 
        default="domain",
        help="Property website to use (default: domain)"
    )
    
    # grab-filters command
    grab_filters = subparsers.add_parser("grab-filters", help="Open filters modal and grab HTML")
    grab_filters.add_argument(
        "--site",
        default="domain", 
        help="Property website to use (default: domain)"
    )
    
    # search command
    search = subparsers.add_parser("search", help="Perform a property search")
    search.add_argument(
        "--site",
        default="domain",
        help="Property website to use (default: domain)"
    )
    
    # parse command
    parse = subparsers.add_parser("parse", help="Parse search results HTML and export to CSV")
    parse.add_argument(
        "--site",
        default="domain",
        help="Property website to parse results for (default: domain)"
    )
    parse.add_argument(
        "--input",
        default=None,
        help="Input directory containing HTML chunks (default: output/{site}/search)"
    )
    parse.add_argument(
        "--output",
        default=None,
        help="Output CSV file path (default: output/{site}/listings.csv)"
    )
    parse.add_argument(
        "--enrich",
        action="store_true",
        help="Calculate driving distances to key locations (requires GOOGLE_MAPS_API_KEY)"
    )
    parse.add_argument(
        "--html",
        action="store_true",
        help="Generate an HTML webpage displaying the listings"
    )
    
    # list-sites command
    subparsers.add_parser("list-sites", help="List available property websites")
    
    return parser


def main():
    """Main entry point with command routing."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "list-sites":
        sites = list_available_sites()
        print("Available sites:")
        for site in sites:
            print(f"  - {site}")
        return
    
    # Handle parse command separately (doesn't need site_config or engine)
    if args.command == "parse":
        try:
            parser_instance = get_parser(args.site)
            logger.info(f"Using parser for: {args.site}")
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)
        
        input_dir = args.input or f"output/{args.site}/search"
        output_file = args.output or f"output/{args.site}/listings.csv"
        
        logger.info(f"Parsing HTML from: {input_dir}")
        collection = parser_instance.parse_directory(input_dir)
        
        if len(collection) == 0:
            logger.warning("No listings found to export")
            sys.exit(0)
        
        # Enrich with distance data if requested
        if args.enrich:
            try:
                from enrichment import DistanceEnricher
                logger.info("Enriching listings with distance data...")
                enricher = DistanceEnricher()
                collection = enricher.enrich_collection(collection)
            except ValueError as e:
                logger.error(f"Distance enrichment failed: {e}")
                logger.error("Make sure GOOGLE_MAPS_API_KEY environment variable is set")
                sys.exit(1)
        
        output_path = collection.to_csv(output_file)
        logger.info(f"Exported {len(collection)} listings to: {output_path}")
        
        # Generate HTML if requested
        html_path = None
        if args.html:
            html_file = output_file.replace('.csv', '.html')
            html_path = collection.to_html(html_file)
            logger.info(f"Generated HTML page: {html_path}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Parse Results Summary")
        print(f"{'='*60}")
        print(f"Total listings: {len(collection)}")
        print(f"Unique suburbs: {len(collection.get_unique_suburbs())}")
        print(f"Suburbs: {', '.join(collection.get_unique_suburbs())}")
        
        if args.enrich:
            from config.locations import (
                KEY_LOCATIONS,
                MAX_TRANSIT_TIME_MINS,
                MAX_DRIVING_TIME_MINS,
                get_transit_locations,
                get_driving_locations,
            )
            print(f"\nTravel time limits applied:")
            print(f"  - Transit locations: max {MAX_TRANSIT_TIME_MINS} mins")
            print(f"  - Driving locations: max {MAX_DRIVING_TIME_MINS} mins")
            print(f"\nTransit locations (public transport):")
            for loc in get_transit_locations():
                print(f"  - {loc.name}")
            print(f"\nDriving locations:")
            for loc in get_driving_locations():
                print(f"  - {loc.name}")
        
        print(f"\nOutput files:")
        print(f"  CSV:  {output_path}")
        if html_path:
            print(f"  HTML: {html_path}")
        print(f"{'='*60}\n")
        return
    
    # Get the site configuration for other commands
    try:
        site_config = get_site_config(args.site)
        logger.info(f"Using site: {site_config.name}")
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Create the search engine
    engine = PropertySearchEngine(site_config, SEARCH_CRITERIA)
    
    # Execute the command
    if args.command == "grab-home":
        engine.grab_homepage_html(output_dir=f"output/{args.site}/home")
    elif args.command == "grab-filters":
        engine.grab_filters_html(output_dir=f"output/{args.site}/filters")
    elif args.command == "search":
        engine.perform_search(output_dir=f"output/{args.site}/search")


if __name__ == "__main__":
    main()
