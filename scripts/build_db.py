"""Build a real SQLite database from the CSV pipeline outputs.

Turns the CSV files into a queryable database (data/leadgen.db) using
db/schema_sqlite.sql. Loads whatever CSVs exist:
  companies_db.csv → companies     scored_leads.csv → lead_scores
  contacts_worksheet.csv → contacts (filled rows)   pipeline_events.csv → pipeline_events

Run:  python scripts/build_db.py     then:  python scripts/query_db.py
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB_PATH = DATA / "leadgen.db"
SCHEMA = ROOT / "db" / "schema_sqlite.sql"


def _rows(name: str):
    path = DATA / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _insert(conn, table: str, rows: list[dict], columns: list[str]) -> int:
    if not rows:
        return 0
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, [[r.get(c, "") or None for c in columns] for r in rows])
    return len(rows)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    n_co = _insert(conn, "companies", _rows("companies_db.csv"), [
        "company_name", "industry", "locations", "hiring_count", "sample_titles",
        "tech_stack", "fit_it_servicing", "fit_manpower", "fit_ai_implementation",
        "fit_systems_integration", "best_service", "source", "source_url",
        "first_seen", "last_seen"])

    n_ls = _insert(conn, "lead_scores", _rows("scored_leads.csv"), [
        "company_name", "fit_score", "firmographic", "intent", "reachability", "overall"])

    contacts = [r for r in _rows("contacts_worksheet.csv") if (r.get("full_name") or "").strip()]
    n_ct = _insert(conn, "contacts", contacts, [
        "company_name", "full_name", "title", "email", "linkedin_url",
        "is_decision_maker", "status", "notes"])

    n_pe = _insert(conn, "pipeline_events", _rows("pipeline_events.csv"), [
        "company_name", "service", "stage", "entered_at", "note"])

    conn.commit()
    conn.close()
    print(f"Built {DB_PATH.relative_to(ROOT)}")
    print(f"  companies={n_co}  lead_scores={n_ls}  contacts={n_ct}  pipeline_events={n_pe}")
    print("Query it: python scripts/query_db.py   (or: sqlite3 data/leadgen.db)")


if __name__ == "__main__":
    main()
