"""Generate a single at-a-glance HTML overview — top leads + service mix + funnel.

One page to screenshot for Discord / show the mentor. Run after the pipeline
(or just run demo.py, which calls this).

    python scripts/overview.py     →     data/overview.html
"""
from __future__ import annotations

import csv
from pathlib import Path

from dashboard import compute_funnel

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "overview.html"

SERVICE_LABELS = {
    "it_servicing": "IT Servicing",
    "manpower": "Manpower",
    "ai_implementation": "AI Implementation",
    "systems_integration": "Systems Integration",
}


def _read(name):
    p = DATA / name
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def main() -> None:
    leads = _read("scored_leads.csv")
    funnel = compute_funnel()
    drafts = _read("outreach_drafts.csv")
    quals = _read("qualified_leads.csv")

    # top leads rows
    top_rows = ""
    for i, r in enumerate(leads[:8], 1):
        top_rows += f"""<tr>
          <td>{i}</td><td><b>{r.get('company_name','')}</b></td>
          <td>{SERVICE_LABELS.get(r.get('best_service',''), r.get('best_service',''))}</td>
          <td class="score">{r.get('fit_score','')}</td>
          <td>{r.get('hiring_count','')}</td>
          <td class="tech">{(r.get('tech_stack','') or '').replace(';', ', ')}</td>
        </tr>"""

    # service mix
    mix = {}
    for r in leads:
        mix[r.get("best_service", "")] = mix.get(r.get("best_service", ""), 0) + 1
    mix_chips = "".join(
        f'<span class="chip">{SERVICE_LABELS.get(k,k)}: <b>{v}</b></span>'
        for k, v in sorted(mix.items(), key=lambda x: -x[1]) if k)

    # AI qualification (verdicts + reasons)
    qual_html = ""
    if quals:
        icon = {"fit": "✅", "maybe": "🟡", "not_fit": "❌"}
        items = ""
        for q in quals[:5]:
            v = q.get("verdict", "")
            reason = (q.get("reason", "") or "").replace("<", "&lt;")
            items += (f'<div class="qrow"><span class="qbadge">{icon.get(v,"?")} '
                      f'{q.get("company_name","")}</span> '
                      f'<span class="qconf">{v} · {q.get("confidence","")}</span>'
                      f'<div class="qreason">{reason}</div></div>')
        qual_html = f"""
  <div class="card"><h2>🤖 AI lead qualification <span class="mode">(Claude)</span></h2>
    <div class="draftmeta">Claude judges each company against the ICP, with a reason.</div>
    {items}
  </div>"""

    # outreach draft (show the top one)
    draft_html = ""
    if drafts:
        d = drafts[0]
        body = (d.get("message", "") or "").replace("<", "&lt;").replace("\n", "<br>")
        draft_html = f"""
  <div class="card"><h2>✉️ Sample AI-drafted outreach <span class="mode">({d.get('mode','')})</span></h2>
    <div class="draftmeta">{d.get('company_name','')} · fit {d.get('fit_score','')} · {d.get('service','')}
      <span class="badge">DRAFT — needs approval before sending</span></div>
    <div class="draft">{body}</div>
  </div>"""

    # funnel bars
    top = funnel[0]["count"] or 1
    fbars = ""
    for i, f in enumerate(funnel):
        pct = f["count"] / top * 100
        conv = "" if i == 0 else f'<span class="conv">{f["conversion"]:.0f}%</span>'
        fbars += f"""<div class="frow">
          <div class="flabel">{f['label']}</div>
          <div class="ftrack"><div class="fbar" style="width:{max(pct,2):.1f}%"></div></div>
          <div class="fnum">{f['count']} {conv}</div></div>"""

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Korea Lead-Gen — Overview</title><style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#f6f7f9;color:#1f2430;margin:0;padding:32px}}
  .wrap{{max-width:860px;margin:0 auto}}
  h1{{font-size:21px;margin:0 0 2px}} .sub{{color:#6b7280;font-size:13px;margin-bottom:18px}}
  .card{{background:#fff;border-radius:14px;padding:22px 26px;box-shadow:0 2px 14px rgba(0,0,0,.06);margin-bottom:18px}}
  h2{{font-size:14px;margin:0 0 12px;color:#374151}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{text-align:left;color:#9aa1ad;font-weight:600;padding:4px 8px;border-bottom:1px solid #eee}}
  td{{padding:7px 8px;border-bottom:1px solid #f3f4f6}}
  .score{{font-weight:700;color:#2563eb}} .tech{{color:#6b7280;font-size:12px}}
  .chip{{display:inline-block;background:#eef2ff;color:#3730a3;border-radius:20px;padding:5px 12px;font-size:12px;margin:0 6px 6px 0}}
  .frow{{display:flex;align-items:center;gap:12px;margin:7px 0}}
  .flabel{{width:160px;font-size:12px}} .ftrack{{flex:1;background:#eef1f5;border-radius:6px;height:20px;overflow:hidden}}
  .fbar{{height:100%;background:linear-gradient(90deg,#3b82f6,#2563eb);border-radius:6px}}
  .fnum{{width:90px;font-size:12px;font-weight:600}} .conv{{color:#9aa1ad;font-weight:400;font-size:11px}}
  .mode{{color:#9aa1ad;font-weight:400;font-size:12px}}
  .draftmeta{{font-size:12px;color:#6b7280;margin-bottom:8px}}
  .badge{{background:#fef3c7;color:#92400e;border-radius:6px;padding:2px 8px;font-size:11px;margin-left:6px}}
  .draft{{background:#f8fafc;border:1px solid #eef1f5;border-radius:8px;padding:14px 16px;font-size:13px;line-height:1.7;white-space:normal}}
  .qrow{{padding:8px 0;border-bottom:1px solid #f3f4f6}}
  .qbadge{{font-size:13px;font-weight:600}} .qconf{{color:#9aa1ad;font-size:11px;margin-left:6px}}
  .qreason{{font-size:12px;color:#6b7280;margin-top:3px;line-height:1.5}}
</style></head><body><div class="wrap">
  <h1>Korea Lead-Gen — Overview</h1>
  <div class="sub">ICP-based sourcing → scoring → funnel. Sample data (same with the live API key).</div>

  <div class="card"><h2>🎯 Top leads (ranked by fit)</h2>
    <table><tr><th>#</th><th>Company</th><th>Best-fit service</th><th>Fit</th><th>Hires</th><th>Tech stack</th></tr>
    {top_rows}</table></div>

  <div class="card"><h2>🧩 Leads by best-fit service</h2>{mix_chips}</div>
{qual_html}
{draft_html}
  <div class="card"><h2>📊 KPI funnel</h2>{fbars}</div>
</div></body></html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(DATA.parent)} — open it / screenshot for Discord.")


if __name__ == "__main__":
    main()
