#!/usr/bin/env python3
"""
Stock Price Data Downloader

Downloads historical stock price data from Yahoo Finance based on
specified start year and end year.

Usage:
    python scripts/download_stock_data.py --start-year 2021 --end-year 2025
    python scripts/download_stock_data.py --start-year 2020 --end-year 2024 --tickers AAPL MSFT GOOGL
    python scripts/download_stock_data.py --start-year 2021 --end-year 2025 --output-dir data/raw/prices
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yfinance as yf
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default stock tickers to download
DEFAULT_TICKERS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet (Google)
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "NVDA",   # NVIDIA
    "META",   # Meta Platforms (Facebook)
]

# Default output directory
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "prices"


def validate_year(year: int, param_name: str) -> None:
    """Validate that the year is reasonable."""
    current_year = datetime.now().year
    if year < 1970:
        raise ValueError(f"{param_name} must be 1970 or later. Got: {year}")
    if year > current_year + 1:
        raise ValueError(
            f"{param_name} cannot be more than 1 year in the future. Got: {year}"
        )


def download_stock_data(
    tickers: list[str],
    start_year: int,
    end_year: int,
    output_dir: str | Path,
    interval: str = "1d",
) -> dict[str, pd.DataFrame]:
    """
    Download stock price data for given tickers and date range.

    Args:
        tickers: List of stock ticker symbols (e.g., ['AAPL', 'MSFT'])
        start_year: Start year for data download (inclusive)
        end_year: End year for data download (inclusive, downloads through Dec 31)
        output_dir: Directory to save CSV files
        interval: Data interval ('1d', '1wk', '1mo')

    Returns:
        Dictionary mapping ticker symbols to their price DataFrames
    """
    # Validate inputs
    validate_year(start_year, "start_year")
    validate_year(end_year, "end_year")

    if start_year > end_year:
        raise ValueError(
            f"start_year ({start_year}) must be <= end_year ({end_year})"
        )

    # Create date range strings
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"Stock Price Data Downloader")
    print(f"{'='*60}")
    print(f"Tickers:    {', '.join(tickers)}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Interval:   {interval}")
    print(f"Output Dir: {output_path}")
    print(f"{'='*60}\n")

    results = {}
    successful = []
    failed = []

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Downloading {ticker}...", end=" ")

        try:
            # Download data using yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval=interval)

            if df.empty:
                print(f"⚠️  No data available")
                failed.append((ticker, "No data available"))
                continue

            # Reset index to make Date a column
            df.reset_index(inplace=True)

            # Clean up column names
            df.columns = [col.strip() for col in df.columns]

            # Select relevant columns
            columns_to_keep = ["Date", "Open", "High", "Low", "Close", "Volume"]
            available_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[available_columns]

            # Format date column
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

            # Save to CSV
            output_file = output_path / f"{ticker}.csv"
            df.to_csv(output_file, index=False)

            rows = len(df)
            date_range = f"{df['Date'].iloc[0]} to {df['Date'].iloc[-1]}"
            print(f"✅ {rows} rows ({date_range})")

            results[ticker] = df
            successful.append(ticker)

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed.append((ticker, str(e)))

    # Print summary
    print(f"\n{'='*60}")
    print(f"Download Summary")
    print(f"{'='*60}")
    print(f"Successful: {len(successful)}/{len(tickers)}")

    if successful:
        print(f"  Tickers: {', '.join(successful)}")

    if failed:
        print(f"\nFailed: {len(failed)}/{len(tickers)}")
        for ticker, reason in failed:
            print(f"  {ticker}: {reason}")

    print(f"\nFiles saved to: {output_path}")
    print(f"{'='*60}")

    return results


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download historical stock price data from Yahoo Finance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --start-year 2021 --end-year 2025
  %(prog)s --start-year 2020 --end-year 2024 --tickers AAPL MSFT GOOGL
  %(prog)s --start-year 2021 --end-year 2025 --interval 1wk
  %(prog)s --start-year 2021 --end-year 2025 --output-dir ./my_data
        """,
    )

    parser.add_argument(
        "--start-year",
        type=int,
        required=True,
        help="Start year for data download (inclusive). E.g., 2021",
    )

    parser.add_argument(
        "--end-year",
        type=int,
        required=True,
        help="End year for data download (inclusive, through Dec 31). E.g., 2025",
    )

    parser.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        help=f"Stock ticker symbols to download. Default: {' '.join(DEFAULT_TICKERS)}",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for CSV files. Default: {DEFAULT_OUTPUT_DIR}",
    )

    parser.add_argument(
        "--interval",
        type=str,
        choices=["1d", "1wk", "1mo"],
        default="1d",
        help="Data interval: 1d (daily), 1wk (weekly), 1mo (monthly). Default: 1d",
    )

    return parser.parse_args()


def main():
    """Main entry point for the stock data downloader."""
    args = parse_arguments()

    try:
        download_stock_data(
            tickers=args.tickers,
            start_year=args.start_year,
            end_year=args.end_year,
            output_dir=args.output_dir,
            interval=args.interval,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()