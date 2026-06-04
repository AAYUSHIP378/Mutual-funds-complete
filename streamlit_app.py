"""Day 8 Bonus Challenge 2: Interactive Streamlit Dashboard

A web-based alternative to Power BI for exploring mutual fund analytics.
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Page config
st.set_page_config(page_title="Bluestock MF Analytics", layout="wide")
st.title("Bluestock Mutual Fund Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    nav = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"])
    perf = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    aum = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", parse_dates=["date"])
    transactions = pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv", parse_dates=["transaction_date"])
    var_cvar = pd.read_csv(BASE_DIR / "var_cvar_report.csv")
    return nav, perf, aum, transactions, var_cvar

nav, perf, aum, transactions, var_cvar = load_data()

# Sidebar navigation
page = st.sidebar.selectbox(
    "Select Page",
    ["Industry Overview", "Fund Performance", "Investor Analytics", "Risk Analysis"]
)

if page == "Industry Overview":
    st.header("Industry Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Funds", len(perf))
    with col2:
        st.metric("Total Investors", transactions["investor_id"].nunique())
    with col3:
        st.metric("Total Transactions", len(transactions))
    
    fund_house_filter = st.selectbox("Filter by Fund House", ["All"] + sorted(perf["fund_house"].unique()))
    if fund_house_filter != "All":
        perf_filtered = perf[perf["fund_house"] == fund_house_filter]
    else:
        perf_filtered = perf
    
    st.subheader(f"Top Funds by Sharpe Ratio ({fund_house_filter})")
    top_funds = perf_filtered.nlargest(10, "sharpe_ratio")[["scheme_name", "fund_house", "category", "sharpe_ratio", "return_3yr_pct"]]
    st.dataframe(top_funds, use_container_width=True)

elif page == "Fund Performance":
    st.header("Fund Performance Analysis")
    
    selected_fund = st.selectbox("Select Fund", perf["scheme_name"].tolist())
    fund_data = perf[perf["scheme_name"] == selected_fund].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("3-Year Return", f"{fund_data['return_3yr_pct']:.2f}%")
    with col2:
        st.metric("Sharpe Ratio", f"{fund_data['sharpe_ratio']:.2f}")
    with col3:
        st.metric("Alpha", f"{fund_data['alpha']:.2f}%")
    with col4:
        st.metric("Max Drawdown", f"{fund_data['max_drawdown_pct']:.2f}%")
    
    st.subheader("NAV Trend")
    fund_nav = nav[nav["amfi_code"] == fund_data["amfi_code"]].sort_values("date")
    fig = px.line(fund_nav, x="date", y="nav", title=f"NAV Trend: {selected_fund}")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Investor Analytics":
    st.header("Investor Analytics")
    
    txn_type_filter = st.selectbox("Transaction Type", ["All", "SIP", "Lump Sum"])
    if txn_type_filter != "All":
        txn_filtered = transactions[transactions["transaction_type"] == txn_type_filter]
    else:
        txn_filtered = transactions
    
    state_summary = txn_filtered.groupby("state")["amount_inr"].sum().sort_values(ascending=False).head(10)
    fig = px.bar(state_summary, title="Top 10 States by Transaction Amount", labels={"value": "Amount (INR)", "index": "State"})
    st.plotly_chart(fig, use_container_width=True)
    
    age_summary = txn_filtered.groupby("age_group")["amount_inr"].mean()
    fig = px.bar(age_summary, title="Average Transaction Amount by Age Group", labels={"value": "Avg Amount (INR)", "index": "Age Group"})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Risk Analysis":
    st.header("Risk Analysis")
    
    var_display = var_cvar.nsmallest(10, "var_95_pct")[["scheme_name", "fund_house", "var_95_pct", "cvar_95_pct", "sharpe_ratio"]]
    st.subheader("Funds with Lowest VaR (95%)")
    st.dataframe(var_display, use_container_width=True)
    
    risk_grade_filter = st.selectbox("Risk Grade", sorted(perf["risk_grade"].unique()))
    risk_filtered = perf[perf["risk_grade"] == risk_grade_filter]
    st.subheader(f"Funds with {risk_grade_filter} Risk Grade")
    st.dataframe(risk_filtered[["scheme_name", "category", "sharpe_ratio", "return_3yr_pct"]], use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Bluestock MF Capstone v1.0")
