"""Data source: Wanted job postings → Korean IT company hiring signals.

Collects developer/IT job postings from Wanted, filters them to the ICP
(developer-type roles), aggregates by company (postings-per-company = hiring
signal), and writes the shared company schema (_common.COMPANY_FIELDS) to
data/companies_raw.csv — so it flows through the exact same enrich → score →
qualify pipeline as every other source.

⚠️ USE POLICY — READ BEFORE RUNNING
This reads Wanted's public listing endpoint programmatically. Automated
collection can conflict with a site's Terms of Service, and in Korea there is
precedent (사람인 v. 잡코리아) around job-posting extraction. Whether to actually
RUN this — and at what scale / for what purpose — is a **company decision**, not
an intern's. This script exists so the capability is ready if the company opts
in; for a commercial product, use a licensed API instead. It is deliberately
rate-limited and capped, and does NOT collect personal contact data.

Run:
    python scripts/source_wanted.py --pages 2 --debug      # verify fields first
    python scripts/source_wanted.py --pages 3
    # then: python scripts/enrich.py && python scripts/score_leads.py
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict

import requests

from _common import write_companies

API_URL = "https://www.wanted.co.kr/api/v4/jobs"
COMPANY_JOBS_URL = "https://www.wanted.co.kr/api/v4/companies/{}/jobs"  # all open roles for one company
JOB_URL = "https://www.wanted.co.kr/wd/{}"      # one representative posting link

DEV_GROUP = "518"                # Wanted "개발" (developer) job group
LIMIT_PER_CALL = 20              # Wanted page size
SAFETY_MAX_PAGES = 30            # hard stop
SLEEP_BETWEEN_CALLS = 1.0        # be polite — one request/sec

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "application/json",
}

# ICP: keep developer/IT-type roles (title-level filter, KR + EN).
DEV_TERMS = [
    "개발", "엔지니어", "engineer", "developer", "backend", "back-end", "프론트",
    "frontend", "front-end", "풀스택", "fullstack", "full-stack", "서버", "server",
    "devops", "sre", "infra", "인프라", "qa", "데이터", "data", "ai", "ml",
    "machine learning", "머신러닝", "딥러닝", "mlops", "보안", "security", "android",
    "ios", "mobile", "모바일", "웹", "web", "플랫폼", "platform",
]


def fetch_page(offset: int, group: str, debug: bool = False) -> list[dict]:
    """One listing page. Returns the raw job list (Wanted 'data')."""
    params = {
        "country": "kr",
        "job_group_id": group,
        "job_sort": "job.latest_order",
        "years": -1,
        "locations": "all",
        "limit": LIMIT_PER_CALL,
        "offset": offset,
    }
    r = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    body = r.json()
    data = body.get("data") or body.get("jobs") or []
    if debug:
        print(f"[debug] offset={offset} status={r.status_code} items={len(data)}")
        if data:
            print("[debug] sample keys:", sorted(data[0].keys()))
            print("[debug] sample item:", data[0])
    return data


DEV_GROUP_ID = 518               # Wanted category parent id for "개발"


def parse_job(job: dict) -> dict | None:
    """Extract company, title, industry, location, id + dev classification."""
    comp = job.get("company") or {}
    company = comp.get("name", "") if isinstance(comp, dict) else ""
    industry = comp.get("industry_name", "") if isinstance(comp, dict) else ""
    title = job.get("position") or job.get("title") or ""
    addr = job.get("address") or {}
    city = addr.get("location", "") if isinstance(addr, dict) else ""
    dist = addr.get("district", "") if isinstance(addr, dict) else ""
    loc = (f"{city} {dist}").strip()
    tags = job.get("category_tags") or []
    parents = {t.get("parent_id") for t in tags if isinstance(t, dict)}
    if not company or not title:
        return None
    company_id = comp.get("id") if isinstance(comp, dict) else None
    # dev if Wanted classifies it under the 개발 group; else fall back to title words
    is_dev = (DEV_GROUP_ID in parents) or (not parents and is_dev_title(title))
    return {"company": company.strip(), "title": title.strip(),
            "industry": industry.strip(), "location": loc,
            "id": job.get("id"), "company_id": company_id, "is_dev": is_dev}


def fetch_company_jobs(company_id, debug: bool = False) -> list[dict]:
    """Every currently-open posting for one company (not just the ones that
    happened to appear on the listing pages we read). This is what makes the
    hiring-count signal accurate — a 280-person company hiring 6 devs shows as
    6, not 1."""
    r = requests.get(COMPANY_JOBS_URL.format(company_id), headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json().get("data") or []
    if debug:
        print(f"[debug] company {company_id}: {len(data)} total open postings")
    return data


def is_dev_title(title: str) -> bool:
    t = title.lower()
    return any(term in t for term in DEV_TERMS)


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect ICP-fit dev postings from Wanted.")
    ap.add_argument("--pages", type=int, default=3, help="listing pages to read")
    ap.add_argument("--job-group", default=DEV_GROUP, help="Wanted job group id (518=dev)")
    ap.add_argument("--all-roles", action="store_true",
                    help="skip the developer-title filter (keep every posting)")
    ap.add_argument("--no-expand", action="store_true",
                    help="skip per-company full-posting fetch (faster, but hiring "
                         "count is undercounted to only what appeared on the pages read)")
    ap.add_argument("--sleep", type=float, default=SLEEP_BETWEEN_CALLS)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    pages = min(args.pages, SAFETY_MAX_PAGES)
    # aggregate by company
    titles: dict[str, list[str]] = defaultdict(list)
    locs: dict[str, set] = defaultdict(set)
    industry: dict[str, str] = {}
    first_id: dict[str, str] = {}
    comp_id: dict[str, str] = {}
    seen_jobs = set()
    kept = skipped = 0

    for p in range(pages):
        try:
            data = fetch_page(p * LIMIT_PER_CALL, args.job_group, args.debug)
        except requests.HTTPError as e:
            sys.exit(f"ERROR: Wanted request failed ({e}). They may be blocking "
                     f"automated access — this is the ToS risk noted in the header.")
        if not data:
            break
        for job in data:
            rec = parse_job(job)
            if not rec:
                continue
            if rec["id"] in seen_jobs:               # dedupe postings
                continue
            seen_jobs.add(rec["id"])
            if not args.all_roles and not rec["is_dev"]:
                skipped += 1
                continue
            kept += 1
            c = rec["company"]
            titles[c].append(rec["title"])
            if rec["location"]:
                locs[c].add(rec["location"])
            industry.setdefault(c, rec["industry"])
            first_id.setdefault(c, rec["id"])
            if rec.get("company_id"):
                comp_id.setdefault(c, rec["company_id"])
        time.sleep(args.sleep)

    # Expansion: for each discovered company, pull EVERY open posting (not just
    # the ones seen on the listing pages) so hiring_count reflects real demand.
    if not args.no_expand:
        companies = list(titles.keys())
        print(f"Expanding {sum(1 for c in companies if comp_id.get(c))} companies "
              f"to their full posting lists...")
        for c in companies:
            cid = comp_id.get(c)
            if not cid:
                continue
            try:
                full = fetch_company_jobs(cid, args.debug)
            except requests.RequestException:
                continue                     # keep the listing-page count on failure
            dev_titles, first_dev = [], None
            for job in full:
                rec = parse_job(job)
                if not rec:
                    continue
                if not args.all_roles and not rec["is_dev"]:
                    continue
                dev_titles.append(rec["title"])
                if first_dev is None:
                    first_dev = rec["id"]
                if rec["location"]:
                    locs[c].add(rec["location"])
            if dev_titles:
                titles[c] = dev_titles       # replace undercount with full list
                if first_dev:
                    first_id[c] = first_dev
            time.sleep(args.sleep)

    rows = []
    for company, ts in titles.items():
        rows.append({
            "company_name": company,
            "industry": industry.get(company, ""),    # from Wanted company.industry_name
            "locations": ";".join(sorted(locs[company])),
            "hiring_count": len(ts),                  # postings = hiring signal
            "employees": "",
            "sample_titles": ";".join(dict.fromkeys(ts)),   # unique, ordered
            "source": "wanted",
            "source_url": JOB_URL.format(first_id[company]) if first_id.get(company) else "",
        })
    rows.sort(key=lambda r: r["hiring_count"], reverse=True)

    write_companies(rows)
    print(f"Collected {kept} dev postings ({skipped} non-dev skipped) across "
          f"{pages} pages → {len(rows)} companies → data/companies_raw.csv")
    if rows:
        print("\nTop by open postings:")
        for r in rows[:10]:
            print(f"  {r['hiring_count']:>2}  {r['company_name']}  ({r['sample_titles'][:50]})")
    print("\nNext: python scripts/enrich.py  then  python scripts/score_leads.py")


if __name__ == "__main__":
    main()
