import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

plt.style.use("seaborn-v0_8")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)
processed = Path("data/processed")

nav = pd.read_csv(processed / "02_nav_history.csv", parse_dates=["date"])
aum = pd.read_csv(processed / "03_aum_by_fund_house.csv", parse_dates=["date"])
sip = pd.read_csv(processed / "04_monthly_sip_inflows.csv", parse_dates=["month"])
category_inflows = pd.read_csv(processed / "05_category_inflows.csv", parse_dates=["month"])
folio = pd.read_csv(processed / "06_industry_folio_count.csv", parse_dates=["month"])
perf = pd.read_csv(processed / "07_scheme_performance.csv")
transactions = pd.read_csv(processed / "08_investor_transactions.csv", parse_dates=["transaction_date"])
holdings = pd.read_csv(processed / "09_portfolio_holdings.csv", parse_dates=["portfolio_date"])

perf_map = perf.set_index("amfi_code")["scheme_name"].to_dict()
nav["scheme_name"] = nav["amfi_code"].map(perf_map)
nav = nav.sort_values(["scheme_name", "date"])

aum["year"] = aum["date"].dt.year
folio["year"] = folio["month"].dt.year
nav = nav[(nav["date"].dt.year >= 2022) & (nav["date"].dt.year <= 2026)]
aum_filtered = aum[aum["year"].between(2022, 2025)]
sip = sip[(sip["month"].dt.year >= 2022) & (sip["month"].dt.year <= 2025)]
category_inflows = category_inflows[(category_inflows["month"].dt.year >= 2022) & (category_inflows["month"].dt.year <= 2025)]
folio = folio[(folio["month"].dt.year >= 2022) & (folio["month"].dt.year <= 2025)]

# NAV trend
fig = px.line(nav, x="date", y="nav", color="scheme_name", line_group="scheme_name", height=700, width=1100, title="Daily NAV Trend for All Schemes (2022-2026)")
fig.update_layout(showlegend=False)
fig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1, line_width=0, annotation_text="2023 Bull Run", annotation_position="top left")
fig.add_vrect(x0="2024-01-01", x1="2024-12-31", fillcolor="red", opacity=0.1, line_width=0, annotation_text="2024 Correction", annotation_position="top left")
fig.write_image(FIG_DIR / "nav_trend_all_schemes.png")

# AUM grouped bar
fig, ax = plt.subplots(figsize=(14, 8))
sns.barplot(data=aum_filtered, x="year", y="aum_crore", hue="fund_house", ax=ax)
ax.set_title("AUM Growth by Fund House (2022-2025)")
ax.set_ylabel("AUM (Crore INR)")
ax.set_xlabel("Year")
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.tight_layout()
fig.savefig(FIG_DIR / "aum_growth_by_fund_house.png")
plt.close(fig)

# SBI dominance
sbi = aum_filtered[aum_filtered["fund_house"] == "SBI Mutual Fund"]
fig = px.bar(sbi, x="year", y="aum_crore", text="aum_crore", title="SBI Mutual Fund AUM by Year", height=550, width=900)
fig.update_traces(marker_color="darkblue", texttemplate="%{text:.0f}")
fig.update_layout(yaxis_title="AUM (Crore INR)")
fig.write_image(FIG_DIR / "sbi_aum_dominance.png")

# SIP monthly trend
fig = px.line(sip, x="month", y="sip_inflow_crore", title="Monthly SIP Inflow Trend (2022-2025)", markers=True, height=600, width=1000)
peak = sip.loc[sip["sip_inflow_crore"].idxmax()]
fig.add_annotation(x=peak["month"].strftime("%Y-%m-%d"), y=peak["sip_inflow_crore"], text=f"₹{peak['sip_inflow_crore']:.0f} Cr all-time high", showarrow=True, arrowhead=2, ay=-80)
fig.write_image(FIG_DIR / "sip_inflow_trend.png")

# Category heatmap
pivot = category_inflows.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)
fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn", ax=ax)
ax.set_title("Net Category Inflows by Month")
ax.set_xlabel("Month")
ax.set_ylabel("Fund Category")
fig.tight_layout()
fig.savefig(FIG_DIR / "category_inflow_heatmap.png")
plt.close(fig)

# Age distribution
sips = transactions[transactions["transaction_type"] == "SIP"].copy()
age_counts = sips["age_group"].value_counts()
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=140, wedgeprops={"linewidth": 1, "edgecolor": "white"})
ax.set_title("Age Group Distribution for SIP Investors")
fig.savefig(FIG_DIR / "age_group_distribution_pie.png")
plt.close(fig)

