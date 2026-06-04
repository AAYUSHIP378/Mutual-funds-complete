from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")
REPORT_PATH = REPORTS_DIR / "day2_cleaning_summary.md"

DATE_COLUMNS = {
    "01_fund_master.csv": ["launch_date"],
    "02_nav_history.csv": ["date"],
    "03_aum_by_fund_house.csv": ["date"],
    "04_monthly_sip_inflows.csv": ["month"],
    "05_category_inflows.csv": ["month"],
    "06_industry_folio_count.csv": ["month"],
    "08_investor_transactions.csv": ["transaction_date"],
    "09_portfolio_holdings.csv": ["portfolio_date"],
    "10_benchmark_indices.csv": ["date"],
}

INTEGER_COLUMNS = {
    "amfi_code",
    "scheme_code",
    "min_sip_amount",
    "min_lumpsum_amount",
    "aum_crore",
    "num_schemes",
    "sip_inflow_crore",
    "amount_inr",
    "morningstar_rating",
}

NUMERIC_HINTS = (
    "_pct",
    "_crore",
    "_lakh",
    "_cr",
    "_inr",
    "nav",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "close_value",
    "current_price",
    "weight",
)


def clean_column_name(column: object) -> str:
    return (
        str(column)
        .strip()
        .lower()
        .replace("%", "pct")
        .replace("&", "and")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def read_raw_csv(path: Path) -> pd.DataFrame:
    if path.read_bytes()[:4] == b"%PDF":
        raise ValueError("PDF content found in a CSV-named file")
    return pd.read_csv(path)


def standardize_strings(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    object_columns = frame.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return frame


def convert_dates(frame: pd.DataFrame, dataset_name: str) -> tuple[pd.DataFrame, list[str]]:
    frame = frame.copy()
    notes: list[str] = []
    inferred_columns = [
        column
        for column in frame.columns
        if column == "date"
        or column == "month"
        or column.endswith("_date")
    ]
    date_columns = list(dict.fromkeys([*DATE_COLUMNS.get(dataset_name, []), *inferred_columns]))

    for column in date_columns:
        if column not in frame.columns:
            notes.append(f"Expected date column `{column}` was not found.")
            continue

        if column == "month":
            parsed = pd.to_datetime(frame[column].astype("string") + "-01", errors="coerce")
        else:
            parsed = pd.to_datetime(frame[column], format="mixed", dayfirst=True, errors="coerce")

        invalid_count = int(parsed.isna().sum() - frame[column].isna().sum())
        frame[column] = parsed.dt.date.astype("string")
        if invalid_count:
            notes.append(f"`{column}` has {invalid_count} invalid date values converted to missing.")
    return frame, notes


def convert_numeric(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    frame = frame.copy()
    notes: list[str] = []
    for column in frame.columns:
        should_convert = column in INTEGER_COLUMNS or any(hint in column for hint in NUMERIC_HINTS)
        if not should_convert:
            continue

        original_missing = int(frame[column].isna().sum())
        numeric = pd.to_numeric(frame[column], errors="coerce")
        introduced_missing = int(numeric.isna().sum()) - original_missing
        if column in INTEGER_COLUMNS and introduced_missing == 0:
            frame[column] = numeric.astype("Int64")
        else:
            frame[column] = numeric
        if introduced_missing:
            notes.append(f"`{column}` has {introduced_missing} non-numeric values converted to missing.")
    return frame, notes


def summarize_quality(dataset_name: str, raw: pd.DataFrame, clean: pd.DataFrame) -> list[str]:
    notes: list[str] = []
    duplicate_rows = int(clean.duplicated().sum())
    missing_cells = int(clean.isna().sum().sum())

    notes.append(f"Raw shape: {raw.shape[0]:,} rows x {raw.shape[1]:,} columns")
    notes.append(f"Processed shape: {clean.shape[0]:,} rows x {clean.shape[1]:,} columns")
    notes.append(f"Duplicate rows: {duplicate_rows:,}")
    notes.append(f"Missing cells after cleaning: {missing_cells:,}")

    if "amfi_code" in clean.columns:
        missing_codes = int(clean["amfi_code"].isna().sum())
        notes.append(f"Missing AMFI codes: {missing_codes:,}")

    if "scheme_code" in clean.columns:
        missing_codes = int(clean["scheme_code"].isna().sum())
        notes.append(f"Missing scheme codes: {missing_codes:,}")

    if {"requested_scheme_name", "meta_scheme_name"}.issubset(clean.columns):
        requested_tokens = clean["requested_scheme_name"].dropna().astype(str).str.split().str[0].str.lower()
        meta_names = clean.loc[requested_tokens.index, "meta_scheme_name"].fillna("").astype(str).str.lower()
        metadata_mismatches = sum(
            1 for token, meta in zip(requested_tokens, meta_names) if token not in meta
        )
        notes.append(f"Rows where requested scheme name does not match API metadata: {metadata_mismatches:,}")

    positive_checks = {
        "nav": "NAV",
        "amount_inr": "transaction amount",
        "aum_crore": "AUM",
        "close_value": "benchmark close",
        "current_price_inr": "stock price",
    }
    for column, label in positive_checks.items():
        if column in clean.columns:
            invalid = int((clean[column].dropna() <= 0).sum())
            notes.append(f"Non-positive {label} values: {invalid:,}")

    if dataset_name == "04_monthly_sip_inflows.csv" and "yoy_growth_pct" in clean.columns:
        missing_yoy = int(clean["yoy_growth_pct"].isna().sum())
        notes.append(f"Missing YoY growth values: {missing_yoy:,} expected for initial baseline months.")

    if "weight_pct" in clean.columns:
        invalid_weight = int(((clean["weight_pct"].dropna() < 0) | (clean["weight_pct"].dropna() > 100)).sum())
        notes.append(f"Portfolio weights outside 0-100 pct: {invalid_weight:,}")

    return notes


def clean_dataset(path: Path) -> tuple[pd.DataFrame | None, list[str]]:
    try:
        raw = read_raw_csv(path)
    except Exception as error:
        return None, [f"Skipped `{path.name}`: {error}"]

    clean = raw.copy()
    clean.columns = [clean_column_name(column) for column in clean.columns]
    clean = standardize_strings(clean)
    clean, date_notes = convert_dates(clean, path.name)
    clean, numeric_notes = convert_numeric(clean)
    all_null_columns = [column for column in clean.columns if clean[column].isna().all()]
    if all_null_columns:
        clean = clean.drop(columns=all_null_columns)
    clean = clean.drop_duplicates().reset_index(drop=True)

    output_path = PROCESSED_DIR / path.name
    clean.to_csv(output_path, index=False)

    notes = summarize_quality(path.name, raw, clean)
    if all_null_columns:
        notes.append(f"Dropped all-null columns: {', '.join(all_null_columns)}")
    notes.extend(date_notes)
    notes.extend(numeric_notes)
    notes.append(f"Saved processed file: `{output_path.as_posix()}`")
    return clean, notes


def create_joined_outputs(datasets: dict[str, pd.DataFrame]) -> list[str]:
    notes: list[str] = []
    fund_master = datasets.get("01_fund_master.csv")
    nav_history = datasets.get("02_nav_history.csv")
    transactions = datasets.get("08_investor_transactions.csv")
    holdings = datasets.get("09_portfolio_holdings.csv")

    if fund_master is not None and nav_history is not None:
        fund_nav = nav_history.merge(
            fund_master[
                [
                    "amfi_code",
                    "fund_house",
                    "scheme_name",
                    "category",
                    "sub_category",
                    "plan",
                    "risk_category",
                    "benchmark",
                ]
            ],
            on="amfi_code",
            how="left",
            validate="many_to_one",
        )
        missing_master = int(fund_nav["scheme_name"].isna().sum())
        output_path = PROCESSED_DIR / "fund_nav_history_enriched.csv"
        fund_nav.to_csv(output_path, index=False)
        notes.append(f"Created `{output_path.as_posix()}` with {len(fund_nav):,} rows.")
        notes.append(f"NAV rows missing fund master details after join: {missing_master:,}")

    if fund_master is not None and transactions is not None:
        transaction_enriched = transactions.merge(
            fund_master[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "risk_category"]],
            on="amfi_code",
            how="left",
            validate="many_to_one",
        )
        output_path = PROCESSED_DIR / "investor_transactions_enriched.csv"
        transaction_enriched.to_csv(output_path, index=False)
        notes.append(f"Created `{output_path.as_posix()}` with {len(transaction_enriched):,} rows.")

    if fund_master is not None and holdings is not None:
        holdings_enriched = holdings.merge(
            fund_master[["amfi_code", "fund_house", "scheme_name", "category", "sub_category"]],
            on="amfi_code",
            how="left",
            validate="many_to_one",
        )
        output_path = PROCESSED_DIR / "portfolio_holdings_enriched.csv"
        holdings_enriched.to_csv(output_path, index=False)
        notes.append(f"Created `{output_path.as_posix()}` with {len(holdings_enriched):,} rows.")

    return notes


def validate_relationships(datasets: dict[str, pd.DataFrame]) -> list[str]:
    notes: list[str] = []
    fund_master = datasets.get("01_fund_master.csv")
    if fund_master is None or "amfi_code" not in fund_master.columns:
        return ["Fund master relationship checks skipped because AMFI code was unavailable."]

    master_codes = set(fund_master["amfi_code"].dropna().astype(str))
    for dataset_name, frame in datasets.items():
        if dataset_name == "01_fund_master.csv" or "amfi_code" not in frame.columns:
            continue
        codes = set(frame["amfi_code"].dropna().astype(str))
        unknown_codes = sorted(codes - master_codes)
        notes.append(f"`{dataset_name}` AMFI codes not in fund master: {len(unknown_codes):,}")
        if unknown_codes:
            notes.append(f"Sample unknown codes: {', '.join(unknown_codes[:10])}")
    return notes


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    datasets: dict[str, pd.DataFrame] = {}
    report_lines = ["# Day 2 Cleaning Summary", ""]

    for path in sorted(RAW_DIR.glob("*.csv")):
        clean, notes = clean_dataset(path)
        report_lines.extend([f"## {path.name}", *[f"- {note}" for note in notes], ""])
        if clean is not None:
            datasets[path.name] = clean

    relationship_notes = validate_relationships(datasets)
    joined_notes = create_joined_outputs(datasets)

    report_lines.extend(["## Relationship Validation", *[f"- {note}" for note in relationship_notes], ""])
    report_lines.extend(["## Enriched Outputs", *[f"- {note}" for note in joined_notes], ""])
    report_lines.extend(
        [
            "## SQL Schema",
            "- Added `sql/day2_schema.sql` for database-ready table definitions and core keys.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote Day 2 cleaning summary -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
