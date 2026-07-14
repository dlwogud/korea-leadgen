"""Firmographic enrichment: employee count from DART (금융감독원 전자공시).

Fills companies_db.employees with the OFFICIAL headcount reported in each
company's annual report (사업보고서 직원현황). This is real, audited public data —
the number a Korean analyst would cite. Coverage is limited to companies that
file reports (listed + external-audit firms), so small startups often return
nothing; those stay blank for a broader source (e.g. 국민연금) to fill.

Design:
  - corpCode list (name -> corp_code) is downloaded once and cached
    (data/dart_corpcodes.json), refreshed only if missing.
  - Per-company lookups are cached (data/dart_employees.csv) so re-runs and the
    daily cron never re-hit DART for a company already resolved. This also means
    the count SURVIVES a re-scrape that blanks employees.

Run:  python scripts/enrich_dart.py        (needs DART_API_KEY in .env)
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

from _common import DATA_DIR, ROOT, load_dotenv
import os

DB = DATA_DIR / "companies_db.csv"
CORP_CACHE = DATA_DIR / "dart_corpcodes.json"
EMP_CACHE = DATA_DIR / "dart_employees.csv"
API = "https://opendart.fss.or.kr/api"
UA = {"User-Agent": "Mozilla/5.0"}


def _norm(s: str) -> str:
    return re.sub(r"\s+|주식회사|\(주\)|㈜", "", s or "").strip()


def _get_json(url: str):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))


def load_corpcodes(key: str) -> dict:
    """{normalized_name: [(corp_code, has_stock), ...]} — cached to disk."""
    if CORP_CACHE.exists():
        raw = json.loads(CORP_CACHE.read_text())
    else:
        print("Downloading DART corp code list (one-time)...")
        data = urllib.request.urlopen(
            urllib.request.Request(f"{API}/corpCode.xml?crtfc_key={key}", headers=UA), timeout=60
        ).read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        root = ET.fromstring(zf.read(zf.namelist()[0]))
        raw = [
            [c.findtext("corp_name", "").strip(), c.findtext("corp_code", "").strip(),
             c.findtext("stock_code", "").strip()]
            for c in root.iter("list")
        ]
        CORP_CACHE.write_text(json.dumps(raw, ensure_ascii=False))
        print(f"  cached {len(raw):,} corps → {CORP_CACHE.name}")
    idx: dict[str, list] = {}
    for name, code, stock in raw:
        idx.setdefault(_norm(name), []).append((code, bool(stock)))
    return idx


def match_corp(name: str, idx: dict) -> str | None:
    nn = _norm(name)
    if nn in idx:
        return idx[nn][0][0]
    # conservative partial match: names within 3 chars, one contained in the other
    for k, v in idx.items():
        if nn and (nn in k or k in nn) and abs(len(k) - len(nn)) <= 3:
            return v[0][0]
    return None


def fetch_employees(key: str, corp_code: str) -> tuple[int, str] | None:
    """Total headcount from the most recent annual report, else None."""
    for yr in ("2024", "2023", "2025"):
        url = f"{API}/empSttus.json?crtfc_key={key}&corp_code={corp_code}&bsns_year={yr}&reprt_code=11011"
        try:
            d = _get_json(url)
        except Exception:
            continue
        if d.get("status") != "000":
            continue
        total = 0
        got = False
        for r in d.get("list", []):
            v = (r.get("sm", "") or "").replace(",", "").strip()
            if v.isdigit():
                total += int(v)
                got = True
        if got:
            return total, yr
    return None


def load_emp_cache() -> dict:
    if not EMP_CACHE.exists():
        return {}
    return {r["company_name"]: r for r in csv.DictReader(EMP_CACHE.open(encoding="utf-8"))}


def save_emp_cache(cache: dict) -> None:
    with EMP_CACHE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_name", "employees", "source_year", "corp_code"])
        w.writeheader()
        w.writerows(cache.values())


def main() -> None:
    load_dotenv()
    key = os.environ.get("DART_API_KEY") or os.environ.get("OPENDART_API_KEY")
    if not key:
        sys.exit("[skip] DART_API_KEY not set in .env — leaving employees as-is.")

    rows = list(csv.DictReader(DB.open(encoding="utf-8")))
    fields = list(rows[0].keys())
    for col in ("employees", "employees_source"):
        if col not in fields:
            fields.append(col)

    cache = load_emp_cache()
    idx = None
    resolved = newly = 0

    for r in rows:
        name = r["company_name"]
        # already have a count (from cache or a prior source)? apply and skip API.
        if name in cache and cache[name].get("employees"):
            r["employees"] = cache[name]["employees"]
            r["employees_source"] = f"DART {cache[name].get('source_year','')}".strip()
            resolved += 1
            continue
        if (r.get("employees") or "").strip():
            continue  # already filled by another source
        if idx is None:
            idx = load_corpcodes(key)
        code = match_corp(name, idx)
        if not code:
            continue
        res = fetch_employees(key, code)
        time.sleep(0.3)
        if not res:
            continue
        total, yr = res
        r["employees"] = str(total)
        r["employees_source"] = f"DART {yr}"
        cache[name] = {"company_name": name, "employees": str(total),
                       "source_year": yr, "corp_code": code}
        resolved += 1
        newly += 1
        print(f"  {name}: {total} employees (DART {yr})")

    save_emp_cache(cache)
    with DB.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"[DART] employees filled for {resolved} companies "
          f"({newly} newly fetched, rest from cache) → companies_db.csv")


if __name__ == "__main__":
    main()
