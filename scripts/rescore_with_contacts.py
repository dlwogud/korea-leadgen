"""Step 3 of contact enrichment: fold filled-in contacts back into the score.

`reachability` was 0 at sourcing time. Once a decision-maker contact exists, a
lead is actually actionable, so its score should rise. Reads the filled
contacts_worksheet.csv, recomputes reachability, and writes a final ranked list.

reachability:
    email present            → 1.0   (can email directly)
    linkedin only            → 0.6   (can reach via LinkedIn)
    name only                → 0.3   (know who, no channel yet)
    nothing                  → 0.0
A non-decision-maker contact is capped at 0.5 (still need the right person).

Run:  python scripts/rescore_with_contacts.py
"""
from __future__ import annotations

import csv

from _common import DATA_DIR, ensure_data_dir, read_companies
from score_leads import firmographic_score, intent_score

WORKSHEET = DATA_DIR / "contacts_worksheet.csv"
FINAL_CSV = DATA_DIR / "final_leads.csv"


def reachability_from_contact(row: dict) -> float:
    email = (row.get("email") or "").strip()
    linkedin = (row.get("linkedin_url") or "").strip()
    name = (row.get("full_name") or "").strip()

    if email:
        base = 1.0
    elif linkedin:
        base = 0.6
    elif name:
        base = 0.3
    else:
        base = 0.0

    is_dm = (row.get("is_decision_maker") or "").strip().lower() in ("y", "yes", "true", "1")
    if base > 0 and not is_dm:
        base = min(base, 0.5)  # found someone, but not the decision-maker yet
    return base


def main() -> None:
    if not WORKSHEET.exists():
        raise SystemExit("No contacts_worksheet.csv yet. Run make_contact_worksheet.py first.")

    # contacts by company (best contact per company)
    contacts: dict[str, dict] = {}
    with WORKSHEET.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("company_name") or "").strip()
            if not name:
                continue
            r = reachability_from_contact(row)
            if name not in contacts or r > contacts[name]["reachability"]:
                contacts[name] = {"reachability": r, "row": row}

    rows = []
    for company in read_companies():
        name = company.get("company_name", "")
        firmo = firmographic_score(company)
        intent = intent_score(int(company.get("hiring_count") or 0))
        reach = contacts.get(name, {}).get("reachability", 0.0)
        contact_row = contacts.get(name, {}).get("row", {})

        fit_score = 100 * (0.40 * firmo + 0.40 * intent + 0.20 * reach)
        rows.append({
            "company_name": name,
            "fit_score": round(fit_score, 1),
            "hiring_count": company.get("hiring_count", ""),
            "industry": company.get("industry", ""),
            "reachability": round(reach, 2),
            "contact_name": contact_row.get("full_name", ""),
            "contact_title": contact_row.get("title", ""),
            "email": contact_row.get("email", ""),
            "linkedin_url": contact_row.get("linkedin_url", ""),
        })

    rows.sort(key=lambda r: r["fit_score"], reverse=True)
    ensure_data_dir()
    with FINAL_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nRe-scored {len(rows)} leads with contacts → data/final_leads.csv\n")
    print(f"{'fit':>5}  {'reach':>5}  {'contact':<16}  company")
    print("-" * 64)
    for r in rows[:15]:
        print(f"{r['fit_score']:>5}  {r['reachability']:>5}  {r['contact_name'][:16]:<16}  {r['company_name']}")


if __name__ == "__main__":
    main()
