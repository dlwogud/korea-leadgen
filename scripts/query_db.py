"""Run useful SQL queries against the SQLite DB — proves it's a real, queryable
database (not just CSVs). Run after build_db.py.

    python scripts/query_db.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "leadgen.db"


def show(title: str, conn, sql: str) -> None:
    print(f"\n## {title}")
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print("  " + " | ".join(cols))
    print("  " + "-" * 56)
    for r in rows:
        print("  " + " | ".join("" if v is None else str(v) for v in r))


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("No data/leadgen.db — run: python scripts/build_db.py")
    conn = sqlite3.connect(DB_PATH)

    show("Top 10 leads by score", conn, """
        SELECT company_name, best_service, fit_score, hiring_count
        FROM v_top_leads LIMIT 10;
    """)

    show("Lead count by best-fit service", conn, """
        SELECT best_service, COUNT(*) AS companies,
               ROUND(AVG(fit_it_servicing),1) AS avg_it_fit
        FROM companies GROUP BY best_service ORDER BY companies DESC;
    """)

    show("Reachable leads (have a contact)", conn, """
        SELECT c.company_name, ct.full_name, ct.title,
               CASE WHEN ct.email <> '' THEN 'email'
                    WHEN ct.linkedin_url <> '' THEN 'linkedin' ELSE 'name' END AS channel
        FROM contacts ct JOIN companies c ON c.company_name = ct.company_name;
    """)

    show("KPI funnel — leads reaching each stage", conn, """
        SELECT s.ord+1 AS step, s.stage,
               (SELECT COUNT(*) FROM v_lead_furthest f WHERE f.furthest_ord >= s.ord) AS leads
        FROM stages s ORDER BY s.ord;
    """)

    conn.close()
    print("\n(These run on data/leadgen.db — a real SQLite database.)")


if __name__ == "__main__":
    main()
