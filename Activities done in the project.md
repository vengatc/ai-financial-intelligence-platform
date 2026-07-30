# Activities Done in the Project

**Project:** AI Financial Intelligence Platform
**Purpose of this document:** A factual log of the *high-level* work actually completed on the capstone project so far, framed for the **MIT Applied Data Science / AI & ML Certificate Program** capstone presentation. Each entry lists only work that has genuinely been done and the part of the MIT curriculum it maps to.

> Focus is on the data-science learning journey (not code structuring, packaging, or repo management). Only completed work is recorded. Entries are appended as new program-relevant work is finished.

---

## Capstone Project Overview

**Goal:** Build a platform that combines historical stock price data and financial news for the "Magnificent 7" mega-cap tech companies (AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META).

**Data used:**
1. Daily OHLCV (Open, High, Low, Close, Volume) stock prices.
2. Financial news articles (with pre-existing machine-generated summaries in the source dataset).

---

## Completed Activities Mapped to MIT AI/ML Learning

### 1. Data Acquisition

| Activity | What Was Actually Done | MIT Learning Applied |
|----------|------------------------|----------------------|
| Automated price data download | Built a command-line downloader (`scripts/download_stock_data.py`) that pulls historical OHLCV prices from Yahoo Finance via `yfinance`, with configurable years, tickers, and interval, and saves per-ticker CSVs. | Data Collection & Acquisition – programmatic sourcing of real-world data. |
| Obtained news dataset | Loaded an existing financial news CSV dataset into the project (`data/raw/news/`). | Working with an external / unstructured-text dataset. |
| Sentiment-date-aligned price download | Built a second downloader (`scripts/download_stock_by_sentiment_dates.py`) that reads each per-ticker sentiment CSV (`data/processed/sentiment_by_ticker/`), robustly parses the `Date` column (handling both `YYYY-MM-DD` and timezone-aware timestamps), derives each stock's actual news start/end dates, and downloads the matching OHLCV price window from Yahoo Finance so price and news coverage line up per ticker (e.g. NVDA 2011-03-03 → 2020-06-10). | Data Collection & Acquisition – aligning two data sources over a common time window to enable later feature fusion. |

### 2. Data Loading & Cleaning

| Activity | What Was Actually Done | MIT Learning Applied |
|----------|------------------------|----------------------|
| Multi-format CSV loading | Wrote a loader that handles both standard CSVs and `yfinance` multi-header CSVs, converting them to a consistent schema (notebook 01). | Data Wrangling – normalizing inconsistent raw file formats. |
| Datetime parsing & type conversion | Parsed `Date` columns to `datetime` (UTC for news) and coerced price columns to numeric. | Data type handling / cleaning. |
| Missing-value check | Counted missing values per ticker and computed % missing per dataset (notebooks 01 & 02). | Data Quality Assessment. |
| Duplicate-date check | Checked each ticker's series for duplicate dates (notebook 01). | Data integrity / de-duplication. |
| Fixed mixed-type text columns | Resolved `.str` accessor errors in notebook 02 by casting float/NaN columns to string before string operations and excluding `'N/A'`/`'nan'` placeholders. | Practical data cleaning of dirty, mixed-type columns. |

### 3. Exploratory Data Analysis (EDA)

| Activity | What Was Actually Done | MIT Learning Applied |
|----------|------------------------|----------------------|
| Descriptive statistics | Generated per-ticker summary stats (min/max/mean Close, average volume) and `describe()` output (notebook 01). | Descriptive Statistics. |
| Cross-stock correlation | Combined all tickers' Close prices into one DataFrame and computed the correlation matrix (notebook 01). | Correlation analysis. |
| Performance comparison | Computed total return (%) for each stock over the observed period (notebook 01). | Derived metrics. |
| Daily returns & volatility | Calculated daily returns (`pct_change`) and annualized volatility (σ × √252) per stock (notebook 01). | Probability & Statistics – variance / standard deviation / risk. |
| News data profiling | Counted total articles, unique stock symbols, unique publishers, top symbols and publishers, and the availability of article text and each summary column (notebook 02). | Exploratory analysis of an unstructured dataset – distributions and completeness. |
| Filtered news to target tickers | Filtered the news dataset to the 7 target tickers, examined per-ticker and per-year article counts, and saved the filtered subset (notebook 02). | Data subsetting / filtering. |
| Grouped headlines by ticker and date | Aggregated all article headlines for each (stock, day) into a single record (list of headlines + count), normalized dates to day-level, and saved the result to `Headlines_by_ticker_date.csv` (notebook 02). | Data aggregation with `groupby` – preparing news for alignment with daily price data. |

