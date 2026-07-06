"""Interactive single-file lead explorer → data/leads.html

Merges every per-company output (score, AI qualification, AI outreach draft,
contact) into one embedded dataset, and renders a standalone interactive page:
click a company to see all its details, plus search / service filter / verdict
filter / sort. No server, no dependencies — inline JS + data, so it's still a
shareable single file that opens in any browser.

    python scripts/webapp.py   →   data/leads.html
"""
from __future__ import annotations

import csv
import json

from _common import DATA_DIR

OUT = DATA_DIR / "leads.html"


def _read(name):
    p = DATA_DIR / name
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def build_dataset() -> list[dict]:
    db = {r["company_name"]: r for r in _read("companies_db.csv")}
    scores = {r["company_name"]: r for r in _read("scored_leads.csv")}
    final = {r["company_name"]: r for r in _read("final_leads.csv")}
    quals = {r["company_name"]: r for r in _read("qualified_leads.csv")}
    drafts = {r["company_name"]: r.get("message", "") for r in _read("outreach_drafts.csv")}
    contacts = {r["company_name"]: r for r in _read("contacts_worksheet.csv")}

    names = list(db) or list(scores)
    rows = []
    for name in names:
        d, s = db.get(name, {}), scores.get(name, {})
        fn, q, c = final.get(name, {}), quals.get(name, {}), contacts.get(name, {})
        rows.append({
            "company": name,
            "service": d.get("best_service", "") or fn.get("best_service", ""),
            "fit": float(fn.get("fit_score") or s.get("fit_score") or 0),
            "hiring": d.get("hiring_count", "") or s.get("hiring_count", ""),
            "industry": d.get("industry", "") or s.get("industry", ""),
            "tech": (d.get("tech_stack", "") or "").replace(";", ", "),
            "region": d.get("locations", ""),
            "url": d.get("source_url", "") or s.get("source_url", ""),
            "contact_name": fn.get("contact_name", "") or c.get("full_name", ""),
            "contact_title": fn.get("contact_title", "") or c.get("title", ""),
            "email": fn.get("email", "") or c.get("email", ""),
            "linkedin": fn.get("linkedin_url", "") or c.get("linkedin_url", ""),
            "verdict": q.get("verdict", ""),
            "confidence": q.get("confidence", ""),
            "reason": q.get("reason", ""),
            "message": drafts.get(name, ""),
        })
    rows.sort(key=lambda r: r["fit"], reverse=True)
    return rows


