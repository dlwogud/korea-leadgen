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

from _common import DATA_DIR, RAW_CSV, read_companies

DB_CSV = DATA_DIR / "companies_db.csv"

DB_FIELDS = [
    "company_name", "industry", "locations", "hiring_count", "sample_titles",
    "tech_stack",
    "fit_it_servicing", "fit_manpower", "fit_ai_implementation", "fit_systems_integration",
    "best_service",
    "source", "source_url", "first_seen", "last_seen",
]

# Tech terms to detect in job titles (extend freely)
TECH_TERMS = [
    "Java", "Python", "Node.js", "Spring", "Kotlin", "Rust", "PHP",
    "React", "Vue", "Angular", "TypeScript", "Next.js", "Flutter", "Android", "iOS", "Swift",
    "AWS", "GCP", "Azure", "Kubernetes", "Docker", "Terraform",
    "Kafka", "Spark", "Airflow", "Hadoop", "SQL", "MongoDB", "Redis", "Elasticsearch",
    "TensorFlow", "PyTorch", "ML", "AI", "NLP", "LLM",
]

# Industry hints that indicate tech-building (IT-Servicing / Manpower fit)
TECH_INDUSTRY = ["IT", "정보통신", "소프트웨어", "솔루션", "플랫폼", "게임", "인터넷",
                 "모바일", "AI", "인공지능", "핀테크", "이커머스", "데이터", "보안", "SI"]
# Traditional industries that more often need Systems Integration
TRADITIONAL_INDUSTRY = ["제조", "유통", "물류", "금융", "은행", "보험", "공공", "건설", "의료"]
# Signals that indicate AI-Implementation need (note: plain "데이터" excluded —
# data engineering is not the same as needing AI built)
AI_TERMS = ["AI", "인공지능", "ML", "머신러닝", "추천", "NLP", "LLM",
            "TensorFlow", "PyTorch", "컴퓨터비전"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def extract_tech_stack(titles: str) -> str:
    text = (titles or "").lower()
    found = [t for t in TECH_TERMS if t.lower() in text]
    # dedupe preserving order
    seen, out = set(), []
    for t in found:
        if t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return ";".join(out)


def _has(hints, *texts) -> bool:
    blob = " ".join(t or "" for t in texts).lower()
    return any(h.lower() in blob for h in hints)


def service_fits(row: dict, tech_stack: str) -> dict:
    titles = row.get("sample_titles", "")
    industry = row.get("industry", "")
    hiring = int(row.get("hiring_count") or 0)
    intent = min(1.0, hiring / 5)                      # hiring-signal strength
    is_tech = _has(TECH_INDUSTRY, industry) or bool(tech_stack)
    tech = 1.0 if is_tech else 0.4

    fit_it = 100 * (0.5 * tech + 0.5 * intent)         # deliver the dev work
    fit_manpower = 100 * (0.4 * tech + 0.6 * intent)   # fill the dev seats (volume)
    ai_sig = 1.0 if _has(AI_TERMS, titles, industry, tech_stack) else 0.2
    fit_ai = 100 * (0.7 * ai_sig + 0.3 * intent)
    si_sig = 1.0 if _has(TRADITIONAL_INDUSTRY, industry) else 0.2
    fit_si = 100 * (0.6 * si_sig)                      # low-confidence from job data

    fits = {
        "fit_it_servicing": round(fit_it, 1),
        "fit_manpower": round(fit_manpower, 1),
        "fit_ai_implementation": round(fit_ai, 1),
        "fit_systems_integration": round(fit_si, 1),
    }
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
