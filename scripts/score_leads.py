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

from _common import DATA_DIR, RAW_CSV, SCORED_CSV, ensure_data_dir, read_companies

# Industry keywords that indicate a tech-building company (strong IT-Servicing fit)
TECH_INDUSTRY_HINTS = [
    "IT", "정보통신", "소프트웨어", "솔루션", "플랫폼", "게임", "인터넷",
    "모바일", "AI", "인공지능", "핀테크", "이커머스", "데이터", "보안", "SI",
]

INTENT_SATURATION = 5   # this many open dev roles ≈ a strong, saturated signal


def firmographic_score(industry: str) -> float:
    """0..1 — industry tech-fit blended with a neutral size placeholder."""
    industry = industry or ""
    industry_fit = 1.0 if any(h.lower() in industry.lower() for h in TECH_INDUSTRY_HINTS) else 0.4
    size_placeholder = 0.5  # unknown from job data; enriched later via DART
    return (industry_fit + size_placeholder) / 2


def intent_score(hiring_count: int) -> float:
    """0..1 — saturating hiring-signal strength."""
    return min(1.0, hiring_count / INTENT_SATURATION)


def score_company(row: dict) -> dict:
    hiring_count = int(row.get("hiring_count") or 0)
    firmo = firmographic_score(row.get("industry", ""))
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
