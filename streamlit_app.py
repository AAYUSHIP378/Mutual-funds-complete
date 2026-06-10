"""Day 8 Bonus Challenge 2: Interactive Streamlit Dashboard with Authentication

A web-based alternative to Power BI for exploring mutual fund analytics with login/signup.
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from auth import register_user, verify_login, load_users, get_user_info

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Page config
st.set_page_config(page_title="Bluestock MF Analytics", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.page = "login"

# Load data
@st.cache_data
def load_data():
    nav = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"])
    perf = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    aum = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", parse_dates=["date"])
    transactions = pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv", parse_dates=["transaction_date"])
    
    # Load and pivot var_cvar data
    var_cvar_raw = pd.read_csv(BASE_DIR / "var_cvar_report.csv")
    var_cvar = var_cvar_raw.pivot_table(
        index=['amfi_code', 'scheme_name', 'fund_house', 'category', 'risk_grade', 'sharpe_ratio'],
        columns='level_1',
        values='daily_return'
    ).reset_index()
    
    return nav, perf, aum, transactions, var_cvar

def show_login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🏦 Bluestock MF Analytics")
        st.markdown("### Mutual Fund Performance Dashboard")
        st.markdown("---")
        
        login_tab, signup_tab = st.tabs(["Login", "Create Account"])
        
        with login_tab:
            st.subheader("Login to Your Account")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                success, message = verify_login(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.page = "dashboard"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            
            st.markdown("---")
            st.markdown("**Demo Credentials:**")
            st.info("Create an account or use:\nUsername: `demo`\nPassword: `demo123`", icon="ℹ️")
        
        with signup_tab:
            st.subheader("Create a New Account")
            new_username = st.text_input("Choose Username", key="signup_username")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Password (min 6 chars)", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True, type="primary"):
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, message = register_user(new_username, new_email, new_password)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account in the Login tab.")
                    else:
                        st.error(message)

def show_dashboard():
    """Display main dashboard"""
    # Top bar with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("📊 Bluestock Mutual Fund Analytics")
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.page = "login"
            st.rerun()
    
    st.markdown(f"**Welcome, {st.session_state.username}!**")
    st.markdown("---")
    
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
        
        # Display VaR and CVaR analysis
        var_display = var_cvar.nsmallest(10, "var_95_pct")[["scheme_name", "fund_house", "var_95_pct", "cvar_95_pct", "sharpe_ratio"]]
        var_display.columns = ["Fund Name", "Fund House", "VaR (95%)", "CVaR (95%)", "Sharpe Ratio"]
        st.subheader("Funds with Lowest VaR (95%) - Lower is Safer")
        st.dataframe(var_display, use_container_width=True)
        
        risk_grade_filter = st.selectbox("Risk Grade", sorted(perf["risk_grade"].unique()))
        risk_filtered = perf[perf["risk_grade"] == risk_grade_filter]
        st.subheader(f"Funds with {risk_grade_filter} Risk Grade")
        st.dataframe(risk_filtered[["scheme_name", "category", "sharpe_ratio", "return_3yr_pct"]], use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.info("Bluestock MF Capstone v1.0\n\nWith Authentication", icon="ℹ️")

# Main app logic
if st.session_state.authenticated:
    show_dashboard()
else:
    show_login_page()
