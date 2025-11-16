#!/usr/bin/env python3
"""Command-line interface for Spatial Transcriptomics Data Miner."""

import argparse
import sys
from pathlib import Path
from typing import List, Dict

from ncbi_fetcher import NCBIFetcher
from tenx_fetcher import TenXFetcher
from htan_fetcher import HTANFetcher
from exporter import ExcelExporter
from config import (
    DEFAULT_NCBI_QUERY,
    DEFAULT_MAX_RESULTS,
    DEFAULT_OUTPUT_FILE
)


def print_banner():
    """Print application banner."""
    banner = """
╭──────────────────────────────────────────────────────╮
│  Spatial Transcriptomics Data Miner v1.0             │
│  Multi-platform ST dataset aggregator                │
╰──────────────────────────────────────────────────────╯
    """
    print(banner)


def fetch_ncbi_data(args) -> List[Dict]:
    """Fetch data from NCBI GEO."""
    if not args.include_ncbi:
        return []
    
    print("\n🧬 NCBI GEO")
    print("-" * 50)
    
    fetcher = NCBIFetcher(email=args.email)
    return fetcher.fetch_all(
        query=args.query,
        max_results=args.max_results
    )


def fetch_10x_data(args) -> List[Dict]:
    """Fetch data from 10x Genomics."""
    if not args.include_10x:
        return []
    
    print("\n🧠 10x Genomics")
    print("-" * 50)
    
    fetcher = TenXFetcher()
    return fetcher.fetch_datasets()


def fetch_htan_data(args) -> List[Dict]:
    """Fetch data from HTAN."""
    if not args.include_htan:
        return []
    
    print("\n🏛️  HTAN")
    print("-" * 50)
    
    fetcher = HTANFetcher()
    return fetcher.fetch_datasets()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spatial Transcriptomics Data Miner - Aggregate ST datasets from multiple platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch from all platforms (default)
  python -m st_miner.cli
  
  # Fetch only from NCBI with custom query
  python -m st_miner.cli --only-ncbi --query 'Visium AND brain'
  
  # Fetch from NCBI and 10x, limit to 500 results
  python -m st_miner.cli --include-ncbi --include-10x --max-results 500
  
  # Separate output by platform only
  python -m st_miner.cli --organize-by platform
  
  # Custom output file
  python -m st_miner.cli --output my_st_catalog.xlsx
        """
    )
    
    # Data source options
    source_group = parser.add_argument_group('Data Sources')
    source_group.add_argument(
        '--only-ncbi',
        action='store_true',
        help='Fetch only from NCBI GEO'
    )
    source_group.add_argument(
        '--only-10x',
        action='store_true',
        help='Fetch only from 10x Genomics'
    )
    source_group.add_argument(
        '--only-htan',
        action='store_true',
        help='Fetch only from HTAN'
    )
    source_group.add_argument(
        '--include-ncbi',
        action='store_true',
        help='Include NCBI GEO (use with other --include flags)'
    )
    source_group.add_argument(
        '--include-10x',
        action='store_true',
        help='Include 10x Genomics (use with other --include flags)'
    )
    source_group.add_argument(
        '--include-htan',
        action='store_true',
        help='Include HTAN (use with other --include flags)'
    )
    
    # NCBI specific options
    ncbi_group = parser.add_argument_group('NCBI Options')
    ncbi_group.add_argument(
        '--query',
        type=str,
        default=DEFAULT_NCBI_QUERY,
        help='NCBI search query (default: spatial transcriptomics OR Visium OR Slide-seq)'
    )
    ncbi_group.add_argument(
        '--max-results',
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f'Maximum number of NCBI results (default: {DEFAULT_MAX_RESULTS})'
    )
    ncbi_group.add_argument(
        '--email',
        type=str,
        help='Email for NCBI API (optional but recommended)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--output',
        '-o',
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=f'Output Excel file (default: {DEFAULT_OUTPUT_FILE})'
    )
    output_group.add_argument(
        '--organize-by',
        type=str,
        choices=['both', 'platform', 'organism', 'none'],
        default='both',
        help='How to organize output sheets (default: both)'
    )
    
    args = parser.parse_args()
    
    # Determine which sources to include
    # If no flags are set, fetch from all sources
    if not any([
        args.only_ncbi, args.only_10x, args.only_htan,
        args.include_ncbi, args.include_10x, args.include_htan
    ]):
        args.include_ncbi = True
        args.include_10x = True
        args.include_htan = True
    else:
        # Handle --only flags
        if args.only_ncbi:
            args.include_ncbi = True
            args.include_10x = False
            args.include_htan = False
        elif args.only_10x:
            args.include_ncbi = False
            args.include_10x = True
            args.include_htan = False
        elif args.only_htan:
            args.include_ncbi = False
            args.include_10x = False
            args.include_htan = True
    
    # Print banner
    print_banner()
    
    # Show configuration
    print("\n⚙️  Configuration:")
    print(f"  • Data Sources: ", end="")
    sources = []
    if args.include_ncbi:
        sources.append("NCBI GEO")
    if args.include_10x:
        sources.append("10x Genomics")
    if args.include_htan:
        sources.append("HTAN")
    print(", ".join(sources))
    
    if args.include_ncbi:
        print(f"  • NCBI Max Results: {args.max_results}")
    print(f"  • Organization: {args.organize_by}")
    print(f"  • Output File: {args.output}")
    
    # Fetch data from all sources
    all_datasets = []
    
    try:
        # NCBI
        ncbi_data = fetch_ncbi_data(args)
        all_datasets.extend(ncbi_data)
        
        # 10x Genomics
        tenx_data = fetch_10x_data(args)
        all_datasets.extend(tenx_data)
        
        # HTAN
        htan_data = fetch_htan_data(args)
        all_datasets.extend(htan_data)
        
        if not all_datasets:
            print("\n⚠️  No datasets found. Exiting.")
            return 1
        
        # Export to Excel
        exporter = ExcelExporter(args.output)
        exporter.export(all_datasets, separate_by=args.organize_by)
        
        print("\n✨ Success! Your spatial transcriptomics catalog is ready.")
        print(f"   File: {Path(args.output).absolute()}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⛔ Interrupted by user. Exiting.")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