# SIP amount by age group
fig, ax = plt.subplots(figsize=(12, 7))
sns.boxplot(data=sips, x="age_group", y="amount_inr", palette="Set2", ax=ax)
ax.set_title("SIP Amount Distribution by Age Group")
ax.set_ylabel("Amount (INR)")
ax.set_xlabel("Age Group")
ax.set_yscale("log")
fig.tight_layout()
fig.savefig(FIG_DIR / "sip_amount_boxplot_age_group.png")
plt.close(fig)

# Gender split
gender_counts = sips["gender"].value_counts()
fig = px.pie(names=gender_counts.index, values=gender_counts.values, title="Gender Split for SIP Investors", height=550, width=700)
fig.write_image(FIG_DIR / "gender_split_pie.png")

# State SIP amounts
state_data = sips.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=True)
fig, ax = plt.subplots(figsize=(12, 10))
sns.barplot(data=state_data, x="amount_inr", y="state", palette="viridis", ax=ax)
ax.set_title("Total SIP Amount by State")
ax.set_xlabel("Total SIP Amount (INR)")
ax.set_ylabel("State")
fig.tight_layout()
fig.savefig(FIG_DIR / "sip_amount_by_state.png")
plt.close(fig)

# City tier split
tier_counts = sips["city_tier"].value_counts()
fig = px.pie(names=tier_counts.index, values=tier_counts.values, title="City Tier Split: T30 vs B30", height=550, width=700)
fig.write_image(FIG_DIR / "city_tier_pie.png")

# Folio growth
fig, ax = plt.subplots(figsize=(12, 7))
sns.lineplot(data=folio, x="month", y="total_folios_crore", marker="o", ax=ax)
ax.set_title("Total Folio Count Growth (2022-2025)")
ax.set_ylabel("Total Folios (Crore)")
ax.set_xlabel("Month")
ax.annotate("13.26 Cr", xy=(pd.to_datetime("2022-01-01"), 13.26), xytext=(pd.to_datetime("2022-04-01"), 14.5), arrowprops={"arrowstyle": "->"})
ax.annotate("26.12 Cr", xy=(pd.to_datetime("2025-12-01"), 26.12), xytext=(pd.to_datetime("2025-09-01"), 24), arrowprops={"arrowstyle": "->"})
fig.tight_layout()
fig.savefig(FIG_DIR / "folio_count_growth.png")
plt.close(fig)

# NAV return correlation
selected = perf.sort_values("aum_crore", ascending=False).head(10)["amfi_code"].tolist()
returns = nav[nav["amfi_code"].isin(selected)].copy()
returns = returns.pivot(index="date", columns="scheme_name", values="nav").pct_change().dropna(how="all")
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(returns.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
ax.set_title("Daily NAV Return Correlation for Top 10 Funds by AUM")
fig.tight_layout()
fig.savefig(FIG_DIR / "nav_return_correlation_heatmap.png")
plt.close(fig)

# Sector allocation donut
sector = holdings.groupby("sector", as_index=False)["weight_pct"].sum().sort_values("weight_pct", ascending=False)
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(sector["weight_pct"], labels=sector["sector"], autopct="%1.1f%%", startangle=140, pctdistance=0.85)
centre_circle = plt.Circle((0, 0), 0.55, fc="white")
fig.gca().add_artist(centre_circle)
ax.set_title("Aggregate Sector Allocation Donut")
fig.savefig(FIG_DIR / "sector_allocation_donut.png")
plt.close(fig)

# Additional top returns
top_returns = perf.sort_values("return_3yr_pct", ascending=False).head(10)
fig, ax = plt.subplots(figsize=(12, 7))
sns.barplot(data=top_returns, x="return_3yr_pct", y="scheme_name", palette="mako", ax=ax)
ax.set_title("Top 10 Funds by 3-Year Return")
ax.set_xlabel("3-Year Return (%)")
ax.set_ylabel("Scheme")
fig.tight_layout()
fig.savefig(FIG_DIR / "top_10_3yr_return.png")
plt.close(fig)

# Category inflow trend lines
category_time = category_inflows.pivot(index="month", columns="category", values="net_inflow_crore").fillna(0)
fig, ax = plt.subplots(figsize=(14, 8))
category_time.plot(ax=ax, marker="o")
ax.set_title("Net Inflow Trends by Category")
ax.set_ylabel("Net Inflow (Crore INR)")
ax.set_xlabel("Month")
ax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc=2)
fig.tight_layout()
fig.savefig(FIG_DIR / "category_inflow_trend_lines.png")
plt.close(fig)

print('exported pictures to', FIG_DIR)
