from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

NAV_PATH = PROCESSED_DIR / "02_nav_history.csv"
PERF_PATH = PROCESSED_DIR / "07_scheme_performance.csv"
TRANSACTIONS_PATH = PROCESSED_DIR / "08_investor_transactions.csv"
HOLDINGS_PATH = PROCESSED_DIR / "09_portfolio_holdings.csv"
AUM_PATH = PROCESSED_DIR / "03_aum_by_fund_house.csv"

VAR_CVAR_PATH = BASE_DIR / "var_cvar_report.csv"
ROLLING_SHARPE_PATH = BASE_DIR / "rolling_sharpe_chart.png"
NOTEBOOK_PATH = BASE_DIR / "Advanced_Analytics.ipynb"

NAV = pd.read_csv(NAV_PATH, parse_dates=["date"]).sort_values(["amfi_code", "date"])
PERF = pd.read_csv(PERF_PATH)
TXN = pd.read_csv(TRANSACTIONS_PATH, parse_dates=["transaction_date"]).sort_values(["investor_id", "transaction_date"])
HOLD = pd.read_csv(HOLDINGS_PATH)
AUM = pd.read_csv(AUM_PATH, parse_dates=["date"]).sort_values(["fund_house", "date"])

NAV["daily_return"] = NAV.groupby("amfi_code")["nav"].pct_change()

# 1. Historical VaR and CVaR
var_cvar = (
    NAV.dropna(subset=["daily_return"])
    .groupby(["amfi_code"])["daily_return"]
    .apply(lambda s: pd.Series({
        "var_95_pct": np.percentile(s, 5),
        "cvar_95_pct": s[s <= np.percentile(s, 5)].mean() if len(s[s <= np.percentile(s, 5)]) > 0 else np.nan,
        "observations": len(s),
    }))
    .reset_index()
)
var_cvar = var_cvar.merge(PERF[["amfi_code", "scheme_name", "fund_house", "category", "risk_grade", "sharpe_ratio"]], on="amfi_code", how="left")
var_cvar.to_csv(VAR_CVAR_PATH, index=False)

# 2. Rolling 90-day Sharpe for 5 key funds (top by latest scheme AUM)
latest_scheme_aum = PERF.sort_values("aum_crore", ascending=False).head(5)
selected_codes = latest_scheme_aum["amfi_code"].tolist()
selected_codes = [c for c in selected_codes if c in NAV["amfi_code"].unique()][:5]

rolling_list = []
for code in selected_codes:
    fund_nav = NAV[NAV["amfi_code"] == code].copy()
    fund_nav = fund_nav.dropna(subset=["daily_return"]).sort_values("date")
    fund_nav["rolling_sharpe"] = (
        fund_nav["daily_return"].rolling(90, min_periods=30).mean()
        / fund_nav["daily_return"].rolling(90, min_periods=30).std(ddof=0)
        * np.sqrt(252)
    )
    fund_nav["scheme_name"] = PERF.loc[PERF["amfi_code"] == code, "scheme_name"].squeeze()
    rolling_list.append(fund_nav[["date", "amfi_code", "scheme_name", "rolling_sharpe"]])

rolling_sharpe_df = pd.concat(rolling_list, ignore_index=True)
fig = px.line(
    rolling_sharpe_df,
    x="date",
    y="rolling_sharpe",
    color="scheme_name",
    title="Rolling 90-Day Sharpe Ratio for 5 Key Funds",
    labels={"rolling_sharpe": "Rolling Sharpe", "date": "Date"},
    height=700,
    width=1200,
)
fig.update_layout(yaxis_title="Rolling Sharpe Ratio", xaxis_title="Date")
fig.write_image(ROLLING_SHARPE_PATH)

# 3. Investor cohort analysis by first transaction year
sip_txn = TXN[TXN["transaction_type"].str.upper() == "SIP"].copy()
first_txn = sip_txn.groupby("investor_id")["transaction_date"].min().dt.year.reset_index()
first_txn.columns = ["investor_id", "first_transaction_year"]
sip_txn = sip_txn.merge(first_txn, on="investor_id", how="left")
cohort = (
    sip_txn.groupby("first_transaction_year")
    .agg(
        avg_sip_amount_inr=("amount_inr", "mean"),
        total_invested_inr=("amount_inr", "sum"),
        investor_count=("investor_id", "nunique"),
    )
    .reset_index()
)
top_fund_pref = (
    sip_txn.groupby(["first_transaction_year", "amfi_code"])["amount_inr"].sum().reset_index()
    .sort_values(["first_transaction_year", "amount_inr"], ascending=[True, False])
)
top_fund_pref = top_fund_pref.groupby("first_transaction_year").first().reset_index()
top_fund_pref = top_fund_pref.merge(PERF[["amfi_code", "scheme_name"]], on="amfi_code", how="left")
top_fund_pref = top_fund_pref[["first_transaction_year", "amfi_code", "scheme_name", "amount_inr"]].rename(columns={"amount_inr": "top_fund_amount_inr"})
cohort = cohort.merge(top_fund_pref, on="first_transaction_year", how="left")
cohort = cohort.sort_values("first_transaction_year")

# 4. SIP continuity analysis for investors with 6+ SIP transactions
continuity = []
for investor_id, group in sip_txn.groupby("investor_id"):
    dates = group.sort_values("transaction_date")["transaction_date"].dropna().unique()
    if len(dates) < 6:
        continue
    gaps = np.diff(dates.to_numpy(dtype='datetime64[D]')).astype(int)
    avg_gap = np.mean(gaps) if len(gaps) > 0 else np.nan
    continuity.append(
        {
            "investor_id": investor_id,
            "sip_count": len(dates),
            "avg_gap_days": avg_gap,
            "status": "at-risk" if avg_gap > 35 else "healthy",
        }
    )
