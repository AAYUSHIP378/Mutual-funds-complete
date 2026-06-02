from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


RAW_DIR = Path("data/raw")
MFAPI_URL = "https://api.mfapi.in/mf/{scheme_code}"

SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}


def _slug(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace("-", " ")
        .replace(" ", "_")
        .replace("__", "_")
    )


def fetch_scheme_nav(scheme_code: str, scheme_name: str) -> pd.DataFrame:
    response = requests.get(MFAPI_URL.format(scheme_code=scheme_code), timeout=60)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    meta = payload.get("meta", {})
    rows = payload.get("data", [])
    frame = pd.DataFrame(rows)

    if frame.empty:
        return pd.DataFrame(
            [
                {
                    "scheme_code": scheme_code,
                    "requested_scheme_name": scheme_name,
                    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            ]
        )

    frame.insert(0, "scheme_code", scheme_code)
    frame.insert(1, "requested_scheme_name", scheme_name)
    for key, value in meta.items():
        frame[f"meta_{key}"] = value
    frame["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    return frame


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    latest_rows = []

    for scheme_code, scheme_name in SCHEMES.items():
        frame = fetch_scheme_nav(scheme_code, scheme_name)
        output_path = RAW_DIR / f"live_nav_{scheme_code}_{_slug(scheme_name)}.csv"
        frame.to_csv(output_path, index=False)
        print(f"Saved {len(frame):,} NAV rows for {scheme_name} ({scheme_code}) -> {output_path}")
        latest_rows.append(frame.head(1))

    latest_frame = pd.concat(latest_rows, ignore_index=True)
    latest_path = RAW_DIR / "live_nav_latest_key_schemes.csv"
    latest_frame.to_csv(latest_path, index=False)
    print(f"Saved latest NAV snapshot -> {latest_path}")


if __name__ == "__main__":
    main()
