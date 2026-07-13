"""Live pipeline — the SARAMIN (licensed) path.

The DEFAULT source is Wanted — use scripts/daily_wanted.sh (see docs/AUTOMATION.md).
This script is the equivalent for teams that have LICENSED the Saramin API: same
enrich → score → AI qualify/draft → delivery outputs, just sourced from Saramin.

Once SARAMIN_API_KEY is in .env, it runs the whole thing on real Saramin postings:
  source (Saramin) → enrich → score → contact worksheet → AI qualify + draft
  → delivery sheet → interactive app → DB

Set ANTHROPIC_API_KEY too for the AI steps (qualify + outreach drafts).

    # first live run — confirm Saramin's field mapping, and start clean:
    python scripts/source_saramin.py --debug          # verify response once
    python scripts/run_live.py --fresh

    # normal / scheduled run:
    python scripts/run_live.py --ai-top 10
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from _common import DATA_DIR, load_dotenv

HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> None:
    print(f"\n=== {script} {' '.join(args)} ===", flush=True)
    r = subprocess.run([sys.executable, str(HERE / script), *args])
    if r.returncode != 0:
        sys.exit(f"step failed: {script}")


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(description="Run the live pipeline on real Saramin data.")
    ap.add_argument("--pages", default="3", help="Saramin pages per query")
    ap.add_argument("--service", choices=["it_servicing", "manpower", "ai_implementation", "systems_integration"],
                    help="source only this service's ICP keywords")
    ap.add_argument("--job-mid-cd", help="Saramin IT category code (from --list-categories)")
    ap.add_argument("--ai-top", type=int, default=10,
                    help="how many top leads to AI-qualify + draft (0 = skip AI to save cost)")
    ap.add_argument("--fresh", action="store_true",
                    help="clear the accumulated DB first (use on the first live run to drop sample data)")
    args = ap.parse_args()

    if not os.getenv("SARAMIN_API_KEY"):
        sys.exit("ERROR: set SARAMIN_API_KEY in .env first (get it at https://oapi.saramin.co.kr).")

    if args.fresh:
        for f in ("companies_db.csv", "final_leads.csv", "leadgen.db"):
            (DATA_DIR / f).unlink(missing_ok=True)
        print("[fresh] cleared accumulated DB (starting clean on real data)")

    # 1. Source real postings
    src = ["--pages", args.pages]
    if args.job_mid_cd:
        src += ["--job-mid-cd", args.job_mid_cd]
    elif args.service:
        src += ["--service", args.service]
    run("source_saramin.py", *src)

    # 2-3. Enrich + score
    run("enrich.py")
    run("score_leads.py")

    # 4. Contact research worksheet (manual step happens here — team fills it)
    run("make_contact_worksheet.py", "--top", "30")

    # 5. AI steps (cost per lead — capped by --ai-top; skipped if no key)
    if args.ai_top > 0 and os.getenv("ANTHROPIC_API_KEY"):
        run("qualify_leads.py", "--top", str(args.ai_top))
        run("generate_messages.py", "--top", str(args.ai_top))
    elif args.ai_top > 0:
        print("[skip AI] no ANTHROPIC_API_KEY set — scoring only")

    # 6. Outputs the team uses
    run("export_delivery.py")
    run("overview.py")
    run("webapp.py")
    run("build_db.py")

    print("\n" + "#" * 60)
    print("LIVE RUN COMPLETE — updated:")
    print("  • data/delivery.csv   → paste into the shared Google Sheet")
    print("  • data/leads.html     → interactive lead explorer")
    print("  • data/leadgen.db     → queryable database (with history)")
    print("#" * 60)


if __name__ == "__main__":
    main()