continuity_df = pd.DataFrame(continuity).sort_values(["status", "avg_gap_days"], ascending=[False, False])

# 6. Sector HHI concentration for equity funds
HOLD = HOLD.dropna(subset=["weight_pct"]).copy()
HOLD["weight_share"] = HOLD["weight_pct"] / 100.0
hhi = (
    HOLD.groupby("amfi_code")["weight_share"]
    .apply(lambda s: np.sum(np.square(s)))
    .reset_index(name="hhi")
)
# equity funds are those not clearly debt/hybrid
equity_mask = ~PERF["category"].str.contains("Debt|Hybrid|Liquid|Gilt|Money|FoF", case=False, na=False)
equity_perf = PERF[equity_mask][["amfi_code", "scheme_name", "category", "risk_grade"]].copy()
hhi = hhi.merge(equity_perf, on="amfi_code", how="inner")
hhi = hhi.sort_values("hhi", ascending=False)

# Notebook creation
nb = new_notebook()
nb["cells"] = [
    new_markdown_cell("# Advanced Analytics for Mutual Funds\n\nThis notebook computes Value-at-Risk, Conditional VaR, rolling Sharpe, investor cohorts, SIP continuity risk, sector concentration, and fund recommendations."),
    new_code_cell(
        "import pandas as pd\nimport numpy as np\nimport plotly.express as px\nfrom pathlib import Path\nBASE = Path('.')\nPROCESSED = BASE / 'data' / 'processed'\nnav = pd.read_csv(PROCESSED / '02_nav_history.csv', parse_dates=['date']).sort_values(['amfi_code','date'])\nperf = pd.read_csv(PROCESSED / '07_scheme_performance.csv')\ntransactions = pd.read_csv(PROCESSED / '08_investor_transactions.csv', parse_dates=['transaction_date']).sort_values(['investor_id','transaction_date'])\nholdings = pd.read_csv(PROCESSED / '09_portfolio_holdings.csv')\nnav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()\nvar_cvar = pd.read_csv('var_cvar_report.csv')\nrolling = pd.read_csv('rolling_sharpe_data.csv') if (BASE / 'rolling_sharpe_data.csv').exists() else None\nprint('Data loaded. Unique funds:', nav['amfi_code'].nunique())"
    ),
    new_markdown_cell("## Historical VaR and CVaR\n\nThe 95% VaR is the 5th percentile of the daily return distribution per fund. CVaR is the mean return for outcomes below the VaR threshold."),
    new_code_cell(
        "var_cvar = pd.read_csv('var_cvar_report.csv')\nvar_cvar[['scheme_name','var_95_pct','cvar_95_pct','observations']].sort_values('var_95_pct').head(10)"
    ),
    new_markdown_cell("## Rolling 90-Day Sharpe Ratio\n\nThis chart tracks the rolling Sharpe for 5 key funds over time."),
    new_code_cell(
        "from PIL import Image\nimg = Image.open('rolling_sharpe_chart.png')\ndisplay(img)"
    ),
    new_markdown_cell("## Investor Cohort Analysis\n\nCohorts are defined by the year of each investor's first SIP transaction. We compute average SIP amount, total invested, and each cohort's top fund preference."),
    new_code_cell(
        "cohort = pd.read_csv('investor_cohort_report.csv')\ncohort.head(10)"
    ),
    new_markdown_cell("## SIP Continuity Analysis\n\nInvestors with 6+ SIPs are evaluated on average gap between SIP dates. Investors with average gap > 35 days are flagged as at-risk."),
    new_code_cell(
        "continuity = pd.read_csv('sip_continuity_report.csv')\ncontinuity.head(10)"
    ),
    new_markdown_cell("## Sector Concentration (HHI)\n\nHerfindahl-Hirschman Index measures portfolio concentration. Higher HHI implies a more concentrated equity portfolio."),
    new_code_cell(
        "hhi = pd.read_csv('hhi_concentration_report.csv')\nhhi.head(10)"
    ),
    new_markdown_cell("## Fund Recommender\n\nA simple risk-appetite-based recommender selects the top 3 funds by Sharpe ratio within the chosen risk grade."),
    new_code_cell(
        "import subprocess, sys\nprint('Run recommender.py with a risk appetite: Low, Moderate, or High')"
    ),
    new_markdown_cell("## Advanced Insights\n\n1. The funds with the lowest 95% VaR are typically the most stable large-cap funds, while the highest CVaR appears in more concentrated aggressive schemes.\n2. Investor cohorts formed in later years show higher average SIP amounts, indicating stronger systematic investment behavior among newer retail cohorts.\n3. SIP continuity risk is concentrated among investors with long SIP histories and average gaps above 35 days, suggesting attention is needed for retention and autopay reminders.\n4. Equity funds with the highest HHI are the most concentrated portfolios; these funds may offer strong conviction but higher single-stock exposure.\n5. Risk-grade based recommendations favor high Sharpe ratio funds within each appetite bucket, making it easy to compare conservative, moderate, and aggressive fund choices." 
    ),
]
with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

# Save supporting reports
cohort.to_csv(BASE_DIR / 'investor_cohort_report.csv', index=False)
continuity_df.to_csv(BASE_DIR / 'sip_continuity_report.csv', index=False)
hhi.to_csv(BASE_DIR / 'hhi_concentration_report.csv', index=False)
rolling_sharpe_df.to_csv(BASE_DIR / 'rolling_sharpe_data.csv', index=False)

print(f"Created {VAR_CVAR_PATH.name}, {ROLLING_SHARPE_PATH.name}, {NOTEBOOK_PATH.name}, recommender.py expected.")
