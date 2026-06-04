# Bluestock MF Data Dictionary

## Cleaned CSV files in `data/processed/`
- `01_fund_master.csv`: fund master metadata, including scheme details, launch dates, benchmark, expense ratios, minimum SIP/lumpsum amounts, fund manager, risk category, and SEBI category.
- `02_nav_history.csv`: cleaned NAV time series for each `amfi_code` with continuous calendar dates and forward-filled NAV for holidays/weekends.
- `03_aum_by_fund_house.csv`: AUM values by fund house and date.
- `04_monthly_sip_inflows.csv`: monthly SIP inflows and YoY measures.
- `05_category_inflows.csv`: net inflow amounts by category and month.
- `06_industry_folio_count.csv`: folio counts by industry category and month.
- `07_scheme_performance.csv`: scheme performance metrics with numeric return columns, expense ratio checks, and range validation.
- `08_investor_transactions.csv`: investor-level transaction data standardized for transaction type and KYC status, with invalid amounts removed.
- `09_portfolio_holdings.csv`: portfolio holdings by scheme with weights and market values.
- `10_benchmark_indices.csv`: benchmark index closing values by date.

## Star schema tables in `bluestock_mf.db`

### dim_date
- `date_id`: surrogate integer key
- `date`: calendar date
- `year`: year of the date
- `quarter`: quarter label, e.g. `Q1`
- `month`: month number
- `month_name`: month name
- `day`: day of month
- `weekday`: weekday name
- `is_weekend`: boolean indicator

### dim_fund
- `amfi_code`: AMFI scheme code primary key
- `scheme_name`: fund scheme name
- `fund_house`: AMC / fund house
- `category`: scheme category
- `sub_category`: more granular scheme category
- `plan`: plan type (Direct/Regular)
- `launch_date`: scheme launch date
- `benchmark`: benchmark index name
- `risk_category`: risk grading
- `expense_ratio_pct`: expense ratio percentage
- `exit_load_pct`: exit load percentage
- `min_sip_amount`: minimum SIP amount
- `min_lumpsum_amount`: minimum lumpsum amount
- `fund_manager`: manager name
- `sebi_category_code`: SEBI category code

### fact_nav
- `nav_id`: surrogate key
- `amfi_code`: foreign key to `dim_fund`
- `date_id`: foreign key to `dim_date`
- `nav`: Net Asset Value

### fact_transactions
- `transaction_id`: surrogate key
- `investor_id`: investor identifier
- `transaction_date`: transaction date
- `date_id`: foreign key to `dim_date`
- `amfi_code`: foreign key to `dim_fund`
- `transaction_type`: standardized transaction type (`SIP`, `Lumpsum`, `Redemption`)
- `amount_inr`: transaction amount in INR
- `state`: investor state
- `city`: investor city
- `city_tier`: city tier
- `age_group`: investor age bucket
- `gender`: investor gender
- `annual_income_lakh`: annual income in lakhs
- `payment_mode`: payment method
- `kyc_status`: KYC status (`Verified`, `Pending`)

### fact_performance
- `performance_id`: surrogate key
- `amfi_code`: foreign key to `dim_fund`
- `return_1yr_pct`: 1-year return
- `return_3yr_pct`: 3-year return
- `return_5yr_pct`: 5-year return
- `benchmark_3yr_pct`: benchmark 3-year return
- `alpha`: alpha
- `beta`: beta
- `sharpe_ratio`: Sharpe ratio
- `sortino_ratio`: Sortino ratio
- `std_dev_ann_pct`: annualized standard deviation
- `max_drawdown_pct`: maximum drawdown
- `aum_crore`: AUM in crores
- `expense_ratio_pct`: expense ratio percentage
- `expense_ratio_within_expected`: boolean flag for 0.1%–2.5% range
- `morningstar_rating`: Morningstar rating
- `risk_grade`: risk grade

### fact_aum
- `aum_id`: surrogate key
- `date_id`: foreign key to `dim_date`
- `fund_house`: fund house
- `aum_lakh_crore`: AUM in lakh crores
- `aum_crore`: AUM in crores
- `num_schemes`: number of schemes

## Analytical artifacts
- `sql/schema.sql`: star schema DDL definitions for `dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, and `fact_aum`.
- `sql/queries.sql`: ten analytical SQL queries including top funds by AUM, average NAV per month, YoY SIP growth, state transaction summaries, and expense ratio analysis.
