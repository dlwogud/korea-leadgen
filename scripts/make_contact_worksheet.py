"""Step 1 of contact enrichment: turn the top-N scored leads into a worksheet
to fill in decision-maker contacts.

Finding the actual person + email is the hard, mostly-manual part of B2B
(no good free API for Korea). This produces a focused worksheet — company info
pre-filled, contact columns blank — so the research is structured instead of ad hoc.

After filling it in (LinkedIn / company site / Hunter.io free tier), run
rescore_with_contacts.py to fold contacts back into the score.

Run:  python scripts/make_contact_worksheet.py --top 20
"""
from __future__ import annotations

import argparse
import csv

from _common import DATA_DIR, SCORED_CSV, ensure_data_dir

WORKSHEET = DATA_DIR / "contacts_worksheet.csv"

# pre-filled (from scoring) + blank columns for manual research
WORKSHEET_FIELDS = [
    # pre-filled
    "company_name", "fit_score", "hiring_count", "industry", "source_url",
    # to fill in manually:
    "full_name", "title", "email", "linkedin_url",
    "is_decision_maker",   # y / n
    "status", "notes",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a contact-research worksheet from top leads.")
    parser.add_argument("--top", type=int, default=20, help="how many top leads to research")
    args = parser.parse_args()

    with SCORED_CSV.open(encoding="utf-8") as f:
        leads = list(csv.DictReader(f))[: args.top]

    ensure_data_dir()
    with WORKSHEET.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=WORKSHEET_FIELDS)
        writer.writeheader()
        for lead in leads:
            writer.writerow({
                "company_name": lead.get("company_name", ""),
                "fit_score": lead.get("fit_score", ""),
                "hiring_count": lead.get("hiring_count", ""),
                "industry": lead.get("industry", ""),
                "source_url": lead.get("source_url", ""),
                # blanks below for manual research
            })

    print(f"Wrote {len(leads)} rows → data/contacts_worksheet.csv")
    print("Fill in full_name / title / email / linkedin_url / is_decision_maker,")
    print("then run: python scripts/rescore_with_contacts.py")


if __name__ == "__main__":
    main()
