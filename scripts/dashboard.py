"""Render the KPI funnel (playbook §6.1) from logged pipeline events.

Computes, per (company, service), the furthest stage reached, then how many
leads reached each stage and the stage-to-stage conversion rate. Outputs:
  - a terminal funnel
  - data/dashboard.html  (self-contained, open in a browser — good for the capstone)

Run:  python scripts/dashboard.py
"""
from __future__ import annotations

import csv

from _common import DATA_DIR

EVENTS_CSV = DATA_DIR / "pipeline_events.csv"
DASHBOARD_HTML = DATA_DIR / "dashboard.html"

STAGES = [
    ("target_identified", "1. Target identified"),
    ("contact_identified", "2. Contact identified"),
    ("outreach_sent", "3. Outreach sent"),
    ("reply_received", "4. Reply received"),
    ("call_booked", "5. Call booked"),
    ("call_held", "6. Call held"),
    ("concrete_interest", "7. Concrete interest"),
    ("korea_visit_ready", "8. Korea-visit ready"),
]
STAGE_INDEX = {name: i for i, (name, _) in enumerate(STAGES)}


def compute_funnel() -> list[dict]:
    """Return per-stage count + conversion from previous stage."""
    if not EVENTS_CSV.exists():
        raise SystemExit("No pipeline_events.csv yet. Log events with log_event.py first.")

    # furthest stage index per (company, service)
    furthest: dict[tuple, int] = {}
    with EVENTS_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stage = row.get("stage", "")
            if stage not in STAGE_INDEX:
                continue
            key = (row.get("company_name", ""), row.get("service", ""))
            idx = STAGE_INDEX[stage]
            furthest[key] = max(furthest.get(key, -1), idx)

    # count of leads that reached AT LEAST each stage
    counts = []
    for i, (name, label) in enumerate(STAGES):
        counts.append(sum(1 for v in furthest.values() if v >= i))

    rows = []
    for i, (name, label) in enumerate(STAGES):
        prev = counts[i - 1] if i > 0 else None
        conv = (counts[i] / prev * 100) if prev else (100.0 if i == 0 else 0.0)
        rows.append({"label": label, "count": counts[i], "conversion": conv})
    return rows


def print_terminal(rows: list[dict]) -> None:
    top = rows[0]["count"] or 1
    print("\nKPI Funnel\n" + "=" * 52)
    for i, r in enumerate(rows):
        bar = "█" * int(round(r["count"] / top * 30))
        conv = "" if i == 0 else f"  ({r['conversion']:.0f}% of prev)"
        print(f"{r['label']:<22} {bar} {r['count']}{conv}")
    overall = rows[-1]["count"] / top * 100
    print("=" * 52)
    print(f"Overall: {rows[-1]['count']}/{rows[0]['count']} reached the final stage ({overall:.0f}%)\n")


def render_html(rows: list[dict]) -> str:
    top = rows[0]["count"] or 1
    bars = []
    for i, r in enumerate(rows):
        pct = r["count"] / top * 100
        conv = "" if i == 0 else f'<span class="conv">{r["conversion"]:.0f}% of previous</span>'
        bars.append(f"""
      <div class="row">
        <div class="label">{r['label']}</div>
        <div class="track"><div class="bar" style="width:{max(pct,2):.1f}%"></div></div>
        <div class="num">{r['count']} {conv}</div>
      </div>""")
    overall = rows[-1]["count"] / top * 100
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Korea Lead-Gen — KPI Funnel</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; background:#f6f7f9;
         color:#1f2430; margin:0; padding:40px; }}
  .card {{ max-width:760px; margin:0 auto; background:#fff; border-radius:14px;
          padding:32px 36px; box-shadow:0 2px 14px rgba(0,0,0,.06); }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  .sub {{ color:#6b7280; font-size:13px; margin-bottom:24px; }}
  .row {{ display:flex; align-items:center; gap:14px; margin:10px 0; }}
  .label {{ width:180px; font-size:13px; }}
  .track {{ flex:1; background:#eef1f5; border-radius:6px; height:24px; overflow:hidden; }}
  .bar {{ height:100%; background:linear-gradient(90deg,#3b82f6,#2563eb); border-radius:6px; }}
  .num {{ width:170px; font-size:13px; font-weight:600; }}
  .conv {{ font-weight:400; color:#9aa1ad; font-size:11px; margin-left:4px; }}
  .footer {{ margin-top:22px; padding-top:16px; border-top:1px solid #eee;
            font-size:13px; color:#374151; }}
</style></head>
<body><div class="card">
  <h1>Korea Lead-Gen — KPI Funnel</h1>
  <div class="sub">Leads reaching each stage (playbook §6.1). Auto-generated from pipeline events.</div>
  {''.join(bars)}
  <div class="footer">Overall: <b>{rows[-1]['count']} / {rows[0]['count']}</b>
    leads reached the final stage (<b>{overall:.0f}%</b>).</div>
</div></body></html>"""


def main() -> None:
    rows = compute_funnel()
    print_terminal(rows)
    DASHBOARD_HTML.write_text(render_html(rows), encoding="utf-8")
    print(f"Wrote data/dashboard.html — open it in a browser.")


if __name__ == "__main__":
    main()
