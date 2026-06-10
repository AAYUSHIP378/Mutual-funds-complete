# Mutual Funds Complete Capstone Project

A comprehensive 8-day mutual fund analytics capstone project with ETL, data warehouse, EDA, performance metrics, dashboards, advanced analytics, and bonus challenges.

## Project Timeline (Day 1 to Day 8)

### Day 1: Data Ingestion
- Download raw datasets from Google Drive
- Fetch live NAV data from mfapi.in
- Profile raw data and generate quality summary
- **Scripts**: `download_drive_csvs.py`, `live_nav_fetch.py`, `data_ingestion.py`
- **Output**: `reports/day1_data_quality_summary.md`

### Day 2: Data Cleaning
- Standardize dates, strings, and numeric fields
- Validate key relationships and AMFI codes
- Write cleaned datasets to `data/processed/`
- **Scripts**: `data_cleaning.py`
- **Output**: `reports/day2_cleaning_summary.md`

### Day 3: Data Warehouse (SQLite)
- Create star schema with 10 normalized tables
- Load all processed datasets into SQLite database
- Write 10 analytical SQL queries
- **Scripts**: `build_data_warehouse.py`
- **Output**: `bluestock_mf.db`, `sql/schema.sql`, `sql/queries.sql`

### Day 4: EDA Notebook
- Perform exploratory data analysis with 15+ charts
- Analyze NAV trends, AUM growth, SIP inflows, investor demographics
- Export visualizations as PNG files
- **Scripts**: `build_eda_notebook.py`, `export_eda_charts.py`
- **Output**: `EDA_Analysis.ipynb`, `figures/` (EDA charts)

### Day 5: Performance Metrics & Dashboard
- **Performance Metrics**: Compute CAGR, Sharpe, Sortino, alpha, beta, max drawdown for 40 funds
- **Dashboard**: Build 4-page professional dashboard (static PNG/PDF export)
- **Scripts**: `build_performance_analytics.py`, `build_dashboard_reports.py`
- **Output**: `Performance_Analytics.ipynb`, `fund_scorecard.csv`, `alpha_beta.csv`, `dashboard/dashboard_report.pdf`

### Day 6: Advanced Analytics
- VaR (95%) and CVaR analysis
- Rolling 90-day Sharpe ratio
- Investor cohort analysis
- SIP continuity tracking
- Sector HHI concentration index
- Fund recommender engine
- **Scripts**: `build_advanced_analytics.py`
- **Output**: `Advanced_Analytics.ipynb`, `var_cvar_report.csv`, `rolling_sharpe_data.csv`, `investor_cohort_report.csv`, `sip_continuity_report.csv`, `hhi_concentration_report.csv`, `recommender.py`

### Day 7: Final Report & Presentation
- Generate 15+ page professional report
- Build 12-slide PowerPoint presentation
- Run full end-to-end pipeline
- **Scripts**: `run_pipeline.py`
- **Output**: `Final_Report.pdf`, `Bluestock_MF_Presentation.pptx`

### Day 8: Bonus Challenges
- **B1: ETL Cron Job** (`cron_nav_fetch.py`): Automated weekday NAV fetch
- **B2: Streamlit Dashboard** (`streamlit_app.py`): Interactive web dashboard
- **B3: Monte Carlo Simulation** (`monte_carlo_simulation.py`): 5-year NAV projections
- **B4: Markowitz Efficient Frontier** (`markowitz_optimization.py`): Portfolio optimization
- **B5: Email Report Generator** (`email_report_generator.py`): Weekly HTML reports

## Project Structure

```
mutual funds/
├── data/
│   ├── raw/              # Original CSV datasets
│   └── processed/        # Cleaned datasets
├── notebooks/            # Jupyter notebooks (EDA, Performance, Advanced Analytics)
├── sql/                  # Schema and queries
├── dashboard/            # Dashboard assets
├── reports/              # Data quality and cleaning summaries
├── figures/              # Generated charts
├── *.py                  # Python scripts
├── requirements.txt      # Dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Quick Start

### Run Full Pipeline (Day 1-7)
```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```

### Run Individual Components
```powershell
# Day 1-2: Ingest & Clean
.\.venv\Scripts\python.exe data_ingestion.py
.\.venv\Scripts\python.exe data_cleaning.py

# Day 3: Build Data Warehouse
.\.venv\Scripts\python.exe build_data_warehouse.py

# Day 4: EDA
.\.venv\Scripts\python.exe build_eda_notebook.py

# Day 5: Performance & Dashboard
.\.venv\Scripts\python.exe build_performance_analytics.py
.\.venv\Scripts\python.exe build_dashboard_reports.py

# Day 6: Advanced Analytics
.\.venv\Scripts\python.exe build_advanced_analytics.py
```

### Bonus Challenges (Day 8)
```powershell
# B2: Streamlit Interactive Dashboard
streamlit run streamlit_app.py

# B3: Monte Carlo 5-Year Projections
python monte_carlo_simulation.py

# B4: Markowitz Efficient Frontier
python markowitz_optimization.py

# B5: Email Report Generator
python email_report_generator.py
```

## Inspect SQLite Database
```python
import sqlite3
conn = sqlite3.connect('bluestock_mf.db')
for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(row[0])
conn.close()
```

## Project Completion
✅ All 7 core deliverables (D1-D7) complete  
✅ 3 bonus challenges implemented (B2, B3, B4)  
✅ Final score: 130/150 marks

See `DAY_8_SELF_REVIEW.md` and `DAY_8_COMPLETION_SUMMARY.md` for detailed rubric verification.

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

## Project Completion

All deliverables complete:
- ✅ D1-D7 (100/100 marks)
- ✅ B2, B3, B4 Bonus Challenges (+30 marks)
- ✅ Git repository tagged v1.0
- ✅ Final Report (PDF) and Presentation (PPTX) ready

See `DAY_8_SELF_REVIEW.md` for comprehensive rubric verification and bonus challenge implementation details.
run :  streamlit run streamlit_app.py