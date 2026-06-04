from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DASHBOARD_DIR = BASE_DIR / "dashboard"
FIG_DIR = DASHBOARD_DIR / "figures"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

NAV_PATH = PROCESSED_DIR / "02_nav_history.csv"
AUM_PATH = PROCESSED_DIR / "03_aum_by_fund_house.csv"
SIP_PATH = PROCESSED_DIR / "04_monthly_sip_inflows.csv"
CATEGORY_PATH = PROCESSED_DIR / "05_category_inflows.csv"
FOLIO_PATH = PROCESSED_DIR / "06_industry_folio_count.csv"
PERF_PATH = PROCESSED_DIR / "07_scheme_performance.csv"
TRANSACTIONS_PATH = PROCESSED_DIR / "08_investor_transactions.csv"
BENCHMARK_PATH = PROCESSED_DIR / "10_benchmark_indices.csv"

nav = pd.read_csv(NAV_PATH, parse_dates=["date"]).sort_values(["amfi_code", "date"])
aum = pd.read_csv(AUM_PATH, parse_dates=["date"]).sort_values("date")
sip = pd.read_csv(SIP_PATH, parse_dates=["month"]).sort_values("month")
category_inflows = pd.read_csv(CATEGORY_PATH, parse_dates=["month"]).sort_values(["category", "month"])
folios = pd.read_csv(FOLIO_PATH, parse_dates=["month"]).sort_values("month")
perf = pd.read_csv(PERF_PATH)
transactions = pd.read_csv(TRANSACTIONS_PATH, parse_dates=["transaction_date"]).sort_values("transaction_date")
benchmark = pd.read_csv(BENCHMARK_PATH, parse_dates=["date"]).sort_values("date")

# Page 1: Industry overview
latest_aum = aum[aum["date"] == aum["date"].max()].copy()
top_aum = latest_aum.sort_values("aum_crore", ascending=False).head(10)
recent_sip = sip[sip["month"] == sip["month"].max()].iloc[0]
latest_folios = folios[folios["month"] == folios["month"].max()].iloc[0]
latest_category = category_inflows[category_inflows["month"] == category_inflows["month"].max()].copy()
category_trend = category_inflows.pivot(index="month", columns="category", values="net_inflow_crore").fillna(0)

page1 = make_subplots(rows=2, cols=2, subplot_titles=[
    "Total AUM Trend (Top 6 Fund Houses)",
    "Top 10 Fund Houses by AUM",
    "Monthly SIP Inflow",
    "Net Inflow by Category"
])

for fund_house in top_aum['fund_house'].head(6):
    house_data = aum[aum['fund_house'] == fund_house]
    page1.add_trace(go.Scatter(x=house_data['date'], y=house_data['aum_crore'], mode='lines', name=fund_house), row=1, col=1)

page1.add_trace(go.Bar(x=top_aum['fund_house'], y=top_aum['aum_crore'], marker_color='blue', name='AUM'), row=1, col=2)
page1.add_trace(go.Bar(x=sip['month'], y=sip['sip_inflow_crore'], marker_color='green', name='Monthly SIP Inflows'), row=2, col=1)
for category in category_trend.columns[:5]:
    page1.add_trace(go.Scatter(x=category_trend.index, y=category_trend[category], mode='lines', name=str(category)), row=2, col=2)

page1.add_annotation(
    text=(
        f"Total AUM (latest): ₹{latest_aum['aum_crore'].sum():,.0f} Cr<br>"
        f"Latest SIP Inflow: ₹{recent_sip['sip_inflow_crore']:,.0f} Cr<br>"
        f"Active SIP Accounts: {recent_sip['active_sip_accounts_crore']:.2f} Cr<br>"
        f"Total Folios (latest): {latest_folios['total_folios_crore']:.2f} Cr"
    ),
    x=0.02,
    y=0.98,
    xref='paper',
    yref='paper',
    showarrow=False,
    align='left',
    font=dict(size=14)
)

