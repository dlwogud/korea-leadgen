"""Export one team-ready delivery sheet: lead + Claude's outreach draft per row.

Merges the scored leads (and contacts, if enriched) with the AI outreach drafts
into a single CSV the business team can paste into a shared Google Sheet and
work directly: review the draft → approve → send.

    python scripts/export_delivery.py   →   data/delivery.csv
"""
from __future__ import annotations

import csv

from _common import DATA_DIR

OUT = DATA_DIR / "delivery.csv"

# Columns the outreach team works with
FIELDS = [
    "company_name", "best_service", "fit_score", "hiring_count", "industry",
    "tech_stack", "contact_name", "contact_title", "email", "linkedin_url",
    "outreach_message",           # Claude's draft
    "status", "notes",            # blank — for the team to fill
]


def _read(name):
    p = DATA_DIR / name
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def main() -> None:
    # base leads: prefer final_leads (has contacts) else scored_leads
    leads = _read("final_leads.csv") or _read("scored_leads.csv")
    drafts = {d["company_name"]: d.get("message", "") for d in _read("outreach_drafts.csv")}
    contacts = {c["company_name"]: c for c in _read("contacts_worksheet.csv")}
    # companies_db has best_service / tech_stack / industry (final_leads doesn't)
    db = {r["company_name"]: r for r in _read("companies_db.csv")}

    rows = []
    for lead in leads:
        name = lead.get("company_name", "")
        c = contacts.get(name, {})
        d = db.get(name, {})
        rows.append({
            "company_name": name,
            "best_service": lead.get("best_service", "") or d.get("best_service", ""),
            "fit_score": lead.get("fit_score", ""),
            "hiring_count": lead.get("hiring_count", "") or d.get("hiring_count", ""),
            "industry": lead.get("industry", "") or d.get("industry", ""),
            "tech_stack": (lead.get("tech_stack", "") or d.get("tech_stack", "") or "").replace(";", ", "),
            "contact_name": lead.get("contact_name", "") or c.get("full_name", ""),
            "contact_title": lead.get("contact_title", "") or c.get("title", ""),
            "email": lead.get("email", "") or c.get("email", ""),
            "linkedin_url": lead.get("linkedin_url", "") or c.get("linkedin_url", ""),
            "outreach_message": drafts.get(name, ""),   # blank if no draft yet
            "status": "",
            "notes": "",
        })

    DATA_DIR.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    with_msg = sum(1 for r in rows if r["outreach_message"])
    print(f"Wrote {len(rows)} leads → data/delivery.csv ({with_msg} with an outreach draft)")
    print("Paste it into the shared Google Sheet for the outreach team.")


if __name__ == "__main__":
    main()
