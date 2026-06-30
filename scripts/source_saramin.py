"""Data source: Saramin Open API (job-search) → company hiring signals.

Two ways to find IT postings:

  1. CATEGORY mode (recommended) — filter by Saramin's own job category
     (job_mid_cd). Catches every IT posting regardless of how the title is
     worded ("백엔드", "Java 개발자", "API Engineer" …), which keyword search
     misses. You need the IT category code; discover it with --list-categories.

  2. KEYWORD mode (fallback) — search a list of role keywords. Works without
     knowing any codes, but misses title variants.

Aggregates postings by company and writes the shared company schema
(_common.COMPANY_FIELDS) to data/companies_raw.csv. The number of open IT
postings per company is our buying signal for the IT-Servicing offering.

LICENSING: Saramin Open API free tier — prototype / non-resale use only
(≤500 calls/day, no reselling). Commercial scale-up needs Saramin licensing.
The source layer is swappable (see _common) so the provider can be replaced.

Run:
    export SARAMIN_API_KEY=...                       # or korea-leadgen/.env
    python scripts/source_saramin.py --list-categories      # 1) find the IT code
    python scripts/source_saramin.py --job-mid-cd 2 --pages 3   # 2) category mode
    python scripts/source_saramin.py                         # keyword fallback
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from collections import Counter

import requests

import icp
from _common import load_dotenv, write_companies

API_URL = "https://oapi.saramin.co.kr/job-search"

# Keywords come from the ICP (config/icp.json) — sourcing is ICP-driven.
# Default = union of all services' keywords; narrow with --service or --keywords.
DEFAULT_KEYWORDS = icp.all_keywords()

COUNT_PER_CALL = 110          # Saramin max per call
SAFETY_MAX_CALLS = 50         # hard stop well under the 500/day limit
SLEEP_BETWEEN_CALLS = 0.4     # be polite to the API


def saramin_search(key: str, *, keyword: str | None = None,
                   job_mid_cd: str | None = None, start: int = 1,
                   debug: bool = False) -> dict:
    """One API call (by keyword and/or category). Returns the 'jobs' object."""
    params = {
        "access-key": key,
        "count": COUNT_PER_CALL,
        "start": start,
        "sort": "pd",  # posting date desc → freshest hiring signals first
    }
    if keyword:
        params["keywords"] = keyword
    if job_mid_cd:
        params["job_mid_cd"] = job_mid_cd

    resp = requests.get(API_URL, params=params, headers={"Accept": "application/json"}, timeout=20)
    resp.raise_for_status()
    try:
        data = resp.json()
    except ValueError:
        print("ERROR: response was not JSON. First 500 chars:\n", resp.text[:500], file=sys.stderr)
        raise
    if debug:
        print(f"[debug] keyword={keyword!r} job_mid_cd={job_mid_cd!r} start={start} "
              f"-> keys={list(data.keys())}", file=sys.stderr)
    return data.get("jobs", {}) or {}


def _as_list(node):
    """Saramin returns a list for many results, a single dict for one. Normalise."""
    if node is None:
        return []
    return node if isinstance(node, list) else [node]


def _absorb_job(job: dict, by_company: dict, seen_job_ids: set) -> None:
    """Fold one posting into the per-company aggregate (with posting dedup)."""
    jid = str(job.get("id") or "")
    if jid and jid in seen_job_ids:
        return  # already counted this posting under another query
    if jid:
        seen_job_ids.add(jid)

    company = (job.get("company") or {}).get("detail") or {}
    name = (company.get("name") or "").strip()
    if not name:
        return
    position = job.get("position") or {}
    title = (position.get("title") or "").strip()
    industry = ((position.get("industry") or {}).get("name") or "").strip()
    location = ((position.get("location") or {}).get("name") or "").strip()
    url = company.get("href") or job.get("url") or ""

    rec = by_company.setdefault(name, {
        "company_name": name, "industry": industry, "_locations": set(),
        "hiring_count": 0, "_titles": [], "source": "saramin", "source_url": url,
    })
    rec["hiring_count"] += 1
    if location:
        rec["_locations"].add(location)
    if title and len(rec["_titles"]) < 5:
        rec["_titles"].append(title)
    if not rec["industry"] and industry:
        rec["industry"] = industry


def _finalise(by_company: dict) -> list[dict]:
    rows = []
    for rec in by_company.values():
        rec["locations"] = ";".join(sorted(rec.pop("_locations")))
        rec["sample_titles"] = ";".join(rec.pop("_titles"))
        rows.append(rec)
    rows.sort(key=lambda r: r["hiring_count"], reverse=True)
    return rows


def fetch_companies(key: str, *, keywords: list[str] | None = None,
                    job_mid_cd: str | None = None, pages: int = 2,
                    debug: bool = False) -> list[dict]:
    """CATEGORY mode if job_mid_cd is set, else KEYWORD mode."""
    by_company: dict = {}
    seen_job_ids: set = set()
    calls = 0
    # category mode = a single query stream; keyword mode = one per keyword
    queries = [{"job_mid_cd": job_mid_cd}] if job_mid_cd else [{"keyword": k} for k in (keywords or [])]

    for q in queries:
        for page in range(1, pages + 1):
            if calls >= SAFETY_MAX_CALLS:
                print(f"[guard] hit SAFETY_MAX_CALLS={SAFETY_MAX_CALLS}; stopping.", file=sys.stderr)
                break
            jobs = saramin_search(key, start=page, debug=debug, **q)
            calls += 1
            job_list = _as_list(jobs.get("job"))
            if not job_list:
                break
            for job in job_list:
                _absorb_job(job, by_company, seen_job_ids)
            time.sleep(SLEEP_BETWEEN_CALLS)

    rows = _finalise(by_company)
    mode = f"category {job_mid_cd}" if job_mid_cd else f"{len(queries)} keyword(s)"
    print(f"[ok] {mode}: {calls} call(s) → {len(rows)} unique companies "
          f"({len(seen_job_ids)} postings)", file=sys.stderr)
    return rows


def list_categories(key: str, seed_keyword: str, pages: int, debug: bool) -> None:
    """Discover Saramin's job category codes by tallying them across a sample.

    Prints `job-mid-code` (code → name → posting count) so you can pick the IT
    category code to use with --job-mid-cd. Run this once after getting a key.
    """
    counter: Counter = Counter()
    names: dict = {}
    calls = 0
    for page in range(1, pages + 1):
        if calls >= SAFETY_MAX_CALLS:
            break
        jobs = saramin_search(key, keyword=seed_keyword, start=page, debug=debug)
        calls += 1
        for job in _as_list(jobs.get("job")):
            mid = (job.get("position") or {}).get("job-mid-code") or {}
            code = str(mid.get("code") or "")
            name = mid.get("name") or ""
            if code:
                counter[code] += 1
                names[code] = name
        time.sleep(SLEEP_BETWEEN_CALLS)

    print(f"\nJob categories seen in '{seed_keyword}' postings ({calls} call(s)):\n")
    print(f"{'code':>6}  {'count':>5}  name")
    print("-" * 50)
    for code, cnt in counter.most_common():
        print(f"{code:>6}  {cnt:>5}  {names.get(code,'')}")
    print("\n→ Pick the IT/dev category code and run:")
    print("    python scripts/source_saramin.py --job-mid-cd <code>")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Source Korean companies from Saramin job postings.")
    parser.add_argument("--job-mid-cd", help="Saramin job category code (CATEGORY mode)")
    parser.add_argument("--service", choices=icp.services(),
                        help="source only this service's ICP keywords (config/icp.json)")
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS),
                        help="comma-separated keywords (KEYWORD mode / category discovery seed)")
    parser.add_argument("--pages", type=int, default=2, help="pages per query (110 postings each)")
    parser.add_argument("--list-categories", action="store_true",
                        help="discover job category codes, then exit")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    key = os.getenv("SARAMIN_API_KEY")
    if not key:
        sys.exit("ERROR: set SARAMIN_API_KEY (env var or korea-leadgen/.env). "
                 "Get a free key at https://oapi.saramin.co.kr")

    if args.list_categories:
        seed = args.keywords.split(",")[0].strip() or "개발"
        list_categories(key, seed, args.pages, args.debug)
        return

    if args.job_mid_cd:
        rows = fetch_companies(key, job_mid_cd=args.job_mid_cd, pages=args.pages, debug=args.debug)
    else:
        keywords = icp.keywords(args.service) if args.service else \
            [k.strip() for k in args.keywords.split(",") if k.strip()]
        rows = fetch_companies(key, keywords=keywords, pages=args.pages, debug=args.debug)

    write_companies(rows)
    print(f"Wrote {len(rows)} companies → data/companies_raw.csv")
    print("Next: python scripts/score_leads.py")


if __name__ == "__main__":
    main()
