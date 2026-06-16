# Power BI Dashboard Setup Guide

This guide will help you update your Power BI file according to the project requirements.

## Prerequisites
- Power BI Desktop installed
- The project directory has:
  - `data/processed/` directory with all cleaned CSVs
  - `bluestock_mf.db` (SQLite database, optional alternative)

---

## Step 1: Data Connection
### Option A: Connect to Cleaned CSVs (Recommended)
1. Open your `mutual fund page 1.pbix` file
2. Go to **Home > Get Data > Text/CSV**
3. Navigate to `data/processed/` directory
4. Import all 10 CSV files:
   - `01_fund_master.csv`
   - `02_nav_history.csv`
   - `03_aum_by_fund_house.csv`
   - `04_monthly_sip_inflows.csv`
   - `05_category_inflows.csv`
   - `06_industry_folio_count.csv`
   - `07_scheme_performance.csv`
   - `08_investor_transactions.csv`
   - `09_portfolio_holdings.csv`
   - `10_benchmark_indices.csv`
5. Click **Load** for each file

### Option B: Connect via SQLite ODBC
1. Install SQLite ODBC Driver if not already installed
2. In Power BI: **Home > Get Data > More... > Database > ODBC**
3. Select your SQLite DSN or connect directly to `bluestock_mf.db`
4. Load all tables

---

## Step 2: Create Relationships
1. Go to **Model** view
2. Create the following relationships:
   - `01_fund_master[amfi_code]` ↔ `02_nav_history[amfi_code]` (1-to-many)
   - `01_fund_master[amfi_code]` ↔ `07_scheme_performance[amfi_code]` (1-to-many)
   - `01_fund_master[amfi_code]` ↔ `08_investor_transactions[amfi_code]` (1-to-many)
   - `01_fund_master[amfi_code]` ↔ `09_portfolio_holdings[amfi_code]` (1-to-many)
   - Date columns should be related between tables where applicable

---

## Step 3: Build Page 1 - Industry Overview
### KPI Cards
Create four KPI cards:
1. **Total AUM (₹81L Cr)**:
   - Use `03_aum_by_fund_house[aum_lakh_crore]`
   - Sum it up and format as currency (₹)
2. **SIP Inflows (₹31K Cr)**:
   - Use `04_monthly_sip_inflows[sip_inflow_crore]`
   - Sum it up and format as currency (₹)
3. **Folios (26.12 Cr)**:
   - Use `06_industry_folio_count[total_folios_crore]`
   - Take the latest value
4. **Schemes (1,908)**:
   - Count distinct `01_fund_master[amfi_code]`

### Line Chart: Industry AUM Trend (2022–2025)
- **X-axis**: `03_aum_by_fund_house[date]`
- **Y-axis**: `03_aum_by_fund_house[aum_lakh_crore]`
- Filter date to 2022–2025

### Bar Chart: AUM by AMC
- **X-axis**: `03_aum_by_fund_house[aum_lakh_crore]` (sum)
- **Y-axis**: `03_aum_by_fund_house[fund_house]`
- Sort descending by AUM

---

## Step 4: Build Page 2 - Fund Performance
### Scatter Plot: Return vs Risk
- **X-axis**: `07_scheme_performance[return_3yr_pct]`
- **Y-axis**: `07_scheme_performance[std_dev_ann_pct]`
- **Bubble size**: `07_scheme_performance[aum_crore]`
- **Legend**: `01_fund_master[category]`

### Fund Scorecard Table
- Show: scheme_name, fund_house, category, return_3yr_pct, sharpe_ratio, alpha, beta, aum_crore, risk_grade
- Make it sortable by clicking column headers

### NAV Line vs Benchmark
- **X-axis**: `02_nav_history[date]`
- **Y-axis 1**: `02_nav_history[nav]` (for selected fund)
- **Y-axis 2**: `10_benchmark_indices[close_value]` (for Nifty 50)

### Slicers
- Fund house: `01_fund_master[fund_house]`
- Category: `01_fund_master[category]`
- Plan: `01_fund_master[plan]`

---

## Step 5: Build Page 3 - Investor Analytics
### Bar Chart: Transaction Amount by State
- **X-axis**: `08_investor_transactions[amount_inr]` (sum)
- **Y-axis**: `08_investor_transactions[state]`

### Donut Chart: Transaction Type Split
- **Values**: `08_investor_transactions[amount_inr]` (sum)
- **Legend**: `08_investor_transactions[transaction_type]`

### Bar Chart: Age Group vs Avg SIP Amount
- **X-axis**: Average of `08_investor_transactions[amount_inr]` (filter to SIP only)
- **Y-axis**: `08_investor_transactions[age_group]`

### Monthly Transaction Volume Line
- **X-axis**: Month from `08_investor_transactions[transaction_date]`
- **Y-axis**: Count of `08_investor_transactions[transaction_id]`

### Slicers
- State: `08_investor_transactions[state]`
- Age group: `08_investor_transactions[age_group]`
- City tier: `08_investor_transactions[city_tier]`

---

## Step 6: Build Page 4 - SIP & Market Trends
### Dual-Axis Chart: SIP Inflow (Bar) + Nifty 50 (Line)
- **X-axis**: `04_monthly_sip_inflows[month]`
- **Y-axis 1 (Bar)**: `04_monthly_sip_inflows[sip_inflow_crore]`
- **Y-axis 2 (Line)**: `10_benchmark_indices[close_value]` (filter to Nifty 50)
- Filter date to 2022–2025

### Category Inflow Heatmap
- Use `05_category_inflows`
- **Rows**: Month
- **Columns**: Category
- **Values**: Net inflow (color-coded)

### Top 5 Categories by Net Inflow (FY25)
- Filter `05_category_inflows` to FY25
- Show top 5 categories by net inflow

---

## Step 7: Add Interactivity
1. **Drill-through**: Right-click fund scorecard table > **Drill-through** > Create drill-through page for NAV details
2. **Tooltips**: Add tooltips to all charts showing relevant details
3. **Bluestock Theme**: Go to **View > Themes** and apply a custom theme with Bluestock colors
4. **Logo**: Add Bluestock logo to all pages

---

## Step 8: Export Deliverables
1. Save as `bluestock_mf_dashboard.pbix`
2. Export to PDF: **File > Export > Export to PDF**
3. Export each page as PNG: For each page, go to **File > Export > Export to Image**
