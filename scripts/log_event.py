"""Record a lead moving through the 8-stage funnel (playbook §6.1).

Each call appends one row to data/pipeline_events.csv. The dashboard reads
these to show stage-by-stage conversion. This is the manual touch-point: when
a reply comes in or a call is booked, log it here (or wire it to email later).

Run:
    python scripts/log_event.py --company "온누리페이" --service it_servicing --stage outreach_sent
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone

from _common import DATA_DIR, ensure_data_dir

EVENTS_CSV = DATA_DIR / "pipeline_events.csv"
EVENT_FIELDS = ["company_name", "service", "stage", "entered_at", "note"]

STAGES = [
    "target_identified", "contact_identified", "outreach_sent", "reply_received",
    "call_booked", "call_held", "concrete_interest", "korea_visit_ready",
]
SERVICES = ["it_servicing", "systems_integration", "ai_implementation", "manpower_placement"]


def append_event(company: str, service: str, stage: str, note: str = "") -> None:
    ensure_data_dir()
    new_file = not EVENTS_CSV.exists()
    with EVENTS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "company_name": company,
            "service": service,
            "stage": stage,
            "entered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": note,
        })


def main() -> None:
    parser = argparse.ArgumentParser(description="Log a funnel event for a lead.")
    parser.add_argument("--company", required=True)
    parser.add_argument("--service", required=True, choices=SERVICES)
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    append_event(args.company, args.service, args.stage, args.note)
    print(f"Logged: {args.company} → {args.stage} ({args.service})")


if __name__ == "__main__":
    main()
