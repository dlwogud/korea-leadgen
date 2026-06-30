"""Ingest a business-provided company list into the pipeline.

The DS role is to RECEIVE what the Business track organises (their target
account list / spreadsheet) and structure + score it. This takes any CSV the
business hands over, maps its columns to our schema, and writes
companies_raw.csv — so a business list flows through the exact same
enrich → score → dashboard pipeline as automated Saramin sourcing.

Column names are auto-detected (Korean or English). At minimum the file needs a
company-name column.

Run:
    python scripts/import_list.py --file business_targets.csv
    python scripts/score_leads.py        # after: python scripts/enrich.py
"""
from __future__ import annotations

import argparse
import csv

from _common import COMPANY_FIELDS, write_companies

# Candidate column names → our field (first match wins, case-insensitive)
COLUMN_ALIASES = {
    "company_name": ["company_name", "회사명", "기업명", "company", "name", "기업", "고객사"],
    "industry":     ["industry", "업종", "산업", "산업군", "분야"],
    "locations":    ["locations", "location", "지역", "region", "소재지"],
    "hiring_count": ["hiring_count", "채용수", "채용", "공고수", "오픈포지션"],
    "sample_titles": ["sample_titles", "titles", "직무", "포지션", "채용직무"],
    "source_url":   ["source_url", "url", "홈페이지", "링크", "website"],
}


def _build_colmap(header: list[str]) -> dict:
    lower = {h.lower().strip(): h for h in header}
    colmap = {}
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower:
                colmap[field] = lower[alias.lower()]
                break
    return colmap


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a business-provided company list.")
    parser.add_argument("--file", required=True, help="CSV from the business track")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        colmap = _build_colmap(header)
        if "company_name" not in colmap:
            raise SystemExit(
                f"Could not find a company-name column in {header}. "
                f"Rename it to one of: {COLUMN_ALIASES['company_name']}")

        rows = []
        for src in reader:
            name = (src.get(colmap["company_name"]) or "").strip()
            if not name:
                continue
            rows.append({
                "company_name": name,
                "industry": src.get(colmap.get("industry", ""), "") or "",
                "locations": src.get(colmap.get("locations", ""), "") or "",
                "hiring_count": src.get(colmap.get("hiring_count", ""), "") or "",
                "sample_titles": src.get(colmap.get("sample_titles", ""), "") or "",
                "source": "business_list",
                "source_url": src.get(colmap.get("source_url", ""), "") or "",
            })

    write_companies(rows)
    print(f"Imported {len(rows)} companies from {args.file} → data/companies_raw.csv")
    print(f"Mapped columns: { {k: colmap[k] for k in colmap} }")
    print("Next: python scripts/enrich.py  then  python scripts/score_leads.py")


if __name__ == "__main__":
    main()
