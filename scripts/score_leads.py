"""Score & rank sourced companies as IT-Servicing leads.

Implements the v1 heuristic from docs/lead-scoring.md, adapted to the signals
we can actually get from job-posting data:

    fit_score = 100 * (0.40*firmographic + 0.40*intent + 0.20*reachability)

  - firmographic : is this an IT/tech-adjacent company?  (industry match)
                   (company size + region get enriched later via DART; until
                    then size is a neutral 0.5 placeholder)
  - intent       : hiring-signal strength = open dev postings, saturating at 5
  - reachability : a known decision-maker contact (0 until contacts are added)

`overall` also factors engagement once outreach starts; at sourcing time
engagement is 0, so we rank by fit_score. Reads data/companies_raw.csv,
writes data/scored_leads.csv (ranked).

Run:  python scripts/score_leads.py
"""
from __future__ import annotations

import csv

import icp
from _common import DATA_DIR, RAW_CSV, SCORED_CSV, ensure_data_dir, read_companies

INTENT_SATURATION = 5   # this many open dev roles ≈ a strong, saturated signal


def size_fit(employees: str) -> float:
    """0..1 — how well headcount matches the 20-300 ICP band.

    Unknown size stays a neutral 0.5 placeholder (most Wanted-only rows). Once a
    real count is enriched (DART / 국민연금), it actually drives the score: an
    in-band company scores full, an over-300 enterprise decays so it no longer
    ties a perfect-fit SMB on points."""
    e = (employees or "").strip()
    if not e.isdigit():
        return 0.5                       # unknown → neutral
    n = int(e)
    if 20 <= n <= 300:
        return 1.0                       # squarely in the ICP band
    if n < 20:
        return 0.4                       # too small / pre-traction
    if n <= 500:
        return 0.3                       # over the band — has its own dev team
    return 0.1                           # clearly enterprise


def firmographic_score(row: dict) -> float:
    """0..1 — industry fit (vs the ICP for this lead's best service) + size fit."""
    industry = row.get("industry", "") or ""
    best = row.get("best_service") or "it_servicing"
    targets = icp.target_industries(best)
    industry_fit = 1.0 if any(t.lower() in industry.lower() for t in targets) else 0.4
    return (industry_fit + size_fit(row.get("employees", ""))) / 2


def intent_score(hiring_count: int) -> float:
    """0..1 — saturating hiring-signal strength."""
    return min(1.0, hiring_count / INTENT_SATURATION)


def score_company(row: dict) -> dict:
    hiring_count = int(row.get("hiring_count") or 0)
    firmo = firmographic_score(row)
    intent = intent_score(hiring_count)
    reachability = 0.0  # no contact yet → enriched when contacts are added

    fit_score = 100 * (0.40 * firmo + 0.40 * intent + 0.20 * reachability)
    engagement_bonus = 0.0  # rises as the lead moves down the funnel
    overall = 0.7 * fit_score + 0.3 * engagement_bonus

    return {
        **row,
        "firmographic": round(firmo, 2),
        "intent": round(intent, 2),
        "reachability": round(reachability, 2),
        "fit_score": round(fit_score, 1),
        "overall": round(overall, 1),
    }


def main() -> None:
    # prefer the enriched living DB (tech stack + service fits) if it exists
    db = DATA_DIR / "companies_db.csv"
    source = db if db.exists() else RAW_CSV
    companies = read_companies(source)
    print(f"(scoring from {source.name})")
    scored = [score_company(r) for r in companies]
    scored.sort(key=lambda r: r["fit_score"], reverse=True)

    ensure_data_dir()
    fields = list(scored[0].keys()) if scored else []
    with SCORED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(scored)

    # console preview: top 15 leads
    print(f"\nScored {len(scored)} companies → data/scored_leads.csv\n")
    print(f"{'rank':>4}  {'fit':>5}  {'hires':>5}  company")
    print("-" * 60)
    for i, r in enumerate(scored[:15], 1):
        print(f"{i:>4}  {r['fit_score']:>5}  {r['hiring_count']:>5}  {r['company_name']}")


if __name__ == "__main__":
    main()
