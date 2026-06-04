"""Day 8 Bonus Challenge 3: Monte Carlo Simulation for NAV Projection

Projects NAV growth over 5 years with uncertainty bands using Monte Carlo methods.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = BASE_DIR / "monte_carlo_projection.png"

NAV = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"]).sort_values(["amfi_code", "date"])
PERF = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")

# Select top 5 funds by Sharpe ratio
top_funds = PERF.nlargest(5, "sharpe_ratio")
selected_codes = top_funds["amfi_code"].tolist()

def monte_carlo_simulation(nav_series, annual_return, annual_volatility, years=5, simulations=1000):
    """
    Simulate future NAV values using geometric Brownian motion.
    
    dS_t = μ * S_t * dt + σ * S_t * dW_t
    """
    trading_days = 252
    dt = 1 / trading_days
    daily_return = annual_return / trading_days
    daily_vol = annual_volatility / np.sqrt(trading_days)
    
    S0 = nav_series.iloc[-1]
    T = years * trading_days
    
    paths = np.zeros((int(T), simulations))
    paths[0, :] = S0
    
    for t in range(1, int(T)):
        Z = np.random.standard_normal(simulations)
        paths[t, :] = paths[t-1, :] * np.exp((daily_return - 0.5 * daily_vol**2) * dt + daily_vol * np.sqrt(dt) * Z)
    
    return paths

# Run simulations for top 5 funds
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for idx, code in enumerate(selected_codes[:6]):
    ax = axes[idx]
    fund_nav = NAV[NAV["amfi_code"] == code]["nav"].dropna()
    fund_name = PERF[PERF["amfi_code"] == code]["scheme_name"].squeeze()
    
    annual_return = PERF[PERF["amfi_code"] == code]["return_3yr_pct"].squeeze() / 100 / 3
    annual_volatility = PERF[PERF["amfi_code"] == code]["std_dev_ann_pct"].squeeze() / 100
    
    paths = monte_carlo_simulation(fund_nav, annual_return, annual_volatility, years=5, simulations=500)
    
    # Calculate quantiles
    percentile_5 = np.percentile(paths, 5, axis=1)
    percentile_25 = np.percentile(paths, 25, axis=1)
    percentile_50 = np.percentile(paths, 50, axis=1)
    percentile_75 = np.percentile(paths, 75, axis=1)
    percentile_95 = np.percentile(paths, 95, axis=1)
    
    days = np.arange(paths.shape[0])
    
    ax.fill_between(days, percentile_5, percentile_95, alpha=0.2, color='blue', label='5%-95%')
    ax.fill_between(days, percentile_25, percentile_75, alpha=0.3, color='blue', label='25%-75%')
    ax.plot(days, percentile_50, color='darkblue', linewidth=2, label='Median')
    ax.axhline(y=fund_nav.iloc[-1], color='red', linestyle='--', label='Current')
    
    ax.set_title(f"{fund_name}", fontsize=10, weight='bold')
    ax.set_xlabel("Trading Days")
    ax.set_ylabel("NAV")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

if len(selected_codes) < 6:
    axes[-1].axis('off')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
print(f"Monte Carlo projection saved: {OUTPUT_PATH}")

# Summary statistics
print("\n5-Year NAV Projection Summary (Top 5 Funds):")
print("=" * 80)
for code in selected_codes:
    fund_name = PERF[PERF["amfi_code"] == code]["scheme_name"].squeeze()
    fund_nav = NAV[NAV["amfi_code"] == code]["nav"].dropna()
    annual_return = PERF[PERF["amfi_code"] == code]["return_3yr_pct"].squeeze() / 100 / 3
    
    paths = monte_carlo_simulation(fund_nav, annual_return, 0.15, years=5, simulations=1000)
    final_nav = paths[-1, :]
    
    print(f"\n{fund_name}")
    print(f"  Current NAV: ₹{fund_nav.iloc[-1]:.2f}")
    print(f"  5-Year Median: ₹{np.percentile(final_nav, 50):.2f}")
    print(f"  5-Year 25-75%: ₹{np.percentile(final_nav, 25):.2f} - ₹{np.percentile(final_nav, 75):.2f}")
    print(f"  5-Year 5-95%: ₹{np.percentile(final_nav, 5):.2f} - ₹{np.percentile(final_nav, 95):.2f}")
