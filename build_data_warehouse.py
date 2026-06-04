from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DB_PATH = Path("bluestock_mf.db")
SQL_DIR = Path("sql")

CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

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

NUMERIC_HINTS = (
    "amfi",
    "scheme_code",
    "amount",
    "aum",
    "nav",
    "return",
    "expense",
    "alpha",
    "beta",
    "sharpe",
    "sortino",
    "std_dev",
    "drawdown",
    "rating",
    "annual_income",
    "lakh",
    "crore",
    "pct",
)

TRANSACTION_TYPE_MAP = {
    "sip": "SIP",
    "s i p": "SIP",
    "s.i.p": "SIP",
    "sip ": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "lump_sum": "Lumpsum",
    "redemption": "Redemption",
}

KYC_STATUSES = {"verified", "pending"}


def normalize_column_name(column: object) -> str:
    value = str(column).strip().lower()
    value = value.replace("%", "pct")
    value = value.replace("&", "and")
    value = value.replace("/", "_")
    value = value.replace("-", "_")
    value = value.replace(" ", "_")
    value = re.sub(r"__+", "_", value)
    return value


def standardize_strings(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    object_columns = frame.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        frame[column] = frame[column].astype("string").str.strip()
        frame[column] = frame[column].replace({"": pd.NA, "nan": pd.NA, "none": pd.NA})
    return frame


def convert_dates(frame: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    frame = frame.copy()
    date_columns = DATE_COLUMNS.get(dataset_name, [])
    for column in date_columns:
        if column not in frame.columns:
            continue

        if column == "month":
            parsed = pd.to_datetime(frame[column].astype(str).str.strip(), errors="coerce")
            if parsed.isna().any():
                parsed = pd.to_datetime(frame[column].astype(str).str.strip() + "-01", errors="coerce")
            frame[column] = pd.to_datetime(parsed, errors="coerce").dt.date
        else:
            frame[column] = pd.to_datetime(frame[column], errors="coerce").dt.date

    return frame


def convert_numeric(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column in frame.columns:
        lower_column = column.lower()
        if any(hint in lower_column for hint in NUMERIC_HINTS):
            numeric = pd.to_numeric(frame[column], errors="coerce")
            if lower_column in {"amfi_code", "scheme_code", "min_sip_amount", "min_lumpsum_amount", "morningstar_rating", "num_schemes"}:
                if numeric.notna().all():
                    frame[column] = numeric.astype("Int64")
                else:
                    frame[column] = numeric
            else:
                frame[column] = numeric
    return frame


def clean_generic(frame: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [normalize_column_name(column) for column in frame.columns]
    frame = standardize_strings(frame)
    frame = convert_dates(frame, dataset_name)
    frame = convert_numeric(frame)
    frame = frame.drop_duplicates().reset_index(drop=True)
    return frame


def clean_nav_history(frame: pd.DataFrame) -> pd.DataFrame:
    frame = clean_generic(frame, "02_nav_history.csv")
    if "date" not in frame.columns or "amfi_code" not in frame.columns or "nav" not in frame.columns:
        raise ValueError("NAV history is missing required columns")

    frame = frame.loc[frame["date"].notna()].copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values(["amfi_code", "date"]) 
    frame = frame.drop_duplicates(subset=["amfi_code", "date"], keep="last")

    expanded = []
    for amfi_code, group in frame.groupby("amfi_code", sort=False):
        group = group.set_index("date").sort_index()
        full_index = pd.date_range(group.index.min(), group.index.max(), freq="D")
        group = group.reindex(full_index)
        group["amfi_code"] = amfi_code
        group["nav"] = group["nav"].ffill()
        group = group.loc[group["nav"].notna()].reset_index(drop=False)
        group = group.rename(columns={"index": "date"})
        expanded.append(group)

    frame = pd.concat(expanded, ignore_index=True)
    frame = frame.loc[frame["nav"] > 0].copy()
    frame["date"] = frame["date"].dt.date
    return frame.reset_index(drop=True)


def standardize_transaction_type(value: str | pd.NA) -> str | pd.NA:
    if pd.isna(value):
        return pd.NA
    normalized = re.sub(r"[^a-zA-Z]", " ", str(value).strip()).lower()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return TRANSACTION_TYPE_MAP.get(normalized, value.strip().title())


def standardize_kyc_status(value: str | pd.NA) -> str | pd.NA:
    if pd.isna(value):
        return pd.NA
    normalized = str(value).strip().lower()
    if normalized in KYC_STATUSES:
        return normalized.title()
    return pd.NA


def clean_investor_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    frame = clean_generic(frame, "08_investor_transactions.csv")
    required_columns = {"transaction_date", "amfi_code", "transaction_type", "amount_inr", "kyc_status"}
    missing = required_columns - set(frame.columns)
    if missing:
        raise ValueError(f"Investor transactions dataset is missing columns: {sorted(missing)}")

    frame = frame.loc[frame["transaction_date"].notna()].copy()
    frame["transaction_date"] = pd.to_datetime(frame["transaction_date"], errors="coerce")
    frame = frame.loc[frame["transaction_date"].notna()].copy()
    frame["transaction_date"] = frame["transaction_date"].dt.date
    frame["transaction_type"] = frame["transaction_type"].apply(standardize_transaction_type).astype("string")
    frame.loc[~frame["transaction_type"].isin(["SIP", "Lumpsum", "Redemption"]), "transaction_type"] = pd.NA
    frame["amount_inr"] = pd.to_numeric(frame["amount_inr"], errors="coerce")
    frame = frame.loc[frame["amount_inr"] > 0].copy()
    frame["kyc_status"] = frame["kyc_status"].apply(standardize_kyc_status).astype("string")
    return frame.reset_index(drop=True)


def clean_scheme_performance(frame: pd.DataFrame) -> pd.DataFrame:
    frame = clean_generic(frame, "07_scheme_performance.csv")
    fields_to_numeric = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]
    for column in fields_to_numeric:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    if "expense_ratio_pct" in frame.columns:
        frame["expense_ratio_within_expected"] = (
            frame["expense_ratio_pct"].between(0.1, 2.5, inclusive="both")
        )
    return frame.reset_index(drop=True)


def write_processed_csv(name: str, frame: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / name
    frame.to_csv(output_path, index=False)
    print(f"Saved cleaned dataset: {output_path}")


def clean_all_datasets() -> dict[str, pd.DataFrame]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned: dict[str, pd.DataFrame] = {}
    for filename in CSV_FILES:
        path = RAW_DIR / filename
        frame = pd.read_csv(path)
        if filename == "02_nav_history.csv":
            cleaned_frame = clean_nav_history(frame)
        elif filename == "08_investor_transactions.csv":
            cleaned_frame = clean_investor_transactions(frame)
        elif filename == "07_scheme_performance.csv":
            cleaned_frame = clean_scheme_performance(frame)
        else:
            cleaned_frame = clean_generic(frame, filename)
        write_processed_csv(filename, cleaned_frame)
        cleaned[filename] = cleaned_frame
    return cleaned


def clean_table_name(filename: str) -> str:
    stem = Path(filename).stem
    stem = stem.lstrip("0123456789_-")
    return normalize_column_name(stem)


def create_dim_date(frame_by_name: dict[str, pd.DataFrame]) -> pd.DataFrame:
    date_values = []
    for name, frame in frame_by_name.items():
        for date_column in DATE_COLUMNS.get(name, []):
            if date_column in frame.columns:
                dates = pd.to_datetime(frame[date_column], errors="coerce").dropna().dt.date
                date_values.append(dates)
    if not date_values:
        raise ValueError("No date values found to build dim_date")
    dates = pd.concat(date_values).drop_duplicates().sort_values().reset_index(drop=True)
    dim_date = pd.DataFrame({
        "date": dates,
        "year": dates.map(lambda x: x.year),
        "quarter": dates.map(lambda x: f"Q{((x.month - 1) // 3) + 1}"),
        "month": dates.map(lambda x: x.month),
        "month_name": dates.map(lambda x: x.strftime("%B")),
        "day": dates.map(lambda x: x.day),
        "weekday": dates.map(lambda x: x.strftime("%A")),
        "is_weekend": dates.map(lambda x: x.weekday() >= 5),
    })
    dim_date.insert(0, "date_id", range(1, len(dim_date) + 1))
    return dim_date


def load_cleaned_csvs_to_sqlite(engine, cleaned_frames: dict[str, pd.DataFrame]) -> dict[str, int]:
    row_counts: dict[str, int] = {}
    for filename, frame in cleaned_frames.items():
        table_name = clean_table_name(filename)
        frame.to_sql(table_name, con=engine, if_exists="replace", index=False)
        row_counts[table_name] = len(frame)
        print(f"Loaded {len(frame):,} rows into SQLite table `{table_name}`")
    return row_counts


def load_star_schema(engine, cleaned_frames: dict[str, pd.DataFrame]) -> None:
    schema_sql = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")
    with engine.begin() as conn:
        for table_name in ["fact_aum", "fact_performance", "fact_transactions", "fact_nav", "dim_fund", "dim_date"]:
            conn.exec_driver_sql(f"DROP TABLE IF EXISTS {table_name}")
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            conn.exec_driver_sql(statement)

    dim_date = create_dim_date(cleaned_frames)
    dim_date.to_sql("dim_date", con=engine, if_exists="append", index=False)

    fund_master = cleaned_frames["01_fund_master.csv"].copy()
    fund_master = fund_master.rename(columns={
        "scheme_name": "scheme_name",
        "fund_house": "fund_house",
        "category": "category",
        "sub_category": "sub_category",
        "plan": "plan",
        "launch_date": "launch_date",
        "benchmark": "benchmark",
        "risk_category": "risk_category",
        "expense_ratio_pct": "expense_ratio_pct",
        "exit_load_pct": "exit_load_pct",
        "min_sip_amount": "min_sip_amount",
        "min_lumpsum_amount": "min_lumpsum_amount",
        "fund_manager": "fund_manager",
        "sebi_category_code": "sebi_category_code",
    })
    fund_master = fund_master[sorted(set(["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "plan", "launch_date", "benchmark", "risk_category", "expense_ratio_pct", "exit_load_pct", "min_sip_amount", "min_lumpsum_amount", "fund_manager", "sebi_category_code"]))]
    fund_master.to_sql("dim_fund", con=engine, if_exists="append", index=False)

    nav = cleaned_frames["02_nav_history.csv"].copy()
    nav = nav.rename(columns={"date": "transaction_date"})
    nav["date"] = pd.to_datetime(nav["transaction_date"], errors="coerce").dt.date
    nav = nav.merge(dim_date[["date_id", "date"]], on="date", how="left")
    fact_nav = nav[["amfi_code", "date_id", "nav"]].copy()
    fact_nav.to_sql("fact_nav", con=engine, if_exists="append", index=False)

    transactions = cleaned_frames["08_investor_transactions.csv"].copy()
    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"], errors="coerce").dt.date
    transactions = transactions.merge(dim_date[["date_id", "date"]], left_on="transaction_date", right_on="date", how="left")
    fact_transactions = transactions[
        [
            "investor_id",
            "transaction_date",
            "date_id",
            "amfi_code",
            "transaction_type",
            "amount_inr",
            "state",
            "city",
            "city_tier",
            "age_group",
            "gender",
            "annual_income_lakh",
            "payment_mode",
            "kyc_status",
        ]
    ].copy()
    fact_transactions.to_sql("fact_transactions", con=engine, if_exists="append", index=False)

    performance = cleaned_frames["07_scheme_performance.csv"].copy()
    performance = performance[
        [
            "amfi_code",
            "return_1yr_pct",
            "return_3yr_pct",
            "return_5yr_pct",
            "benchmark_3yr_pct",
            "alpha",
            "beta",
            "sharpe_ratio",
            "sortino_ratio",
            "std_dev_ann_pct",
            "max_drawdown_pct",
            "aum_crore",
            "expense_ratio_pct",
            "expense_ratio_within_expected",
            "morningstar_rating",
            "risk_grade",
        ]
    ].copy()
    performance.to_sql("fact_performance", con=engine, if_exists="append", index=False)

    aum = cleaned_frames["03_aum_by_fund_house.csv"].copy()
    aum["date"] = pd.to_datetime(aum["date"], errors="coerce").dt.date
    aum = aum.merge(dim_date[["date_id", "date"]], on="date", how="left")
    fact_aum = aum[["date_id", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]].copy()
    fact_aum.to_sql("fact_aum", con=engine, if_exists="append", index=False)

    print("Star schema tables created and loaded into SQLite.")


def verify_row_counts(engine, cleaned_frames: dict[str, pd.DataFrame]) -> dict[str, tuple[int, int]]:
    verification = {}
    with engine.connect() as conn:
        for filename, frame in cleaned_frames.items():
            table_name = clean_table_name(filename)
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            db_count = result.scalar_one()
            verification[table_name] = (len(frame), db_count)
    return verification


def main() -> None:
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_frames = clean_all_datasets()

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON;")

    load_cleaned_csvs_to_sqlite(engine, cleaned_frames)

    if not (SQL_DIR / "schema.sql").exists():
        raise FileNotFoundError("schema.sql not found in sql/ directory")

    load_star_schema(engine, cleaned_frames)

    verification = verify_row_counts(engine, cleaned_frames)
    print("\nRow count verification for cleaned raw tables:")
    for table_name, (source_count, db_count) in verification.items():
        print(f"- {table_name}: source={source_count:,}, sqlite={db_count:,}")

    print(f"\nBuilt SQLite database at {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()
