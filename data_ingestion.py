from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
REPORTS_DIR = Path("reports")
REPORT_PATH = REPORTS_DIR / "day1_data_quality_summary.md"


def read_csv(path: Path) -> pd.DataFrame:
    if path.read_bytes()[:4] == b"%PDF":
        raise ValueError("File has PDF content, not CSV content")

    encodings = ["utf-8", "utf-8-sig", "latin1"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error
    raise RuntimeError(f"Could not read {path} with supported encodings") from last_error


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in frame.columns
    ]
    return frame


def likely_code_columns(frame: pd.DataFrame) -> list[str]:
    return [
        column
        for column in frame.columns
        if "scheme_code" in column
        or column in {"code", "amfi_code", "amfi_scheme_code", "schemeid", "scheme_id"}
    ]


def find_dataset(datasets: dict[str, pd.DataFrame], required_terms: list[str]) -> tuple[str, pd.DataFrame] | None:
    for name, frame in datasets.items():
        haystack = f"{name} {' '.join(frame.columns)}".lower()
        if all(term in haystack for term in required_terms):
            return name, frame
    return None


def summarize_anomalies(name: str, frame: pd.DataFrame) -> list[str]:
    anomalies: list[str] = []
    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        anomalies.append(f"{duplicate_rows} duplicate rows")

    empty_columns = [column for column in frame.columns if frame[column].isna().all()]
    if empty_columns:
        anomalies.append(f"all-null columns: {', '.join(empty_columns)}")

    unnamed_columns = [column for column in frame.columns if str(column).lower().startswith("unnamed")]
    if unnamed_columns:
        anomalies.append(f"unnamed index-like columns: {', '.join(map(str, unnamed_columns))}")

    missing_rates = frame.isna().mean().sort_values(ascending=False)
    high_missing = missing_rates[missing_rates >= 0.50]
    if not high_missing.empty:
        details = ", ".join(f"{column}={rate:.0%}" for column, rate in high_missing.items())
        anomalies.append(f"high missingness: {details}")

    if not anomalies:
        anomalies.append("No obvious structural anomalies detected")
    return anomalies


def print_profile(name: str, frame: pd.DataFrame) -> list[str]:
    print("\n" + "=" * 100)
    print(f"Dataset: {name}")
    print(f"Shape: {frame.shape}")
    print("\nDtypes:")
    print(frame.dtypes)
    print("\nHead:")
    print(frame.head())
    anomalies = summarize_anomalies(name, frame)
    print("\nAnomalies:")
    for anomaly in anomalies:
        print(f"- {anomaly}")
    return anomalies


def explore_fund_master(master_name: str, master: pd.DataFrame) -> list[str]:
    lines = [f"## Fund Master Exploration ({master_name})", ""]
    candidate_columns = {
        "fund houses": ["fund_house", "amc", "amc_name", "fundhouse", "fund_house_name"],
        "categories": ["category", "scheme_category", "asset_class"],
        "sub-categories": ["sub_category", "subcategory", "scheme_sub_category", "sub_category_name"],
        "risk grades": ["risk_grade", "risk_category", "risk", "riskometer", "risk_level"],
    }

    normalized = normalize_columns(master)
    for label, candidates in candidate_columns.items():
        column = next((candidate for candidate in candidates if candidate in normalized.columns), None)
        if column is None:
            message = f"No obvious {label} column found"
            print(message)
            lines.append(f"- {message}")
            continue
        values = sorted(normalized[column].dropna().astype(str).str.strip().unique())
        print(f"\nUnique {label} ({column}):")
        print(values)
        lines.append(f"- Unique {label} from `{column}`: {len(values)} values")
        lines.append(f"  Sample: {', '.join(values[:20]) if values else 'None'}")

    code_columns = likely_code_columns(normalized)
    if code_columns:
        code_column = code_columns[0]
        lengths = normalized[code_column].dropna().astype(str).str.extract(r"(\d+)")[0].str.len()
        distribution = lengths.value_counts(dropna=False).sort_index().to_dict()
        lines.extend(
            [
                "",
                "### AMFI Scheme Code Structure",
                f"- AMFI scheme codes are numeric identifiers for mutual fund schemes. In this dataset, `{code_column}` length distribution is {distribution}.",
                "- These codes are used as stable join keys between fund master records and NAV history/API data.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "### AMFI Scheme Code Structure",
                "- No obvious AMFI scheme code column was found in the fund master dataset.",
            ]
        )
    return lines


