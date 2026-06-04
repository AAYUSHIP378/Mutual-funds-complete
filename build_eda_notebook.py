import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()
cells = []

cells.append(new_markdown_cell('# EDA Analysis for Mutual Funds\n\nThis notebook contains exploratory charts and key findings for NAV, AUM, SIP inflows, investor demographics, geographic distribution, folio growth, and sector allocation.'))

cells.append(new_code_cell('import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport seaborn as sns\nimport matplotlib.pyplot as plt\nfrom pathlib import Path\n\nplt.style.use("seaborn-v0_8")\nFIG_DIR = Path("figures")\nFIG_DIR.mkdir(parents=True, exist_ok=True)\n'))

cells.append(new_code_cell('processed = Path("data/processed")\nnav = pd.read_csv(processed / "02_nav_history.csv", parse_dates=["date"])\naum = pd.read_csv(processed / "03_aum_by_fund_house.csv", parse_dates=["date"])\nsip = pd.read_csv(processed / "04_monthly_sip_inflows.csv", parse_dates=["month"])\ncategory_inflows = pd.read_csv(processed / "05_category_inflows.csv", parse_dates=["month"])\nfolio = pd.read_csv(processed / "06_industry_folio_count.csv", parse_dates=["month"])\nperf = pd.read_csv(processed / "07_scheme_performance.csv")\ntransactions = pd.read_csv(processed / "08_investor_transactions.csv", parse_dates=["transaction_date"])\nholdings = pd.read_csv(processed / "09_portfolio_holdings.csv", parse_dates=["portfolio_date"])\n\nperf_map = perf.set_index("amfi_code")["scheme_name"].to_dict()\nnav["scheme_name"] = nav["amfi_code"].map(perf_map)\nnav = nav.sort_values(["scheme_name", "date"])\n\naum["year"] = aum["date"].dt.year\nfolio["year"] = folio["month"].dt.year\n\nnav = nav[(nav["date"].dt.year >= 2022) & (nav["date"].dt.year <= 2026)]\naum_filtered = aum[aum["year"].between(2022, 2025)]\nsip = sip[(sip["month"].dt.year >= 2022) & (sip["month"].dt.year <= 2025)]\ncategory_inflows = category_inflows[(category_inflows["month"].dt.year >= 2022) & (category_inflows["month"].dt.year <= 2025)]\nfolio = folio[(folio["month"].dt.year >= 2022) & (folio["month"].dt.year <= 2025)]\n'))

cells.append(new_markdown_cell('## NAV Trend Analysis\n\nDaily NAV trends are plotted across all 40 schemes for 2022–2026, with 2023 bull market and 2024 correction periods highlighted.'))

cells.append(new_code_cell('fig = px.line(nav, x="date", y="nav", color="scheme_name", line_group="scheme_name", height=700, width=1100, title="Daily NAV Trend for All Schemes (2022-2026)")\nfig.update_layout(showlegend=False)\nfig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1, line_width=0, annotation_text="2023 Bull Run", annotation_position="top left")\nfig.add_vrect(x0="2024-01-01", x1="2024-12-31", fillcolor="red", opacity=0.1, line_width=0, annotation_text="2024 Correction", annotation_position="top left")\nfig.write_image(FIG_DIR / "nav_trend_all_schemes.png")\nfig.show()'))

cells.append(new_markdown_cell('## AUM Growth by Fund House\n\nGrouped bar chart of annual AUM by fund house from 2022 to 2025, highlighting SBI Mutual Fund.'))

cells.append(new_code_cell('fig, ax = plt.subplots(figsize=(14, 8))\nsns.barplot(data=aum_filtered, x="year", y="aum_crore", hue="fund_house", ax=ax)\nax.set_title("AUM Growth by Fund House (2022-2025)")\nax.set_ylabel("AUM (Crore INR)")\nax.set_xlabel("Year")\nax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)\nfig.tight_layout()\nfig.savefig(FIG_DIR / "aum_growth_by_fund_house.png")\nplt.close(fig)'))

cells.append(new_markdown_cell('### SBI AUM Dominance\n\nSBI Mutual Fund leads the market with a dominant AUM share, exceeding ₹12.5 lakh crore in the 2022-2025 window.'))

