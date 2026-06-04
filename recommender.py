import argparse
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PERF_PATH = BASE_DIR / "data" / "processed" / "07_scheme_performance.csv"

RISK_MAP = {
    "low": ["Low", "Low to Moderate", "Moderate"],
    "moderate": ["Moderate", "Low to Moderate", "High"],
    "high": ["High", "Aggressive", "Very High"],
}


def normalize_risk(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().title()


def get_allowed_risks(appetite: str):
    appetite = appetite.strip().lower()
    if appetite not in RISK_MAP:
        raise ValueError(f"Unsupported risk appetite: {appetite}. Choose Low, Moderate, or High.")
    return RISK_MAP[appetite]


def recommend(appetite: str, top_n: int = 3):
    df = pd.read_csv(PERF_PATH)
    df["risk_grade"] = df["risk_grade"].astype(str).apply(normalize_risk)
    allowed = get_allowed_risks(appetite)
    matching = df[df["risk_grade"].isin(allowed)].copy()

    if matching.empty:
        raise ValueError(f"No funds found for risk appetite '{appetite}'.")

    recommendations = matching.sort_values("sharpe_ratio", ascending=False).head(top_n)
    print(f"Top {top_n} fund recommendations for '{appetite.title()}' risk appetite:\n")
    print(recommendations[["scheme_name", "fund_house", "category", "risk_grade", "sharpe_ratio", "return_3yr_pct", "aum_crore"]].to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend top funds by risk appetite using Sharpe ratio.")
    parser.add_argument("risk_appetite", choices=["Low", "Moderate", "High"], help="Risk appetite: Low, Moderate, or High")
    parser.add_argument("--top", type=int, default=3, help="Number of top funds to recommend")
    args = parser.parse_args()
    recommend(args.risk_appetite, top_n=args.top)