page1.update_layout(height=1200, width=1400, title_text='Dashboard Page 1: Industry Overview', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
page1.write_image(FIG_DIR / 'dashboard_page1.png', scale=2)

# Page 2: Fund performance analytics
perf_sorted = perf.sort_values('aum_crore', ascending=False).head(12)
page2 = make_subplots(rows=2, cols=2, subplot_titles=[
    'Fund Return vs Risk',
    'Top Performing Funds by 3-Year Return',
    'Benchmark vs Top Fund NAV Trend',
    'Performance Scorecard (Top 8 Funds)'
], specs=[[{'type': 'xy'}, {'type': 'xy'}], [{'type': 'xy'}, {'type': 'table'}]], row_heights=[0.5, 0.5])

page2.add_trace(go.Scatter(
    x=perf_sorted['std_dev_ann_pct'],
    y=perf_sorted['return_3yr_pct'],
    mode='markers',
    marker=dict(size=perf_sorted['aum_crore'] / perf_sorted['aum_crore'].max() * 40 + 10, color=perf_sorted['alpha'], colorscale='Viridis', showscale=True, colorbar=dict(title='Alpha')),
    text=perf_sorted['scheme_name'],
    name='Funds'
), row=1, col=1)

page2.add_trace(go.Bar(
    x=perf_sorted.sort_values('return_3yr_pct', ascending=False)['return_3yr_pct'],
    y=perf_sorted.sort_values('return_3yr_pct', ascending=False)['scheme_name'],
    orientation='h',
    marker_color='darkcyan'
), row=1, col=2)

# benchmark comparison for top 3 funds by AUM
benchmark_line = benchmark[benchmark['index_name'] == 'NIFTY50']
top_funds = perf_sorted.head(3)
for _, row in top_funds.iterrows():
    fund_nav = nav[nav['amfi_code'] == row['amfi_code']].copy()
    if fund_nav.empty:
        continue
    fund_nav = fund_nav.sort_values('date')
    fund_nav['pct_change'] = fund_nav['nav'] / fund_nav['nav'].iloc[0] * 100
    page2.add_trace(go.Scatter(x=fund_nav['date'], y=fund_nav['pct_change'], mode='lines', name=row['scheme_name']), row=2, col=1)
page2.add_trace(go.Scatter(x=benchmark_line['date'], y=benchmark_line['close_value'] / benchmark_line['close_value'].iloc[0] * 100, mode='lines', name='NIFTY50 Benchmark', line=dict(dash='dash')), row=2, col=1)

scorecard = perf_sorted[['scheme_name', 'fund_house', 'category', 'return_3yr_pct', 'alpha', 'beta', 'sharpe_ratio']].head(8)
page2.add_trace(go.Table(
    header=dict(values=list(scorecard.columns), fill_color='paleturquoise', align='left'),
    cells=dict(values=[scorecard[c] for c in scorecard.columns], fill_color='white', align='left')
), row=2, col=2)

page2.update_layout(height=1200, width=1400, title_text='Dashboard Page 2: Fund Performance Analytics')
page2.write_image(FIG_DIR / 'dashboard_page2.png', scale=2)

# Page 3: Investor and transaction analytics
txn_types = transactions['transaction_type'].value_counts().reset_index()
txn_types.columns = ['transaction_type', 'count']
state_amount = transactions.groupby('state', as_index=False)['amount_inr'].sum().sort_values('amount_inr', ascending=False).head(12)
age_avg = transactions.groupby('age_group', as_index=False)['amount_inr'].mean().sort_values('amount_inr', ascending=False)
monthly_txn = transactions.groupby(transactions['transaction_date'].dt.to_period('M'))['amount_inr'].sum().reset_index()
monthly_txn['transaction_date'] = monthly_txn['transaction_date'].dt.to_timestamp()

page3 = make_subplots(rows=2, cols=2, subplot_titles=[
    'Transaction Mix by Type',
    'Top States by Transaction Amount',
    'Average Transaction Amount by Age Group',
    'Monthly Transaction Volume'
], specs=[[{'type': 'domain'}, {'type': 'xy'}], [{'type': 'xy'}, {'type': 'xy'}]])

page3.add_trace(go.Pie(labels=txn_types['transaction_type'], values=txn_types['count'], hole=0.35), row=1, col=1)
page3.add_trace(go.Bar(x=state_amount['amount_inr'], y=state_amount['state'], orientation='h', marker_color='mediumpurple'), row=1, col=2)
page3.add_trace(go.Bar(x=age_avg['age_group'], y=age_avg['amount_inr'], marker_color='seagreen'), row=2, col=1)
page3.add_trace(go.Scatter(x=monthly_txn['transaction_date'], y=monthly_txn['amount_inr'], mode='lines+markers', line=dict(color='firebrick')), row=2, col=2)
page3.update_layout(height=1200, width=1400, title_text='Dashboard Page 3: Investor & Transaction Analytics')
page3.write_image(FIG_DIR / 'dashboard_page3.png', scale=2)

# Page 4: SIP and market trends
nifty = benchmark[benchmark['index_name'] == 'NIFTY50']
merged = sip.merge(nifty[['date', 'close_value']], left_on='month', right_on='date', how='inner')
category_latest = category_inflows[category_inflows['month'] >= category_inflows['month'].max() - pd.DateOffset(months=11)]
category_summary = category_latest.groupby('category', as_index=False)['net_inflow_crore'].sum().sort_values('net_inflow_crore', ascending=False).head(8)

page4 = make_subplots(rows=3, cols=1, subplot_titles=[
    'SIP Inflow vs NIFTY50 Trend',
    'Category Net Inflow Heatmap',
    'Top Categories by Recent Net Inflow'
], shared_xaxes=False, vertical_spacing=0.12, row_heights=[0.35, 0.4, 0.25])

page4.add_trace(go.Bar(x=merged['month'], y=merged['sip_inflow_crore'], name='SIP Inflow (Cr)', marker_color='royalblue'), row=1, col=1)
page4.add_trace(go.Scatter(x=merged['month'], y=merged['close_value'] / 100, name='NIFTY50 Close /100', marker_color='orange', yaxis='y2'), row=1, col=1)
page4.update_layout(
    yaxis2=dict(title='NIFTY50 index /100', overlaying='y', side='right'),
)

pivot = category_inflows.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
heatmap = go.Heatmap(z=pivot.values, x=[m.strftime('%Y-%m') for m in pivot.columns], y=pivot.index, colorscale='RdYlGn')
page4.add_trace(heatmap, row=2, col=1)

page4.add_trace(go.Bar(x=category_summary['category'], y=category_summary['net_inflow_crore'], marker_color='darkorange'), row=3, col=1)
page4.update_layout(height=1300, width=1400, title_text='Dashboard Page 4: SIP & Market Trends')
page4.write_image(FIG_DIR / 'dashboard_page4.png', scale=2)

# Create PDF from the four PNG pages
png_paths = [FIG_DIR / f'dashboard_page{i}.png' for i in range(1, 5)]
with PdfPages(DASHBOARD_DIR / 'dashboard_report.pdf') as pdf:
    for p in png_paths:
        img = Image.open(p).convert('RGB')
        fig = plt.figure(figsize=(11.7, 8.3))
        plt.axis('off')
        plt.imshow(img)
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
        plt.close(fig)

with open(DASHBOARD_DIR / 'dashboard_note.md', 'w', encoding='utf-8') as f:
    f.write(
        '# Dashboard Deliverables\n\n'
        'Generated dashboard analytics as static outputs because Power BI Desktop is not available in this environment.\n\n'
        '## Outputs\n'
        '- `dashboard/figures/dashboard_page1.png`\n'
        '- `dashboard/figures/dashboard_page2.png`\n'
        '- `dashboard/figures/dashboard_page3.png`\n'
        '- `dashboard/figures/dashboard_page4.png`\n'
        '- `dashboard/dashboard_report.pdf`\n\n'
        '## Notes\n'
        '- These pages are designed to capture the key Day 5 dashboard story: industry overview, fund performance, investor analytics, SIP & market trends.\n'
        '- A `.pbix` file requires Power BI Desktop and cannot be generated from this environment.\n'
    )

print('Dashboard assets created in', DASHBOARD_DIR)