# Plain string (NOT an f-string / .format()) — only __DATA__ is substituted,
# so all CSS/JS braces are single.
HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Korea Lead-Gen — Leads</title><style>
  :root{--bd:#edeff3;--mut:#6b7280;--faint:#9ca3af;--ink:#111827;--accent:#4f46e5}
  *{box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#f4f5f8;color:var(--ink);margin:0;padding:32px 20px;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1120px;margin:0 auto}
  .head{margin-bottom:18px}
  h1{font-size:22px;font-weight:700;margin:0 0 3px;letter-spacing:-.01em}
  .sub{color:var(--mut);font-size:13px}
  .stats{display:flex;gap:12px;margin:16px 0}
  .stat{flex:1;background:#fff;border-radius:14px;padding:14px 18px;box-shadow:0 1px 3px rgba(16,24,40,.06)}
  .stat .n{font-size:22px;font-weight:700;letter-spacing:-.02em} .stat .l{font-size:11px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
  .tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
  input,select{padding:9px 12px;border:1px solid var(--bd);border-radius:10px;font-size:13px;background:#fff;color:var(--ink);outline:none}
  input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(79,70,229,.1)}
  input{flex:1;min-width:200px}
  .layout{display:flex;gap:16px;align-items:flex-start}
  .card{background:#fff;border-radius:16px;box-shadow:0 1px 3px rgba(16,24,40,.06),0 1px 2px rgba(16,24,40,.04)}
  .list{flex:1.1;overflow:hidden} .detail{flex:1;padding:22px 24px;position:sticky;top:32px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;color:var(--faint);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding:12px 16px;border-bottom:1px solid var(--bd);cursor:pointer;user-select:none}
  td{padding:12px 16px;border-bottom:1px solid #f4f5f7;vertical-align:middle}
  tr:last-child td{border-bottom:none}
  tr.row{cursor:pointer;transition:background .1s} tr.row:hover{background:#fafbfc} tr.sel{background:#f5f3ff;box-shadow:inset 3px 0 0 var(--accent)}
  .score{font-weight:700;color:var(--accent);font-size:15px}
  .chip{display:inline-block;background:#eef2ff;color:#4338ca;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:500}
  .pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600}
  .pill-fit{background:#dcfce7;color:#15803d} .pill-maybe{background:#fef3c7;color:#b45309} .pill-not_fit{background:#fee2e2;color:#b91c1c} .pill-{background:#f3f4f6;color:#9ca3af}
  .detail h2{font-size:18px;font-weight:700;margin:0 0 3px;letter-spacing:-.01em} .detail .meta{color:var(--mut);font-size:12px;margin-bottom:16px}
  .sec{margin:16px 0} .sec .lbl{font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-bottom:6px}
  .reason{font-size:13px;color:#374151;line-height:1.6;margin-top:6px}
  .msg{background:#f9fafb;border:1px solid var(--bd);border-radius:10px;padding:14px 16px;font-size:13px;line-height:1.7;white-space:pre-wrap;color:#374151}
  .kv{font-size:13px;line-height:1.9} .kv b{color:var(--ink)}
  .empty{color:var(--faint);font-size:12px}
  .joblink{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;padding:8px 16px;border-radius:10px;font-size:13px;font-weight:600;transition:background .1s}
  .joblink:hover{background:#4338ca}
  @media(max-width:820px){.layout{flex-direction:column}.detail{position:static}}
</style></head><body><div class="wrap">
  <div class="head"><h1>Korea Lead-Gen — Leads</h1>
    <div class="sub" id="summary"></div></div>
  <div class="stats" id="stats"></div>
  <div class="tools">
    <input id="q" placeholder="Search company…" oninput="render()">
    <select id="svc" onchange="render()"><option value="">All services</option></select>
    <select id="vd" onchange="render()">
      <option value="">All verdicts</option><option value="fit">✅ fit</option>
      <option value="maybe">🟡 maybe</option><option value="not_fit">❌ not_fit</option></select>
  </div>
  <div class="layout">
    <div class="card list"><table>
      <thead><tr><th onclick="sortBy('fit')">Fit ▾</th><th onclick="sortBy('company')">Company</th>
      <th>Service</th><th>Hires</th><th>Verdict</th></tr></thead>
      <tbody id="rows"></tbody></table></div>
    <div class="card detail" id="detail"></div>
  </div>
</div>
<script>
const DATA = __DATA__;
const SVC = {it_servicing:"IT Servicing", manpower:"Manpower", ai_implementation:"AI Implementation", systems_integration:"Systems Integration"};
const VICON = {fit:"✅", maybe:"🟡", not_fit:"❌"};
let sortKey="fit", sortDir=-1, selected=null;
const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;");
const svc = document.getElementById("svc"), q = document.getElementById("q"), vd = document.getElementById("vd");

[...new Set(DATA.map(d=>d.service).filter(Boolean))].forEach(s=>{
  const o=document.createElement("option");o.value=s;o.textContent=SVC[s]||s;svc.appendChild(o);});

function sortBy(k){ sortDir = (sortKey===k)? -sortDir : (k==="fit"?-1:1); sortKey=k; render(); }

function filtered(){
  const term=q.value.toLowerCase(), fs=svc.value, fv=vd.value;
  return DATA.filter(d=>(!term||d.company.toLowerCase().includes(term))
    &&(!fs||d.service===fs)&&(!fv||d.verdict===fv))
    .sort((a,b)=>{const x=a[sortKey],y=b[sortKey];return (x>y?1:x<y?-1:0)*sortDir;});
}

function pill(v){ return '<span class="pill pill-'+v+'">'+(VICON[v]||'')+' '+(v||'-')+'</span>'; }

function render(){
  const rows=filtered();
  document.getElementById("summary").textContent =
    "ICP-based scoring + AI qualification + AI outreach draft";
  const fitN = DATA.filter(d=>d.verdict==="fit").length;
  const avg = DATA.length ? Math.round(DATA.reduce((a,d)=>a+d.fit,0)/DATA.length) : 0;
  document.getElementById("stats").innerHTML =
    '<div class="stat"><div class="n">'+DATA.length+'</div><div class="l">Leads</div></div>'
   +'<div class="stat"><div class="n">'+fitN+'</div><div class="l">AI-qualified fit</div></div>'
   +'<div class="stat"><div class="n">'+avg+'</div><div class="l">Avg fit score</div></div>'
   +'<div class="stat"><div class="n">'+rows.length+'</div><div class="l">Showing</div></div>';
  document.getElementById("rows").innerHTML = rows.map(d=>
    '<tr class="row '+(selected===d.company?'sel':'')+'" onclick="select(\\''+d.company.replace(/'/g,"\\\\'")+'\\')">'
    +'<td class="score">'+Math.round(d.fit)+'</td><td><b>'+esc(d.company)+'</b></td>'
    +'<td><span class="chip">'+(SVC[d.service]||d.service||'-')+'</span></td>'
    +'<td>'+(d.hiring||'-')+'</td>'
    +'<td>'+pill(d.verdict)+'</td></tr>').join("")
    || '<tr><td colspan=5 class="empty" style="padding:24px;text-align:center">No matches.</td></tr>';
  if(rows.length && !rows.find(r=>r.company===selected)) select(rows[0].company); else drawDetail();
}

function select(name){ selected=name; render(); }

function drawDetail(){
  const d = DATA.find(x=>x.company===selected);
  const el=document.getElementById("detail");
  if(!d){ el.innerHTML='<div class="empty">Select a lead.</div>'; return; }
  const contact = d.contact_name
    ? '<div class="kv"><b>'+esc(d.contact_name)+'</b> '+esc(d.contact_title)+'<br>'
      +(d.email?esc(d.email)+"<br>":"")+(d.linkedin?esc(d.linkedin):"")+'</div>'
    : '<div class="empty">No decision-maker contact yet.</div>';
  const link = d.url ? '<a class="joblink" href="'+esc(d.url)+'" target="_blank" rel="noopener">🔗 View job posting →</a>' : '';
  el.innerHTML =
    '<h2>'+esc(d.company)+'</h2>'
    +'<div class="meta">'+esc(d.industry)+' · '+esc(d.region)+' · '+(d.hiring||0)+' openings</div>'
    +(link?'<div class="sec">'+link+'</div>':'')
    +'<div class="sec"><div class="lbl">Fit score</div>'
      +'<span class="score" style="font-size:22px">'+Math.round(d.fit)+'</span> / 100 '
      +'&nbsp;<span class="chip">'+(SVC[d.service]||d.service||'-')+'</span></div>'
    +'<div class="sec"><div class="lbl">🤖 AI qualification</div>'
      +pill(d.verdict)+' <span class="empty">('+(d.confidence||'-')+')</span>'
      +'<div class="reason">'+(esc(d.reason)||'<span class=empty>not qualified yet</span>')+'</div></div>'
    +'<div class="sec"><div class="lbl">Tech stack</div><div class="kv">'+(esc(d.tech)||'<span class=empty>—</span>')+'</div></div>'
    +'<div class="sec"><div class="lbl">Contact</div>'+contact+'</div>'
    +'<div class="sec"><div class="lbl">✉️ AI outreach draft</div>'
      +(d.message?'<div class="msg">'+esc(d.message)+'</div>':'<div class="empty">no draft yet — run generate_messages.py</div>')+'</div>';
}
render();
</script></body></html>"""


def main() -> None:
    data = build_dataset()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    DATA_DIR.mkdir(exist_ok=True)
    OUT.write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(DATA_DIR.parent)} — {len(data)} leads. "
          f"Open it / share it (single file, click a company for details).")


if __name__ == "__main__":
    main()