cells.append(new_code_cell('sbi = aum_filtered[aum_filtered["fund_house"] == "SBI Mutual Fund"]\nfig = px.bar(sbi, x="year", y="aum_crore", text="aum_crore", title="SBI Mutual Fund AUM by Year", height=550, width=900)\nfig.update_traces(marker_color="darkblue", texttemplate="%{text:.0f}")\nfig.update_layout(yaxis_title="AUM (Crore INR)")\nfig.write_image(FIG_DIR / "sbi_aum_dominance.png")\nfig.show()'))

cells.append(new_markdown_cell('## SIP Inflow Time Series\n\nMonthly SIP inflows from January 2022 through December 2025, with annotation on the all-time high December 2025 observation.'))

cells.append(new_code_cell('fig = px.line(sip, x="month", y="sip_inflow_crore", title="Monthly SIP Inflow Trend (2022-2025)", markers=True, height=600, width=1000)\npeak = sip.loc[sip["sip_inflow_crore"].idxmax()]\nfig.add_annotation(x=peak["month"], y=peak["sip_inflow_crore"], text=f"₹{peak[\"sip_inflow_crore\"]:.0f} Cr all-time high", showarrow=True, arrowhead=2, ay=-80)\nfig.write_image(FIG_DIR / "sip_inflow_trend.png")\nfig.show()'))

cells.append(new_markdown_cell('## Category Inflow Heatmap\n\nCategory inflows displayed as a heatmap across months and fund categories.'))

cells.append(new_code_cell('pivot = category_inflows.pivot(index="category", columns="month", values="net_inflow_crore").fillna(0)\nfig, ax = plt.subplots(figsize=(16, 8))\nsns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn", ax=ax)\nax.set_title("Net Category Inflows by Month")\nax.set_xlabel("Month")\nax.set_ylabel("Fund Category")\nfig.tight_layout()\nfig.savefig(FIG_DIR / "category_inflow_heatmap.png")\nplt.close(fig)'))

cells.append(new_markdown_cell('## Investor Demographics\n\nAge group distribution, SIP amount box plot by age group, and gender split for investor transactions.'))

cells.append(new_code_cell('sips = transactions[transactions["transaction_type"] == "SIP"].copy()\nage_counts = sips["age_group"].value_counts()\nfig, ax = plt.subplots(figsize=(7, 7))\nax.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=140, wedgeprops={"linewidth": 1, "edgecolor": "white"})\nax.set_title("Age Group Distribution for SIP Investors")\nfig.savefig(FIG_DIR / "age_group_distribution_pie.png")\nplt.close(fig)'))

cells.append(new_code_cell('fig, ax = plt.subplots(figsize=(12, 7))\nsns.boxplot(data=sips, x="age_group", y="amount_inr", palette="Set2", ax=ax)\nax.set_title("SIP Amount Distribution by Age Group")\nax.set_ylabel("Amount (INR)")\nax.set_xlabel("Age Group")\nax.set_yscale("log")\nfig.tight_layout()\nfig.savefig(FIG_DIR / "sip_amount_boxplot_age_group.png")\nplt.close(fig)'))

cells.append(new_code_cell('gender_counts = sips["gender"].value_counts()\nfig = px.pie(names=gender_counts.index, values=gender_counts.values, title="Gender Split for SIP Investors", height=550, width=700)\nfig.write_image(FIG_DIR / "gender_split_pie.png")\nfig.show()'))

cells.append(new_markdown_cell('## Geographic Distribution\n\nSIP amount by state and city tier distribution for T30 vs B30.'))

cells.append(new_code_cell('state_data = sips.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=True)\nfig, ax = plt.subplots(figsize=(12, 10))\nsns.barplot(data=state_data, x="amount_inr", y="state", palette="viridis", ax=ax)\nax.set_title("Total SIP Amount by State")\nax.set_xlabel("Total SIP Amount (INR)")\nax.set_ylabel("State")\nfig.tight_layout()\nfig.savefig(FIG_DIR / "sip_amount_by_state.png")\nplt.close(fig)'))

