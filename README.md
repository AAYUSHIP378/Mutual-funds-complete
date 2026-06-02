# Mutual Funds Day 1 Ingestion

Day 1 setup for the mutual fund capstone project.

## Structure

- `data/raw/` - provided CSV datasets plus live NAV extracts
- `data/processed/` - reserved for cleaned outputs
- `notebooks/` - exploratory notebooks
- `sql/` - SQL assets
- `dashboard/` - dashboard assets
- `reports/` - generated data quality summaries

## Scripts

- `download_drive_csvs.py` downloads the provided Google Drive source files into `data/raw`.
- `live_nav_fetch.py` fetches NAV history/latest rows from `mfapi.in` for HDFC Top 100 Direct and five key schemes.
- `data_ingestion.py` profiles the raw CSVs, prints `.shape`, `.dtypes`, and `.head()`, explores fund master fields, validates AMFI codes, and writes `reports/day1_data_quality_summary.md`.

## Run

```powershell
.\.venv\Scripts\python.exe download_drive_csvs.py
.\.venv\Scripts\python.exe live_nav_fetch.py
.\.venv\Scripts\python.exe data_ingestion.py
```
