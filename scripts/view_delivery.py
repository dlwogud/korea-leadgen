"""Render delivery.csv as a clean, in-browser sheet view (data/delivery.html).

The delivery CSV is the artifact the outreach team pastes into Google Sheets.
This makes a read-only HTML table of the SAME data so it opens nicely from a
shared link (a raw .csv just downloads). Regenerate after export_delivery.py.

    python scripts/view_delivery.py   →   data/delivery.html
"""
from __future__ import annotations

import csv
import html

from _common import DATA_DIR

SRC = DATA_DIR / "delivery.csv"
OUT = DATA_DIR / "delivery.html"

# columns to show as compact table cells (outreach_message gets its own wide cell)
COLS = [
    ("company_name", "Company"), ("best_service", "Service"),
    ("fit_score", "Fit"), ("hiring_count", "Hires"),
    ("industry", "Industry"), ("tech_stack", "Tech stack"),
]

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Korea Lead-Gen — Delivery Sheet</title><style>
  *{box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1a1a2e;padding:24px}
  h1{font-size:20px;margin:0 0 4px} .sub{color:#6b7280;font-size:13px;margin-bottom:18px}
  .wrap{background:#fff;border-radius:14px;box-shadow:0 1px 3px rgba(16,24,40,.06);overflow:hidden}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;color:#6b7280;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding:11px 14px;border-bottom:1px solid #e5e7eb;background:#fafafa;position:sticky;top:0}
  td{padding:11px 14px;border-bottom:1px solid #f4f5f7;vertical-align:top}
  tr:last-child td{border-bottom:none}
  .name{font-weight:600}
  .pill{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;background:#eef2ff;color:#4338ca}
  .msg{font-size:12px;line-height:1.6;color:#374151;max-width:520px;white-space:pre-wrap;max-height:120px;overflow:auto;background:#f9fafb;border:1px solid #eef0f2;border-radius:8px;padding:8px 10px}
  .empty{color:#c0c4cc}
</style></head><body>
<h1>Delivery Sheet — Korea Lead-Gen</h1>
<div class="sub">__N__ leads · ranked by fit · outreach drafts by Claude. Read-only view of the team CSV.</div>
<div class="wrap"><table><thead><tr>__HEAD__<th>Outreach draft</th></tr></thead><tbody>
__ROWS__
</tbody></table></div>
</body></html>"""


def main() -> None:
    with SRC.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: float(r.get("fit_score") or 0), reverse=True)

    head = "".join(f"<th>{label}</th>" for _, label in COLS)
    out_rows = []
    for r in rows:
        cells = []
        for key, _ in COLS:
            v = html.escape(r.get(key, "") or "")
            if key == "best_service" and v:
                v = f'<span class="pill">{v}</span>'
            if key == "company_name":
                v = f'<span class="name">{v}</span>'
            cells.append(f"<td>{v or '<span class=empty>—</span>'}</td>")
        msg = html.escape(r.get("outreach_message", "") or "")
        msg_cell = f'<div class="msg">{msg}</div>' if msg else '<span class="empty">— (no draft yet)</span>'
        out_rows.append(f"<tr>{''.join(cells)}<td>{msg_cell}</td></tr>")

    page = (PAGE.replace("__N__", str(len(rows)))
                .replace("__HEAD__", head)
                .replace("__ROWS__", "\n".join(out_rows)))
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} — {len(rows)} leads (in-browser sheet view).")


if __name__ == "__main__":
    main()
