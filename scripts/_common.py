"""Shared helpers: .env loading, CSV paths, the company record shape.

Keeping the company record schema in one place is what makes the data source
pluggable — source_saramin.py (or a future source_worknet.py) only has to emit
rows with these columns, and score_leads.py consumes them unchanged.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from urllib.parse import quote

# Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_CSV = DATA_DIR / "companies_raw.csv"
SCORED_CSV = DATA_DIR / "scored_leads.csv"

# The shared "company" schema every data source must emit.
COMPANY_FIELDS = [
    "company_name",   # 회사명
    "industry",       # 업종 (best-effort from the source)
    "locations",      # ';'-joined regions seen across postings
    "hiring_count",   # number of open IT/dev postings found = hiring-signal strength
    "employees",      # approx. headcount (firmographic ICP check: 20-300); '' if unknown
    "sample_titles",  # ';'-joined example job titles (evidence)
    "source",         # which data source produced this row ('saramin', ...)
    "source_url",     # one representative link
]


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader (no external dependency). Lines like KEY=value."""
    path = path or (ROOT / ".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def write_companies(rows: list[dict], path: Path = RAW_CSV) -> None:
    ensure_data_dir()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMPANY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in COMPANY_FIELDS})


def read_companies(path: Path = RAW_CSV) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def job_link(source_url: str, source: str, company: str) -> str:
    """A working posting link for any source: the real posting URL if we have
    it, else a search on that source (Saramin / Wanted), else a Google search."""
    if (source_url or "").strip():
        return source_url.strip()
    q = quote(company or "")
    s = (source or "").lower()
    if "saramin" in s:
        return "https://www.saramin.co.kr/zf_user/search?searchword=" + q
    if "wanted" in s:
        return "https://www.wanted.co.kr/search?query=" + q
    return "https://www.google.com/search?q=" + quote((company or "") + " 채용")