def validate_amfi_codes(datasets: dict[str, pd.DataFrame]) -> list[str]:
    master_match = find_dataset(datasets, ["fund", "master"])
    nav_match = find_dataset(datasets, ["nav"])
    lines = ["## AMFI Code Validation", ""]

    if master_match is None or nav_match is None:
        lines.append("- Could not run full validation because fund master or NAV history was not confidently identified.")
        print("\nAMFI validation skipped: fund_master or nav_history dataset not found.")
        return lines

    master_name, master = master_match
    nav_name, nav_history = nav_match
    master_norm = normalize_columns(master)
    nav_norm = normalize_columns(nav_history)

    master_code_columns = likely_code_columns(master_norm)
    nav_code_columns = likely_code_columns(nav_norm)
    if not master_code_columns or not nav_code_columns:
        lines.append("- Could not run full validation because a scheme code column was missing.")
        print("\nAMFI validation skipped: scheme code column missing.")
        return lines

    master_code_column = master_code_columns[0]
    nav_code_column = nav_code_columns[0]
    master_codes = set(master_norm[master_code_column].dropna().astype(str).str.extract(r"(\d+)")[0].dropna())
    nav_codes = set(nav_norm[nav_code_column].dropna().astype(str).str.extract(r"(\d+)")[0].dropna())
    missing_codes = sorted(master_codes - nav_codes)

    lines.extend(
        [
            f"- Fund master dataset: `{master_name}` using `{master_code_column}`",
            f"- NAV history dataset: `{nav_name}` using `{nav_code_column}`",
            f"- Fund master unique AMFI codes: {len(master_codes):,}",
            f"- NAV history unique AMFI codes: {len(nav_codes):,}",
            f"- Fund master codes missing from NAV history: {len(missing_codes):,}",
        ]
    )
    if missing_codes:
        lines.append(f"- Missing code sample: {', '.join(missing_codes[:25])}")
    else:
        lines.append("- Result: every fund master AMFI code exists in NAV history.")

    print("\nAMFI Code Validation:")
    for line in lines[2:]:
        print(line)

    lines.extend(["", *explore_fund_master(master_name, master)])
    return lines


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_paths = sorted(
        path for path in RAW_DIR.glob("*.csv") if not path.name.startswith("live_nav_")
    )
    if not csv_paths:
        raise FileNotFoundError(f"No provided CSV files found in {RAW_DIR.resolve()}")

    datasets: dict[str, pd.DataFrame] = {}
    report_lines = ["# Day 1 Data Quality Summary", ""]

    for path in csv_paths:
        try:
            frame = read_csv(path)
        except Exception as error:
            message = f"Skipped `{path.name}`: {error}"
            print(f"\n{message}")
            report_lines.extend([f"## {path.name}", f"- Anomaly: {message}", ""])
            continue

        datasets[path.name] = frame
        anomalies = print_profile(path.name, frame)
        report_lines.extend(
            [
                f"## {path.name}",
                f"- Shape: {frame.shape[0]:,} rows x {frame.shape[1]:,} columns",
                f"- Columns: {', '.join(map(str, frame.columns))}",
                f"- Anomalies: {'; '.join(anomalies)}",
                "",
            ]
        )

    report_lines.extend(validate_amfi_codes(datasets))
    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\nWrote data quality summary -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