### 4. Sentiment Analysis (NLP)

| Activity | What Was Actually Done | MIT Learning Applied |
|----------|------------------------|----------------------|
| FinBERT news sentiment scoring | Applied the pretrained finance-domain transformer `ProsusAI/finbert` (HuggingFace `transformers` `sentiment-analysis` pipeline) to each filtered news headline (`Article_title`), generating a sentiment label (positive / negative / neutral) and a confidence score. Ran the inference on **Google Colab GPU** because the local GPU was insufficient; handled missing titles and saved the enriched dataset to `data/processed/Filtered_external_sentiment.csv` (notebook `SentimentAnalysis.ipynb`). | Natural Language Processing / Deep Learning – transformer (BERT) text classification and pretrained-model inference (transfer learning). |

### 5. Feature Engineering (Technical Indicators)

| Activity | What Was Actually Done | MIT Learning Applied |
|----------|------------------------|----------------------|
| Computed technical indicators | Engineered per-ticker technical-analysis features from raw OHLCV data using pandas: SMA(10, 20), EMA(10, 20), RSI(14) (Wilder's smoothing), MACD(12, 26) with signal(9) and histogram, Daily Return (`pct_change`), and 20-day rolling Volatility plus its annualized form (notebook `03_feature_engineering.ipynb`). | Feature Engineering – deriving predictive technical features from time-series data. |
| Verified no missing values & saved | Dropped indicator warm-up rows so the engineered feature columns contain no missing values, then saved per-ticker feature CSVs and a combined `features_all_tickers.csv` to `data/processed/`. | Data Quality Assessment; preparing a clean feature matrix for modeling. |

---

## MIT Curriculum Areas Demonstrated So Far

| MIT Learning Area | Where Demonstrated |
|-------------------|--------------------|
| Data Collection & Acquisition | `yfinance` downloader script; loading the news dataset |
| Data Wrangling & Cleaning | Multi-format loaders, datetime/type conversion, missing/duplicate checks, mixed-type column fix |
| Descriptive Statistics & Probability | Summary stats, daily returns, annualized volatility |
| Exploratory Data Analysis | Correlation matrix, performance comparison, news dataset profiling & filtering |
| Natural Language Processing / Deep Learning | FinBERT (BERT transformer) sentiment classification of news headlines, run on Google Colab GPU |
| Feature Engineering | Technical indicators (SMA, EMA, RSI, MACD, Daily Return, Volatility) computed per ticker in notebook 03 |

---

## Presentation Talking Points (based on completed work)

1. **End-to-end start:** Automated acquisition of real market data plus loading a real news dataset.
2. **Real-world data cleaning:** Handling multiple CSV formats, mixed data types, and missing values on genuine messy data.
3. **Statistical analysis:** Correlation across the 7 stocks and computation of returns and annualized volatility.
4. **Dataset profiling:** Understanding coverage of the news dataset (by ticker, publisher, and content availability) before any modeling.
5. **Applied NLP / transfer learning:** Used a finance-domain pretrained transformer (FinBERT) to convert unstructured news headlines into structured sentiment features (label + score), running on cloud GPU (Google Colab) to overcome local hardware limits.

---

*Maintenance note: Append a new row to the relevant table only after an activity is actually completed, and add the area to "Curriculum Areas Demonstrated" if newly covered. Do not list planned or not-yet-done work.*

*Sync note: Whenever a new activity is completed and logged here, also strike through the matching item(s) in `todo/MIT_AI_ML_Capstone_Quest_Detailed.html` (add `class="task done"`, set the checkbox to `checked`, and change `☐` to `☑`) if a corresponding task exists there, so the HTML quest tracker stays in sync with this log.*
