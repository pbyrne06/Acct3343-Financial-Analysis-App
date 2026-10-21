# Tech & Software Screener

An interactive stock-screening app for technology and software companies, built with Streamlit.

Screen a universe of **100 companies** using seven financial filters calibrated for the tech sector:

- **Sell side (risk flags):** Max Accruals (STA), Min Altman Z-Score, Max SNOA
- **Buy side (value & quality):** Min Gross Profitability (GPA), Min Book-to-Market (B/M), Max Price-to-Sales (P/S), Max Debt-to-Equity (D/E)

## Features

- **Mutually exclusive recommendations** — a company that triggers any risk flag can never be a Buy Candidate. Every firm is classified as Buy Candidate (long), Sell Flag (short/avoid), or Hold / Watchlist.
- **Ranking** — Buy Candidates are ranked by a Quality–Value Score and Sell Flags by a Risk Score (both percentile-based, 0–100), or re-ranked by any single metric from the sidebar.
- **Evidence for every call** — Sell rows list the exact risk flags triggered; the Company Lookup shows any firm's recommendation and the values behind it.
- **Top Picks summary** — the five strongest long and short recommendations at the current settings, each with its supporting metrics, rebuilding live as filters change.
- **Downloads** — export either portfolio as a CSV.
- **Visual analysis** — a quality-vs-value scatter (bubble size = market cap) and an Altman Z-Score distribution with the live distress threshold.
- **Metric guide** — an in-app explainer covering what each metric measures and how recommendations are formed.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` — the Streamlit app
- `universe.csv` — the 100-company universe and its financial metrics
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — app theme

*Built for ACCT 3343 — Financial Accounting Analysis. For informational and educational purposes only — not investment advice.*
