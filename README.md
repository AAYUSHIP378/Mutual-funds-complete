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
- `data_cleaning.py` standardizes dates, strings, and numeric fields, validates key relationships, writes cleaned files to `data/processed`, creates enriched analysis-ready datasets, and writes `reports/day2_cleaning_summary.md`.

## Run

```powershell
.\.venv\Scripts\python.exe download_drive_csvs.py
.\.venv\Scripts\python.exe live_nav_fetch.py
.\.venv\Scripts\python.exe data_ingestion.py
.\.venv\Scripts\python.exe data_cleaning.py
```

## Build Data Warehouse

```powershell
.\.venv\Scripts\python.exe build_data_warehouse.py
```

This script:
- cleans and writes all processed CSV files to `data/processed/`
- creates the SQLite star schema in `bluestock_mf.db`
- verifies row counts for the loaded tables
- uses `sql/schema.sql` for DDL and writes analytical queries to `sql/queries.sql`

## Generate Dashboard Outputs

```powershell
.\.venv\Scripts\python.exe build_dashboard_reports.py
```

This script generates:
- `dashboard/figures/dashboard_page1.png`
- `dashboard/figures/dashboard_page2.png`
- `dashboard/figures/dashboard_page3.png`
- `dashboard/figures/dashboard_page4.png`
- `dashboard/dashboard_report.pdf`

Note: a Power BI `.pbix` file cannot be created from this environment because Power BI Desktop is not available.

## Advanced Analytics (Day 6)

```powershell
.\.venv\Scripts\python.exe build_advanced_analytics.py
```

This script generates:
- `Advanced_Analytics.ipynb`
- `var_cvar_report.csv`
- `rolling_sharpe_chart.png`
- `recommender.py`
- `investor_cohort_report.csv`
- `sip_continuity_report.csv`
- `hhi_concentration_report.csv`

## Final Deliverables (Day 7)

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```

This command runs the full workflow and generates:
- `Final_Report.pdf`
- `Bluestock_MF_Presentation.pptx`
- final analytics and dashboard outputs

Note: `run_pipeline.py` will skip raw download if `data/raw/` already contains source files.

## Inspect SQLite Database

With SQLite installed:

```powershell
sqlite3 bluestock_mf.db
.tables
```

Or with Python:

```python
import sqlite3
conn = sqlite3.connect('bluestock_mf.db')
for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(row[0])
conn.close()
```
