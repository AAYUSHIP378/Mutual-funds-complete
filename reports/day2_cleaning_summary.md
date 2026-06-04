# Day 2 Cleaning Summary

## 01_fund_master.csv
- Raw shape: 40 rows x 15 columns
- Processed shape: 40 rows x 15 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing AMFI codes: 0
- Saved processed file: `data/processed/01_fund_master.csv`

## 02_nav_history.csv
- Raw shape: 46,000 rows x 3 columns
- Processed shape: 46,000 rows x 3 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing AMFI codes: 0
- Non-positive NAV values: 0
- Saved processed file: `data/processed/02_nav_history.csv`

## 03_aum_by_fund_house.csv
- Raw shape: 90 rows x 5 columns
- Processed shape: 90 rows x 5 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Non-positive AUM values: 0
- Saved processed file: `data/processed/03_aum_by_fund_house.csv`

## 04_monthly_sip_inflows.csv
- Raw shape: 48 rows x 6 columns
- Processed shape: 48 rows x 6 columns
- Duplicate rows: 0
- Missing cells after cleaning: 12
- Missing YoY growth values: 12 expected for initial baseline months.
- Saved processed file: `data/processed/04_monthly_sip_inflows.csv`

## 05_category_inflows.csv
- Raw shape: 144 rows x 3 columns
- Processed shape: 144 rows x 3 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Saved processed file: `data/processed/05_category_inflows.csv`

## 06_industry_folio_count.csv
- Raw shape: 21 rows x 6 columns
- Processed shape: 21 rows x 6 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Saved processed file: `data/processed/06_industry_folio_count.csv`

## 07_scheme_performance.csv
- Raw shape: 40 rows x 19 columns
- Processed shape: 40 rows x 19 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing AMFI codes: 0
- Non-positive AUM values: 0
- Saved processed file: `data/processed/07_scheme_performance.csv`

## 08_investor_transactions.csv
- Raw shape: 32,778 rows x 13 columns
- Processed shape: 32,778 rows x 13 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing AMFI codes: 0
- Non-positive transaction amount values: 0
- Saved processed file: `data/processed/08_investor_transactions.csv`

## 09_portfolio_holdings.csv
- Raw shape: 322 rows x 8 columns
- Processed shape: 322 rows x 8 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing AMFI codes: 0
- Non-positive stock price values: 0
- Portfolio weights outside 0-100 pct: 0
- Saved processed file: `data/processed/09_portfolio_holdings.csv`

## 10_benchmark_indices.csv
- Raw shape: 8,050 rows x 3 columns
- Processed shape: 8,050 rows x 3 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Non-positive benchmark close values: 0
- Saved processed file: `data/processed/10_benchmark_indices.csv`

## Bluestock_MF_Capstone_Project.csv
- Skipped `Bluestock_MF_Capstone_Project.csv`: PDF content found in a CSV-named file

## live_nav_118632_nippon_large_cap.csv
- Raw shape: 3,298 rows x 12 columns
- Processed shape: 3,298 rows x 11 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 0
- Non-positive NAV values: 0
- Dropped all-null columns: meta_isin_div_reinvestment
- Saved processed file: `data/processed/live_nav_118632_nippon_large_cap.csv`

## live_nav_119092_axis_bluechip.csv
- Raw shape: 3,565 rows x 12 columns
- Processed shape: 3,565 rows x 11 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 3,565
- Non-positive NAV values: 0
- Dropped all-null columns: meta_isin_div_reinvestment
- Saved processed file: `data/processed/live_nav_119092_axis_bluechip.csv`

## live_nav_119551_sbi_bluechip.csv
- Raw shape: 3,236 rows x 12 columns
- Processed shape: 3,236 rows x 12 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 3,236
- Non-positive NAV values: 0
- Saved processed file: `data/processed/live_nav_119551_sbi_bluechip.csv`

## live_nav_120503_icici_bluechip.csv
- Raw shape: 3,307 rows x 12 columns
- Processed shape: 3,307 rows x 11 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 3,307
- Non-positive NAV values: 1
- Dropped all-null columns: meta_isin_div_reinvestment
- Saved processed file: `data/processed/live_nav_120503_icici_bluechip.csv`

## live_nav_120841_kotak_bluechip.csv
- Raw shape: 3,301 rows x 12 columns
- Processed shape: 3,301 rows x 11 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 3,301
- Non-positive NAV values: 0
- Dropped all-null columns: meta_isin_div_reinvestment
- Saved processed file: `data/processed/live_nav_120841_kotak_bluechip.csv`

## live_nav_125497_hdfc_top_100_direct.csv
- Raw shape: 3,091 rows x 12 columns
- Processed shape: 3,091 rows x 11 columns
- Duplicate rows: 0
- Missing cells after cleaning: 0
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 3,091
- Non-positive NAV values: 0
- Dropped all-null columns: meta_isin_div_reinvestment
- Saved processed file: `data/processed/live_nav_125497_hdfc_top_100_direct.csv`

## live_nav_latest_key_schemes.csv
- Raw shape: 6 rows x 12 columns
- Processed shape: 6 rows x 12 columns
- Duplicate rows: 0
- Missing cells after cleaning: 5
- Missing scheme codes: 0
- Rows where requested scheme name does not match API metadata: 5
- Non-positive NAV values: 0
- Saved processed file: `data/processed/live_nav_latest_key_schemes.csv`

## Relationship Validation
- `02_nav_history.csv` AMFI codes not in fund master: 0
- `07_scheme_performance.csv` AMFI codes not in fund master: 0
- `08_investor_transactions.csv` AMFI codes not in fund master: 0
- `09_portfolio_holdings.csv` AMFI codes not in fund master: 0

## Enriched Outputs
- Created `data/processed/fund_nav_history_enriched.csv` with 46,000 rows.
- NAV rows missing fund master details after join: 0
- Created `data/processed/investor_transactions_enriched.csv` with 32,778 rows.
- Created `data/processed/portfolio_holdings_enriched.csv` with 322 rows.

## SQL Schema
- Added `sql/day2_schema.sql` for database-ready table definitions and core keys.