cells.append(new_code_cell('tier_counts = sips["city_tier"].value_counts()\nfig = px.pie(names=tier_counts.index, values=tier_counts.values, title="City Tier Split: T30 vs B30", height=550, width=700)\nfig.write_image(FIG_DIR / "city_tier_pie.png")\nfig.show()'))

cells.append(new_markdown_cell('## Folio Count Growth\n\nLine chart showing industry folio growth from January 2022 to December 2025, with key milestones highlighted.'))

cells.append(new_code_cell('fig, ax = plt.subplots(figsize=(12, 7))\nsns.lineplot(data=folio, x="month", y="total_folios_crore", marker="o", ax=ax)\nax.set_title("Total Folio Count Growth (2022-2025)")\nax.set_ylabel("Total Folios (Crore)")\nax.set_xlabel("Month")\nfor label, value in [("2022-01-01", 13.26), ("2025-12-01", 26.12)]:\n    ax.annotate(f"{value:.2f} Cr", xy=(pd.to_datetime(label), value), xytext=(pd.to_datetime(label), value + 1.2), arrowprops={"arrowstyle": "->"})\nfig.tight_layout()\nfig.savefig(FIG_DIR / "folio_count_growth.png")\nplt.close(fig)'))

cells.append(new_markdown_cell('## NAV Return Correlation Matrix\n\nPairwise correlations of daily NAV returns for 10 selected funds show relative risk and co-movement patterns.'))

cells.append(new_code_cell('selected = perf.sort_values("aum_crore", ascending=False).head(10)["amfi_code"].tolist()\nreturns = nav[nav["amfi_code"].isin(selected)].copy()\nreturns = returns.pivot(index="date", columns="scheme_name", values="nav").pct_change().dropna(how="all")\nfig, ax = plt.subplots(figsize=(12, 10))\nsns.heatmap(returns.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)\nax.set_title("Daily NAV Return Correlation for Top 10 Funds by AUM")\nfig.tight_layout()\nfig.savefig(FIG_DIR / "nav_return_correlation_heatmap.png")\nplt.close(fig)'))

cells.append(new_markdown_cell('## Sector Allocation Donut\n\nAggregate sector weights across portfolio holdings to show overall asset allocation.'))

cells.append(new_code_cell('sector = holdings.groupby("sector", as_index=False)["weight_pct"].sum().sort_values("weight_pct", ascending=False)\nfig, ax = plt.subplots(figsize=(8, 8))\nax.pie(sector["weight_pct"], labels=sector["sector"], autopct="%1.1f%%", startangle=140, pctdistance=0.85)\ncentre_circle = plt.Circle((0, 0), 0.55, fc="white")\nfig.gca().add_artist(centre_circle)\nax.set_title("Aggregate Sector Allocation Donut")\nfig.savefig(FIG_DIR / "sector_allocation_donut.png")\nplt.close(fig)'))

cells.append(new_markdown_cell('## Additional Insights\n\nTop performing funds by 3-year return and category inflow patterns add further context to investor behavior and fund performance.'))

cells.append(new_code_cell('top_returns = perf.sort_values("return_3yr_pct", ascending=False).head(10)\nfig, ax = plt.subplots(figsize=(12, 7))\nsns.barplot(data=top_returns, x="return_3yr_pct", y="scheme_name", palette="mako", ax=ax)\nax.set_title("Top 10 Funds by 3-Year Return")\nax.set_xlabel("3-Year Return (%)")\nax.set_ylabel("Scheme")\nfig.tight_layout()\nfig.savefig(FIG_DIR / "top_10_3yr_return.png")\nplt.close(fig)'))

cells.append(new_code_cell('category_time = category_inflows.pivot(index="month", columns="category", values="net_inflow_crore").fillna(0)\nfig, ax = plt.subplots(figsize=(14, 8))\ncategory_time.plot(ax=ax, marker="o")\nax.set_title("Net Inflow Trends by Category")\nax.set_ylabel("Net Inflow (Crore INR)")\nax.set_xlabel("Month")\nax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc=2)\nfig.tight_layout()\nfig.savefig(FIG_DIR / "category_inflow_trend_lines.png")\nplt.close(fig)'))

nb['cells'] = cells
with open('EDA_Analysis.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
print('wrote EDA_Analysis.ipynb')
