# Day 1 Data Quality Summary

## 01_fund_master.csv
- Shape: 40 rows x 15 columns
- Columns: amfi_code, fund_house, scheme_name, category, sub_category, plan, launch_date, benchmark, expense_ratio_pct, exit_load_pct, min_sip_amount, min_lumpsum_amount, fund_manager, risk_category, sebi_category_code
- Anomalies: No obvious structural anomalies detected

## 02_nav_history.csv
- Shape: 46,000 rows x 3 columns
- Columns: amfi_code, date, nav
- Anomalies: No obvious structural anomalies detected

## 03_aum_by_fund_house.csv
- Shape: 90 rows x 5 columns
- Columns: date, fund_house, aum_lakh_crore, aum_crore, num_schemes
- Anomalies: No obvious structural anomalies detected

## 04_monthly_sip_inflows.csv
- Shape: 48 rows x 6 columns
- Columns: month, sip_inflow_crore, active_sip_accounts_crore, new_sip_accounts_lakh, sip_aum_lakh_crore, yoy_growth_pct
- Anomalies: No obvious structural anomalies detected

## 05_category_inflows.csv
- Shape: 144 rows x 3 columns
- Columns: month, category, net_inflow_crore
- Anomalies: No obvious structural anomalies detected

## 06_industry_folio_count.csv
- Shape: 21 rows x 6 columns
- Columns: month, total_folios_crore, equity_folios_crore, debt_folios_crore, hybrid_folios_crore, others_folios_crore
- Anomalies: No obvious structural anomalies detected

## 07_scheme_performance.csv
- Shape: 40 rows x 19 columns
- Columns: amfi_code, scheme_name, fund_house, category, plan, return_1yr_pct, return_3yr_pct, return_5yr_pct, benchmark_3yr_pct, alpha, beta, sharpe_ratio, sortino_ratio, std_dev_ann_pct, max_drawdown_pct, aum_crore, expense_ratio_pct, morningstar_rating, risk_grade
- Anomalies: No obvious structural anomalies detected

## 08_investor_transactions.csv
- Shape: 32,778 rows x 13 columns
- Columns: investor_id, transaction_date, amfi_code, transaction_type, amount_inr, state, city, city_tier, age_group, gender, annual_income_lakh, payment_mode, kyc_status
- Anomalies: No obvious structural anomalies detected

## 09_portfolio_holdings.csv
- Shape: 322 rows x 8 columns
- Columns: amfi_code, stock_symbol, stock_name, sector, weight_pct, market_value_cr, current_price_inr, portfolio_date
- Anomalies: No obvious structural anomalies detected

## 10_benchmark_indices.csv
- Shape: 8,050 rows x 3 columns
- Columns: date, index_name, close_value
- Anomalies: No obvious structural anomalies detected

## Bluestock_MF_Capstone_Project.csv
- Anomaly: Skipped `Bluestock_MF_Capstone_Project.csv`: File has PDF content, not CSV content

## AMFI Code Validation

- Fund master dataset: `01_fund_master.csv` using `amfi_code`
- NAV history dataset: `02_nav_history.csv` using `amfi_code`
- Fund master unique AMFI codes: 40
- NAV history unique AMFI codes: 40
- Fund master codes missing from NAV history: 0
- Result: every fund master AMFI code exists in NAV history.

## Fund Master Exploration (01_fund_master.csv)

- Unique fund houses from `fund_house`: 10 values
  Sample: Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund
- Unique categories from `category`: 2 values
  Sample: Debt, Equity
- Unique sub-categories from `sub_category`: 12 values
  Sample: ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value
- Unique risk grades from `risk_category`: 5 values
  Sample: High, Low, Moderate, Moderately High, Very High

### AMFI Scheme Code Structure
- AMFI scheme codes are numeric identifiers for mutual fund schemes. In this dataset, `amfi_code` length distribution is {6: 40}.
- These codes are used as stable join keys between fund master records and NAV history/API data.