CREATE TABLE fund_master (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date DATE NOT NULL,
    benchmark TEXT NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    exit_load_pct REAL NOT NULL,
    min_sip_amount INTEGER NOT NULL,
    min_lumpsum_amount INTEGER NOT NULL,
    fund_manager TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    sebi_category_code TEXT NOT NULL
);

CREATE TABLE nav_history (
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
);

CREATE TABLE aum_by_fund_house (
    date DATE NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore INTEGER NOT NULL,
    num_schemes INTEGER NOT NULL,
    PRIMARY KEY (date, fund_house)
);

CREATE TABLE monthly_sip_inflows (
    month DATE PRIMARY KEY,
    sip_inflow_crore INTEGER NOT NULL,
    active_sip_accounts_crore REAL NOT NULL,
    new_sip_accounts_lakh REAL NOT NULL,
    sip_aum_lakh_crore REAL NOT NULL,
    yoy_growth_pct REAL
);

CREATE TABLE category_inflows (
    month DATE NOT NULL,
    category TEXT NOT NULL,
    net_inflow_crore REAL NOT NULL,
    PRIMARY KEY (month, category)
);

CREATE TABLE industry_folio_count (
    month DATE PRIMARY KEY,
    total_folios_crore REAL NOT NULL,
    equity_folios_crore REAL NOT NULL,
    debt_folios_crore REAL NOT NULL,
    hybrid_folios_crore REAL NOT NULL,
    others_folios_crore REAL NOT NULL
);

CREATE TABLE scheme_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL NOT NULL,
    return_3yr_pct REAL NOT NULL,
    return_5yr_pct REAL NOT NULL,
    benchmark_3yr_pct REAL NOT NULL,
    alpha REAL NOT NULL,
    beta REAL NOT NULL,
    sharpe_ratio REAL NOT NULL,
    sortino_ratio REAL NOT NULL,
    std_dev_ann_pct REAL NOT NULL,
    max_drawdown_pct REAL NOT NULL,
    aum_crore INTEGER NOT NULL,
    expense_ratio_pct REAL NOT NULL,
    morningstar_rating INTEGER NOT NULL,
    risk_grade TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
);

CREATE TABLE investor_transactions (
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr INTEGER NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    city_tier TEXT NOT NULL,
    age_group TEXT NOT NULL,
    gender TEXT NOT NULL,
    annual_income_lakh REAL NOT NULL,
    payment_mode TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
);

CREATE TABLE portfolio_holdings (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL NOT NULL,
    current_price_inr REAL NOT NULL,
    portfolio_date DATE NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
);

CREATE TABLE benchmark_indices (
    date DATE NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL NOT NULL,
    PRIMARY KEY (date, index_name)
);
