"""Enrich + maintain the living prospect DB (closes DS-track §5.2 gaps).

Takes a fresh source run (companies_raw.csv) and:
  1. extracts a TECH-STACK signal from job titles (React / AWS / Python …),
  2. scores FIT for all 4 service areas (not just IT-Servicing),
  3. MERGES into a persistent data/companies_db.csv with first_seen / last_seen
     timestamps — so re-running keeps the DB continuously updated instead of
     overwriting it.

companies_db.csv is the "living database" scoring reads from.

Run:  python scripts/enrich.py
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone

import icp
from _common import DATA_DIR, RAW_CSV, read_companies

DB_CSV = DATA_DIR / "companies_db.csv"

DB_FIELDS = [
    "company_name", "industry", "locations", "hiring_count", "employees", "sample_titles",
    "tech_stack",
    "fit_it_servicing", "fit_manpower", "fit_ai_implementation", "fit_systems_integration",
    "best_service",
    "source", "source_url", "first_seen", "last_seen",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def extract_tech_stack(titles: str) -> str:
    text = (titles or "").lower()
    found = [t for t in icp.tech_terms() if t.lower() in text]
    seen, out = set(), []                               # dedupe, preserve order
    for t in found:
        if t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return ";".join(out)


def service_fits(row: dict, tech_stack: str) -> dict:
    """Per-service fit, all driven by config/icp.json (the ICP)."""
    scoring_row = {**row, "tech_stack": tech_stack}
    fits = {f"fit_{svc}": round(icp.fit(scoring_row, svc), 1) for svc in icp.services()}
    best = max(fits, key=fits.get).replace("fit_", "")
    return {**fits, "best_service": best}


def load_existing() -> dict:
    if not DB_CSV.exists():
        return {}
    with DB_CSV.open(encoding="utf-8") as f:
        return {r["company_name"]: r for r in csv.DictReader(f)}


def main() -> None:
    raw = read_companies(RAW_CSV)
    existing = load_existing()
    now = _now()

    for row in raw:
        name = row.get("company_name", "")
        tech = extract_tech_stack(row.get("sample_titles", ""))
        fits = service_fits(row, tech)
        prev = existing.get(name)
        existing[name] = {
            "company_name": name,
            "industry": row.get("industry", ""),
            "locations": row.get("locations", ""),
            "hiring_count": row.get("hiring_count", ""),   # latest value (not summed)
            "employees": row.get("employees", ""),
            "sample_titles": row.get("sample_titles", ""),
            "tech_stack": tech,
            **fits,
            "source": row.get("source", ""),
            "source_url": row.get("source_url", ""),
            "first_seen": prev["first_seen"] if prev else now,
            "last_seen": now,
        }

    rows = sorted(existing.values(),
                  key=lambda r: float(r.get("fit_it_servicing") or 0), reverse=True)
    with DB_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in DB_FIELDS})

    new_count = sum(1 for r in rows if r["first_seen"] == now)
    print(f"DB updated → data/companies_db.csv  ({len(rows)} companies, "
          f"{new_count} new this run, as of {now})")
    print(f"\n{'company':<18}{'best service':<20}{'tech stack'}")
    print("-" * 70)
    for r in rows[:10]:
        print(f"{r['company_name'][:17]:<18}{r['best_service']:<20}{r['tech_stack'][:30]}")


if __name__ == "__main__":
    main()
