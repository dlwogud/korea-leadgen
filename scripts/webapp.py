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
            "roles": (d.get("sample_titles", "") or s.get("sample_titles", "") or "").replace(";", ", "),
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
    # rank by fit score, then verdict (fit > maybe > not_fit) as the tie-breaker
    _vrank = {"fit": 3, "maybe": 2, "not_fit": 1}
    rows.sort(key=lambda r: (r["fit"], _vrank.get(r["verdict"], 0)), reverse=True)
    return rows


# Plain string (NOT an f-string / .format()) — only __DATA__ is substituted,
# so all CSS/JS braces are single.
HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Korea Lead-Gen — Leads</title><style>
  :root{
    --page:#F9F8F7;--surface:#FFFFFF;--card:#F4F3F1;--line:#E0DFDD;
    --ink:#111111;--ink-mid:#52514E;--ink-mute:#888780;
    --accent:#3778D6;--brand-bg:#E6F1FC;--brand-600:#2A5FB0;
    --positive-700:#0E7D56;--positive-bg:#EAF9DE;--warn-700:#9A6B00;--warn-bg:#FAEEDA;
    --bd:#E0DFDD;--mut:#52514E;--faint:#888780;
  }
  *{box-sizing:border-box}
  body{font-family:Inter,"Apple SD Gothic Neo","Noto Sans KR",system-ui,-apple-system,sans-serif;font-size:13px;background:var(--page);color:var(--ink);margin:0;padding:32px 20px;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1120px;margin:0 auto}
  .head{margin-bottom:18px}
  h1{font-size:20px;font-weight:600;margin:0 0 3px;letter-spacing:-.01em}
  .sub{color:var(--mut);font-size:13px}
  .stats{display:flex;gap:12px;margin:16px 0}
  .stat{flex:1;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 18px}
  .stat .n{font-size:24px;font-weight:600;letter-spacing:-.01em;font-variant-numeric:tabular-nums} .stat .l{font-size:10px;color:var(--ink-mute);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
  .tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
  input,select{padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:var(--surface);color:var(--ink);outline:none}
  input:focus,select:focus{border-color:var(--accent)}
  input{flex:1;min-width:200px}
  .layout{display:flex;gap:16px;align-items:flex-start}
  .card{background:var(--surface);border:1px solid var(--line);border-radius:12px}
  .list{flex:1.1;max-height:78vh;overflow-y:auto} .detail{flex:1;padding:22px 24px;position:sticky;top:32px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;color:var(--ink-mute);font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:.04em;padding:12px 16px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;position:sticky;top:0;background:var(--surface);z-index:1}
  td{padding:12px 16px;border-bottom:1px solid var(--line);vertical-align:middle;font-variant-numeric:tabular-nums}
  tr:last-child td{border-bottom:none}
  tr.row{cursor:pointer;transition:background .1s} tr.row:hover{background:var(--card)} tr.sel{background:var(--brand-bg);box-shadow:inset 3px 0 0 var(--accent)}
  .score{font-weight:600;color:var(--accent);font-size:15px;font-variant-numeric:tabular-nums}
  .chip{display:inline-block;background:var(--brand-bg);color:var(--brand-600);border-radius:4px;padding:2px 6px;font-size:10px;font-weight:500}
  .pill{display:inline-block;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:500}
  .pill-fit{background:var(--positive-bg);color:var(--positive-700)} .pill-maybe{background:var(--warn-bg);color:var(--warn-700)} .pill-not_fit{background:#FBE9E9;color:#B42318} .pill-{background:var(--card);color:var(--ink-mute)}
  .detail h2{font-size:18px;font-weight:600;margin:0 0 3px;letter-spacing:-.01em} .detail .meta{color:var(--mut);font-size:12px;margin-bottom:16px}
  .sec{margin:16px 0} .sec .lbl{font-size:10px;color:var(--ink-mute);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-bottom:6px}
  .reason{font-size:13px;color:var(--ink-mid);line-height:1.6;margin-top:6px}
  .msg{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;font-size:13px;line-height:1.7;white-space:pre-wrap;color:var(--ink-mid)}
  textarea.msg{width:100%;min-height:190px;resize:vertical;font-family:inherit;outline:none;display:block}
  textarea.msg:focus{border-color:var(--accent)}
  .draftbar{display:flex;gap:8px;margin-top:8px}
  .copybtn{padding:6px 14px;border:none;border-radius:8px;background:var(--accent);color:#fff;font-size:12px;font-weight:500;cursor:pointer}
  .resetbtn{padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink-mid);font-size:12px;cursor:pointer}
  .kv{font-size:13px;line-height:1.9} .kv b{color:var(--ink)}
  .empty{color:var(--ink-mute);font-size:12px}
  .joblink{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:500;transition:background .1s}
  .joblink:hover{background:var(--brand-600)}
  @media(max-width:820px){.layout{flex-direction:column}.detail{position:static}}
</style></head><body><div class="wrap">
  <div class="head"><h1>Korea Lead-Gen — Leads</h1>
    <div class="sub" id="summary"></div></div>
  <div class="stats" id="stats"></div>
  <div class="tools">
    <input id="q" placeholder="Search company, industry, tech… (typo-tolerant)" oninput="render()">
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
let EDITS = {};
try { EDITS = JSON.parse(localStorage.getItem("km_edits") || "{}"); } catch(e) { EDITS = {}; }
function curDraft(){ if(EDITS[selected]!=null) return EDITS[selected]; const d=DATA.find(x=>x.company===selected); return (d&&d.message)||""; }
function saveEdit(v){ EDITS[selected]=v; try{ localStorage.setItem("km_edits", JSON.stringify(EDITS)); }catch(e){} }
function resetDraft(){ delete EDITS[selected]; try{ localStorage.setItem("km_edits", JSON.stringify(EDITS)); }catch(e){} drawDetail(); }
function copyDraft(btn){ const t=curDraft(); navigator.clipboard.writeText(t).then(()=>{ const o=btn.textContent; btn.textContent="✓ Copied"; setTimeout(()=>btn.textContent=o,1200); }).catch(()=>{}); }
function editableDraft(){
  return '<textarea class="msg" spellcheck="false" oninput="saveEdit(this.value)">'+esc(curDraft())+'</textarea>'
    +'<div class="draftbar"><button class="copybtn" onclick="copyDraft(this)">📋 Copy</button>'
    +'<button class="resetbtn" onclick="resetDraft()">Reset to AI draft</button></div>';
}
const SVC = {it_servicing:"IT Servicing", manpower:"Manpower", ai_implementation:"AI Implementation", systems_integration:"Systems Integration"};
const VICON = {fit:"✅", maybe:"🟡", not_fit:"❌"};
let sortKey="fit", sortDir=-1, selected=null;
const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;");
const svc = document.getElementById("svc"), q = document.getElementById("q"), vd = document.getElementById("vd");

[...new Set(DATA.map(d=>d.service).filter(Boolean))].forEach(s=>{
  const o=document.createElement("option");o.value=s;o.textContent=SVC[s]||s;svc.appendChild(o);});

function sortBy(k){ sortDir = (sortKey===k)? -sortDir : (k==="fit"?-1:1); sortKey=k; render(); }

// Levenshtein edit distance (for typo tolerance)
function lev(a,b){
  const m=a.length,n=b.length; if(!m)return n; if(!n)return m;
  let prev=Array.from({length:n+1},(_,i)=>i);
  for(let i=1;i<=m;i++){ const cur=[i];
    for(let j=1;j<=n;j++){ cur[j]=Math.min(prev[j]+1,cur[j-1]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1)); }
    prev=cur; }
  return prev[n];
}
// Korean role/tech term -> English alias, so English searches hit Korean data
const ALIAS = {"데이터 엔지니어":"data engineer","데이터엔지니어":"data engineer",
  "백엔드":"backend","프론트엔드":"frontend","서버 개발":"server developer","서버":"server",
  "데브옵스":"devops","기술지원":"technical support","고객지원":"customer support cs","운영":"operations ops",
  "머신러닝":"machine learning ml","테스트":"qa test","개발자":"developer","시스템 엔지니어":"system engineer",
  "핀테크":"fintech","이커머스":"ecommerce","게임":"gaming game","보안":"security","물류":"logistics","제조":"manufacturing"};
// all searchable text: name + industry + tech + service + region + job roles (+ English aliases)
function hay(d){
  let t = (d.company+' '+(d.industry||'')+' '+(d.tech||'')+' '+(SVC[d.service]||d.service||'')+' '+d.service+' '+(d.region||'')+' '+(d.roles||'')).toLowerCase();
  for(const k in ALIAS){ if(t.indexOf(k.toLowerCase())>=0) t += ' '+ALIAS[k]; }
  return t;
}
// fuzzy substring: slide a window over the text and compare each to the term
function fuzzyHas(text,term){
  if(text.includes(term)) return true;
  const L=term.length, max = L<=2?0 : (L<=5?1:2);
  if(max===0) return false;
  for(let i=0;i<=text.length-1;i++){
    for(let w=Math.max(1,L-max); w<=L+max; w++){
      if(i+w>text.length) continue;
      if(lev(text.substr(i,w),term)<=max) return true;
    }
  }
  return false;
}
// match: exact across all fields, OR typo-tolerant on the company name
function matches(d,term){
  if(!term) return true;
  return hay(d).includes(term) || fuzzyHas(d.company.toLowerCase(), term);
}

function filtered(){
  const term=q.value.toLowerCase().trim(), fs=svc.value, fv=vd.value;
  return DATA.filter(d=> matches(d,term) && (!fs||d.service===fs) && (!fv||d.verdict===fv))
    .sort((a,b)=>{const x=a[sortKey],y=b[sortKey]; if(x!==y) return (x>y?1:-1)*sortDir; const VR={fit:3,maybe:2,not_fit:1}; return (VR[b.verdict]||0)-(VR[a.verdict]||0);});
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
    +'<div class="sec"><div class="lbl">✉️ AI outreach draft (editable)</div>'
      +(d.message?editableDraft():'<div class="empty">no draft yet — run generate_messages.py</div>')+'</div>';
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
