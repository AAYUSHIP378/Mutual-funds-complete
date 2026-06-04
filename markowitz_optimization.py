"""Day 8 Bonus Challenge 4: Markowitz Efficient Frontier Portfolio Optimization

Computes the efficient frontier for 5 selected funds and identifies the optimal portfolio.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = BASE_DIR / "efficient_frontier.png"

NAV = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv", parse_dates=["date"]).sort_values(["amfi_code", "date"])
PERF = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")

# Select top 5 funds by Sharpe ratio
top_funds = PERF.nlargest(5, "sharpe_ratio")
selected_codes = top_funds["amfi_code"].tolist()

# Compute daily returns
returns_dict = {}
for code in selected_codes:
    fund_nav = NAV[NAV["amfi_code"] == code].sort_values("date")
    daily_returns = fund_nav["nav"].pct_change().dropna()
    returns_dict[code] = daily_returns.values

# Create returns DataFrame
returns_df = pd.DataFrame(returns_dict)
returns_df.columns = [PERF[PERF["amfi_code"] == c]["scheme_name"].squeeze() for c in selected_codes]

# Compute correlation and covariance
cov_matrix = returns_df.cov() * 252  # Annualized
mean_returns = returns_df.mean() * 252  # Annualized

# Portfolio metrics
def portfolio_return(weights):
    return np.sum(mean_returns * weights)

def portfolio_volatility(weights):
    return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

def negative_sharpe(weights, rf=0.065):
    p_ret = portfolio_return(weights)
    p_vol = portfolio_volatility(weights)
    return -(p_ret - rf) / p_vol

# Generate efficient frontier
n_portfolios = 100
frontier_returns = []
frontier_volatilities = []
frontier_weights = []

# Random portfolios for frontier
for i in range(n_portfolios):
    target_return = np.linspace(mean_returns.min(), mean_returns.max(), n_portfolios)[i]
    
    constraints = (
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # weights sum to 1
        {"type": "eq", "fun": lambda w: portfolio_return(w) - target_return},  # target return
    )
    bounds = tuple((0, 1) for _ in selected_codes)
    init_guess = np.array([1/len(selected_codes)] * len(selected_codes))
    
    result = minimize(
        portfolio_volatility,
        init_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
    )
    
    if result.success:
        frontier_returns.append(portfolio_return(result.x))
        frontier_volatilities.append(portfolio_volatility(result.x))
        frontier_weights.append(result.x)

# Find optimal portfolio (maximum Sharpe)
rf = 0.065
constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
bounds = tuple((0, 1) for _ in selected_codes)
init_guess = np.array([1/len(selected_codes)] * len(selected_codes))
result_optimal = minimize(
    negative_sharpe,
    init_guess,
    args=(rf,),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints,
)

optimal_weights = result_optimal.x
optimal_return = portfolio_return(optimal_weights)
optimal_volatility = portfolio_volatility(optimal_weights)
optimal_sharpe = (optimal_return - rf) / optimal_volatility

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Efficient frontier
ax1.scatter(frontier_volatilities, frontier_returns, alpha=0.5, s=50, label='Frontier')
ax1.scatter([optimal_volatility], [optimal_return], color='red', s=200, marker='*', label='Optimal Portfolio', zorder=5)

# Individual funds
for i, code in enumerate(selected_codes):
    fund_name = PERF[PERF["amfi_code"] == code]["scheme_name"].squeeze()
    fund_ret = mean_returns.iloc[i]
    fund_vol = np.sqrt(cov_matrix.iloc[i, i])
    ax1.scatter(fund_vol, fund_ret, s=100, alpha=0.7)
    ax1.annotate(fund_name, (fund_vol, fund_ret), fontsize=8)

ax1.set_xlabel('Volatility (Annual)')
ax1.set_ylabel('Return (Annual)')
ax1.set_title('Markowitz Efficient Frontier')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Portfolio allocation
ax2.pie(optimal_weights, labels=returns_df.columns, autopct='%1.1f%%')
ax2.set_title('Optimal Portfolio Allocation')

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
print(f"Efficient frontier saved: {OUTPUT_PATH}")

# Output summary
print("\nMarkowitz Portfolio Optimization Results:")
print("=" * 80)
print("\nOptimal Portfolio Allocation:")
for fund_name, weight in zip(returns_df.columns, optimal_weights):
    print(f"  {fund_name}: {weight*100:.2f}%")

print(f"\nOptimal Portfolio Metrics:")
print(f"  Expected Annual Return: {optimal_return*100:.2f}%")
print(f"  Annual Volatility: {optimal_volatility*100:.2f}%")
print(f"  Sharpe Ratio: {optimal_sharpe:.2f}")

print(f"\nIndividual Fund Metrics:")
for i, code in enumerate(selected_codes):
    fund_name = PERF[PERF["amfi_code"] == code]["scheme_name"].squeeze()
    fund_sharpe = (mean_returns.iloc[i] - rf) / np.sqrt(cov_matrix.iloc[i, i])
    print(f"  {fund_name}: Return={mean_returns.iloc[i]*100:.2f}%, Vol={np.sqrt(cov_matrix.iloc[i, i])*100:.2f}%, Sharpe={fund_sharpe:.2f}")
