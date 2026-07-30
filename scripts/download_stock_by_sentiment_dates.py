#!/usr/bin/env python3
"""
Download Stock Price Data Based on Sentiment Date Ranges

For each ticker's sentiment CSV file, this script determines the earliest and
latest news date, then downloads the matching stock price history from
Yahoo Finance covering that exact date range.

Usage:
    python scripts/download_stock_by_sentiment_dates.py
    python scripts/download_stock_by_sentiment_dates.py --sentiment-dir data/processed/sentiment_by_ticker
    python scripts/download_stock_by_sentiment_dates.py --output-dir data/raw/prices --interval 1d
"""

import argparse
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default directories
DEFAULT_SENTIMENT_DIR = PROJECT_ROOT / "data" / "processed" / "sentiment_by_ticker"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "prices"


def get_sentiment_date_ranges(sentiment_dir: Path) -> dict[str, dict]:
    """
    Read each sentiment CSV and determine the ticker, first date, and last date.

    Args:
        sentiment_dir: Directory containing *_sentiment.csv files

    Returns:
        Dictionary mapping ticker -> {"start": Timestamp, "end": Timestamp, "file": name}
    """
    ranges: dict[str, dict] = {}

    for file in sorted(sentiment_dir.iterdir()):
        if file.suffix.lower() != ".csv":
            continue

        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"⚠️  Could not read {file.name}: {e}")
            continue

        if "Date" not in df.columns:
            print(f"⚠️  {file.name} has no 'Date' column, skipping")
            continue

        # Parse dates (handles both 'YYYY-MM-DD' and full timestamps with tz)
        dates = pd.to_datetime(df["Date"], utc=True, errors="coerce").dropna()
        if dates.empty:
            print(f"⚠️  {file.name} has no valid dates, skipping")
            continue

        # Normalize to date-only (drop time and timezone)
        first_date = dates.min().tz_convert(None).normalize()
        last_date = dates.max().tz_convert(None).normalize()

        # Determine ticker symbol
        if "Stock_symbol" in df.columns and df["Stock_symbol"].notna().any():
            symbol = str(df["Stock_symbol"].dropna().unique()[0])
        else:
            # Fall back to filename prefix (e.g. AAPL_sentiment.csv -> AAPL)
            symbol = file.stem.split("_")[0].upper()

        ranges[symbol] = {
            "start": first_date,
            "end": last_date,
            "file": file.name,
        }

        print(
            f"{symbol:<6} | {file.name:<28} | "
            f"{first_date.date()}  ->  {last_date.date()}"
        )

    return ranges


def download_for_ranges(
    ranges: dict[str, dict],
    output_dir: Path,
    interval: str = "1d",
) -> dict[str, pd.DataFrame]:
    """
    Download stock price data for each ticker over its sentiment date range.

    Args:
        ranges: Mapping of ticker -> {"start", "end", "file"}
        output_dir: Directory to save CSV files
        interval: Data interval ('1d', '1wk', '1mo')

    Returns:
        Dictionary mapping ticker -> price DataFrame
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("Downloading Stock Prices Based on Sentiment Date Ranges")
    print(f"{'='*70}")
    print(f"Output Dir: {output_dir}")
    print(f"Interval:   {interval}")
    print(f"{'='*70}\n")

    results: dict[str, pd.DataFrame] = {}
    successful, failed = [], []

    tickers = list(ranges.keys())
    for i, ticker in enumerate(tickers, 1):
        info = ranges[ticker]
        start_date = info["start"].strftime("%Y-%m-%d")
        # yfinance 'end' is exclusive, so add 1 day to include the last date
        end_date = (info["end"] + timedelta(days=1)).strftime("%Y-%m-%d")

        print(
            f"[{i}/{len(tickers)}] {ticker}  "
            f"({start_date} -> {info['end'].strftime('%Y-%m-%d')})...",
            end=" ",
        )

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date, interval=interval)

            if df.empty:
                print("⚠️  No data available")
                failed.append((ticker, "No data available"))
                continue

            df.reset_index(inplace=True)
            df.columns = [col.strip() for col in df.columns]

            columns_to_keep = ["Date", "Open", "High", "Low", "Close", "Volume"]
            available = [c for c in columns_to_keep if c in df.columns]
            df = df[available]

            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

            output_file = output_dir / f"{ticker}.csv"
            df.to_csv(output_file, index=False)

            rows = len(df)
            date_range = f"{df['Date'].iloc[0]} to {df['Date'].iloc[-1]}"
            print(f"✅ {rows} rows ({date_range})")

            results[ticker] = df
            successful.append(ticker)

        except Exception as e:
            print(f"❌ Error: {e}")
            failed.append((ticker, str(e)))

    # Summary
    print(f"\n{'='*70}")
    print("Download Summary")
    print(f"{'='*70}")
    print(f"Successful: {len(successful)}/{len(tickers)}")
    if successful:
        print(f"  Tickers: {', '.join(successful)}")
    if failed:
        print(f"\nFailed: {len(failed)}/{len(tickers)}")
        for ticker, reason in failed:
            print(f"  {ticker}: {reason}")
    print(f"\nFiles saved to: {output_dir}")
    print(f"{'='*70}")

    return results


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Download stock price data based on the news/sentiment date range "
            "found in each ticker's sentiment CSV file."
        )
    )
    parser.add_argument(
        "--sentiment-dir",
        type=str,
        default=str(DEFAULT_SENTIMENT_DIR),
        help=f"Directory with *_sentiment.csv files. Default: {DEFAULT_SENTIMENT_DIR}",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for price CSVs. Default: {DEFAULT_OUTPUT_DIR}",
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
    args = parse_arguments()

    sentiment_dir = Path(args.sentiment_dir)
    output_dir = Path(args.output_dir)

    if not sentiment_dir.exists():
        print(f"Error: sentiment directory not found: {sentiment_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"{'='*70}")
    print("Sentiment Date Ranges Per Ticker")
    print(f"{'='*70}")
    print(f"{'TICKER':<6} | {'FILE':<28} | START -> END")
    print(f"{'-'*70}")

    ranges = get_sentiment_date_ranges(sentiment_dir)

    if not ranges:
        print("\nNo valid sentiment files found. Nothing to download.")
        sys.exit(1)

    download_for_ranges(ranges, output_dir, interval=args.interval)


if __name__ == "__main__":
    main()