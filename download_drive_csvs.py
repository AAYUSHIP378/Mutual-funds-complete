from __future__ import annotations

import re
from pathlib import Path

import requests


RAW_DIR = Path("data/raw")

DRIVE_FILE_IDS = [
    "10GfFYNtj-yqUoJ05zxkFhti0DkEW_CuZ",
    "1SY1wVj6aU3coZcPVE5DuWxUOj5mtUP4T",
    "1NoQEbNNZyenLShtBM4CRjrh6c5lhx5Qy",
    "1M-OqSJBEz-so0Q69PzMZBq10ON_WaI17",
    "1rgkdnDbv0GcjZgfdczqr7kkVB7cGBz4s",
    "1N65c5EcrgYQmDJUAs8cxyZnp9WV10izk",
    "1zRk1hIJ1gF2vmmYbXFuKmpaFDzTiFIFj",
    "1O2cXuQhc8SMOcYY38fCJF7IErOqaP6iv",
    "13VZkUoJlyXADh3M9kbaXLi9cVEJs_76s",
    "1Avro89RBqKCLooFxiOiIpLTOtdJADTq_",
    "1vxvhJB2gVKsLfv51pXcLa39hnOr7M6vZ",
]


def _filename_from_response(response: requests.Response, file_id: str, index: int) -> str:
    disposition = response.headers.get("content-disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', disposition)
    if match:
        return match.group(1).replace("/", "_").replace("\\", "_")
    return f"provided_dataset_{index:02d}_{file_id}.csv"


def download_file(file_id: str, index: int) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    url = "https://drive.google.com/uc"
    response = session.get(url, params={"export": "download", "id": file_id}, timeout=60)
    response.raise_for_status()

    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            response = session.get(
                url,
                params={"export": "download", "confirm": value, "id": file_id},
                timeout=60,
            )
            response.raise_for_status()
            break

    filename = _filename_from_response(response, file_id, index)
    if response.content.startswith(b"%PDF"):
        filename = f"{Path(filename).stem}.pdf"
    elif not filename.lower().endswith(".csv"):
        filename = f"{Path(filename).stem}.csv"

    output_path = RAW_DIR / filename
    output_path.write_bytes(response.content)
    print(f"Downloaded {file_id} -> {output_path} ({output_path.stat().st_size:,} bytes)")
    return output_path


def main() -> None:
    for index, file_id in enumerate(DRIVE_FILE_IDS, start=1):
        download_file(file_id, index)


if __name__ == "__main__":
    main()
