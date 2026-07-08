"""Consolidated team platform — the merged 'best of' single-file app.

Combines the team's strengths into ONE navigable platform (no server needed):
  • Overview     — KPIs at a glance + honesty note
  • Pipeline     — CRM table: priority (High/Med/Low), AI verdict, status, detail
  • KPI Funnel   — the playbook's 8-stage funnel (real events only)
  • Outreach     — Claude EN/KR drafts + Jake→Mel→Rey approval workflow
  • Recommendation — Go / Pilot / No-Go, data-driven

Data comes from the same pipeline (build_dataset). Contact/evidence columns are
left ready for the crawled contact data to plug in.

    python scripts/platform.py   →   data/platform.html
"""
from __future__ import annotations

import csv
import json

from _common import DATA_DIR
from webapp import build_dataset


def _employees() -> dict:
    p = DATA_DIR / "companies_db.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        return {r["company_name"]: r.get("employees", "") for r in csv.DictReader(f)}


HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Korea Market Activation Platform</title><style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{--accent:#4f46e5;--bd:#e5e7eb;--ink:#111827;--faint:#6b7280;--bg:#f6f7f9}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--ink);display:flex;min-height:100vh}
  /* sidebar */
  .side{width:230px;background:#0f1222;color:#cbd5e1;padding:22px 14px;position:fixed;height:100vh;overflow:auto}
  .brand{color:#fff;font-weight:700;font-size:15px;line-height:1.3;padding:0 8px 4px}
  .brand small{display:block;color:#8b93a7;font-weight:500;font-size:11px;margin-top:3px}
  .nav{margin-top:20px;display:flex;flex-direction:column;gap:4px}
  .nav a{color:#cbd5e1;text-decoration:none;padding:10px 12px;border-radius:9px;font-size:13.5px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:9px}
  .nav a:hover{background:#1c2135}
  .nav a.on{background:var(--accent);color:#fff}
  .side .foot{margin-top:22px;padding:12px 8px;color:#6b7280;font-size:11px;line-height:1.5;border-top:1px solid #232842}
  /* main */
  .main{margin-left:230px;flex:1;padding:28px 34px;max-width:1150px}
  h1{font-size:22px;margin-bottom:3px} .sub{color:var(--faint);font-size:13px;margin-bottom:22px}
  h2{font-size:15px;margin:0 0 14px}
  section{display:none} section.on{display:block}
  .cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}
  .stat{flex:1;min-width:150px;background:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 1px 3px rgba(16,24,40,.06)}
  .stat .n{font-size:26px;font-weight:700} .stat .l{color:var(--faint);font-size:12px;margin-top:2px}
  .card{background:#fff;border-radius:16px;box-shadow:0 1px 3px rgba(16,24,40,.06);padding:20px;margin-bottom:18px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;color:var(--faint);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding:11px 12px;border-bottom:1px solid var(--bd);background:#fafafa;cursor:pointer}
  td{padding:11px 12px;border-bottom:1px solid #f4f5f7;vertical-align:middle}
  tr.lead{cursor:pointer} tr.lead:hover td{background:#f9fafb}
  .pill{display:inline-block;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:600}
  .fit{background:#dcfce7;color:#166534}.maybe{background:#fef9c3;color:#854d0e}.not_fit{background:#fee2e2;color:#991b1b}
  .pri-High{background:#e0e7ff;color:#3730a3}.pri-Medium{background:#f3f4f6;color:#4b5563}.pri-Low{background:#f9fafb;color:#9ca3af}
  .chip{display:inline-block;background:#eef2ff;color:#4338ca;border-radius:20px;padding:2px 9px;font-size:11px}
  .bar{background:#eef0f4;border-radius:8px;height:28px;position:relative;overflow:hidden;margin:6px 0}
  .bar .fill{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,#818cf8,#4f46e5);border-radius:8px}
  .bar .lbl{position:absolute;left:12px;top:0;line-height:28px;font-size:12px;color:#1f2937;font-weight:600;z-index:1}
  .bar .val{position:absolute;right:12px;top:0;line-height:28px;font-size:12px;color:#1f2937;font-weight:700;z-index:1}
  .msg{background:#f9fafb;border:1px solid var(--bd);border-radius:10px;padding:13px 15px;font-size:12.5px;line-height:1.7;white-space:pre-wrap;color:#374151;max-height:280px;overflow:auto}
  .empty{color:#c0c4cc}
  .row2{display:flex;gap:18px;flex-wrap:wrap}.row2>*{flex:1;min-width:280px}
  #detail{position:fixed;top:0;right:0;width:420px;max-width:92vw;height:100vh;background:#fff;box-shadow:-8px 0 30px rgba(0,0,0,.14);padding:24px;overflow:auto;transform:translateX(100%);transition:.18s}
  #detail.on{transform:translateX(0)}
  #detail .x{float:right;cursor:pointer;color:#9ca3af;font-size:22px;line-height:1}
  #detail h3{font-size:18px;margin-bottom:2px} .kv{font-size:12.5px;color:#374151;margin:8px 0}
  .kv b{color:#111} .sec-t{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#9ca3af;font-weight:700;margin:16px 0 6px}
  .aw{display:flex;gap:6px;align-items:center;font-size:12px}
  .step{padding:3px 9px;border-radius:20px;background:#f3f4f6;color:#9ca3af;font-weight:600}
  .step.done{background:#dcfce7;color:#166534}
  .rec{font-size:34px;font-weight:800;margin:6px 0}
  .go{color:#16a34a}.pilot{color:#d97706}.nogo{color:#dc2626}
  .note{background:#eef2ff;border:1px solid #dfe3ff;border-radius:10px;padding:11px 14px;font-size:12.5px;color:#3730a3;line-height:1.6}
  a.jl{color:var(--accent);font-weight:600;text-decoration:none}
</style></head><body>
<div class="side">
  <div class="brand">Korea Market Activation<small>Springboard × SyncTalents</small></div>
  <div class="nav">
    <a data-v="overview" class="on">📊 Overview</a>
    <a data-v="pipeline">🗂️ Pipeline</a>
    <a data-v="funnel">📉 KPI Funnel</a>
    <a data-v="outreach">✉️ Outreach Studio</a>
    <a data-v="reco">🎯 Recommendation</a>
  </div>
  <div class="foot">Team build — AI engine (Claude) · ICP scoring · pipeline · funnel · outreach · DSS. Data: demo (real listings); production switches to a licensed API.</div>
</div>
<div class="main">
  <section id="overview" class="on"></section>
  <section id="pipeline"></section>
  <section id="funnel"></section>
  <section id="outreach"></section>
  <section id="reco"></section>
</div>
<div id="detail"></div>
<script>
const DATA = __DATA__;
const AW = ["Jake","Mel","Rey"];       // approval chain
const state = {};                        // per-company approval step
DATA.forEach(d=> state[d.company]=0);

const pri = d => d.verdict==="fit"?"High":d.verdict==="maybe"?"Medium":"Low";
const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const pill = v => v?'<span class="pill '+v+'">'+v+'</span>':'<span class="empty">—</span>';

function counts(){
  const fit = DATA.filter(d=>d.verdict==="fit").length;
  const withC = DATA.filter(d=>d.email||d.contact_name).length;
  const withM = DATA.filter(d=>d.message).length;
  const avg = DATA.length? Math.round(DATA.reduce((a,b)=>a+b.fit,0)/DATA.length):0;
  return {n:DATA.length, fit, withC, withM, avg};
}
// funnel — HONEST: only stages backed by real events
function funnel(){
  const c=counts();
  return [
    ["1 · Target Identification", c.n],
    ["2 · Contact Identification", c.withC],
    ["3 · Outreach Drafted", c.withM],
    ["4 · Outreach Sent", 0],
    ["5 · Response", 0],
    ["6 · Verification Call", 0],
    ["7 · Meeting / Interest", 0],
    ["8 · Korea Visit", 0],
  ];
}

function renderOverview(){
  const c=counts();
  const svc={}; DATA.forEach(d=>{const k=d.service||"—";svc[k]=(svc[k]||0)+1;});
  const svcRows=Object.entries(svc).sort((a,b)=>b[1]-a[1]).map(e=>barRow(e[0],e[1],DATA.length)).join("");
  const prc={High:0,Medium:0,Low:0}; DATA.forEach(d=>prc[pri(d)]++);
  const prRows=["High","Medium","Low"].map(k=>barRow(k,prc[k],DATA.length)).join("");
  const top=[...DATA].sort((a,b)=>b.fit-a.fit).map(d=>
    '<tr class="lead" onclick=\\'openLead('+JSON.stringify(d.company)+')\\'><td><b>'+esc(d.company)+'</b></td><td>'+pill(d.verdict)+'</td><td><span class="pill pri-'+pri(d)+'">'+pri(d)+'</span></td><td style="text-align:right"><b>'+d.fit.toFixed(0)+'</b></td></tr>').join("");
  document.getElementById("overview").innerHTML =
    '<h1>Overview</h1><div class="sub">AI-powered Korean lead generation for Springboard\\'s 4 services — sourced, scored, qualified &amp; drafted automatically.</div>'
    +'<div class="cards">'
    +stat(c.n,"Leads")+stat(c.fit,"AI-qualified <b>fit</b>")+stat(c.avg,"Avg fit score")+stat(c.withM,"Outreach drafts")
    +'</div>'
    +'<div class="row2"><div class="card"><h2>🏆 Leads (ranked) <span class="empty" style="font-size:12px;font-weight:400">· scroll for all '+DATA.length+'</span></h2><div style="max-height:300px;overflow:auto">'
    +'<table><tbody>'+top+'</tbody></table></div></div>'
    +'<div class="card"><h2>Service mix</h2>'+svcRows
    +'<h2 style="margin-top:16px">Priority</h2>'+prRows+'</div></div>'
    +'<div class="card"><h2>📉 Pipeline funnel</h2>'+funnel().map(f=>barRow(f[0],f[1],c.n)).join("")
    +'<div class="note" style="margin-top:10px">Stages 4–8 stay at 0 until outreach is actually sent — <b>honesty principle</b>, no fake data.</div></div>';
}
const stat = (n,l)=>'<div class="stat"><div class="n">'+n+'</div><div class="l">'+l+'</div></div>';
function barRow(label,val,max){const p=(max&&val>0)?Math.max(7,Math.round(val/max*100)):0;
  return '<div class="bar"><i class="fill" style="width:'+p+'%"></i><span class="lbl">'+label+'</span><span class="val">'+val+'</span></div>';}

let sortK="fit", sortD=-1;
const ALIAS={"데이터":"data","백엔드":"backend","프론트":"frontend","핀테크":"fintech","게임":"game gaming","보안":"security","의료":"health medical","헬스":"health","클라우드":"cloud","인공지능":"ai","엔지니어":"engineer","개발자":"developer","이커머스":"ecommerce"};
function hay(d){let h=[d.company,d.industry,d.service,d.tech,d.region,d.roles,d.verdict,pri(d)].join(" ").toLowerCase();for(const k in ALIAS){if(h.indexOf(k.toLowerCase())>=0)h+=" "+ALIAS[k];}return h;}
function matchLead(d,t){return !t || hay(d).indexOf(t)>=0;}
function renderPipeline(){
  document.getElementById("pipeline").innerHTML =
    '<h1>Pipeline (CRM)</h1><div class="sub">'+DATA.length+' companies · search, sort, click a row for detail.</div>'
    +'<div class="card"><input id="q" placeholder="🔍 Search company, industry, role, tech… (KR/EN, typo-tolerant fields)" oninput="renderRows()" '
    +'style="width:100%;padding:10px 12px;border:1px solid var(--bd);border-radius:10px;font-size:13px;margin-bottom:12px;outline:none">'
    +'<table><thead><tr><th onclick="sortP(\\'company\\')">Company</th><th>Service</th><th onclick="sortP(\\'fit\\')">Fit ▾</th><th>Priority</th><th>AI verdict</th><th>Hiring</th><th>Evidence</th></tr></thead><tbody id="pbody"></tbody></table>'
    +'<div id="pcount" class="sub" style="margin:10px 0 0"></div></div>';
  renderRows();
}
function renderRows(){
  const el=document.getElementById("q"); const t=el?el.value.toLowerCase().trim():"";
  const rows=[...DATA].filter(d=>matchLead(d,t)).sort((a,b)=>{let x=a[sortK],y=b[sortK];if(sortK==="fit")return (y-x)*sortD;if(x<y)return -1*sortD;if(x>y)return 1*sortD;return 0;});
  document.getElementById("pbody").innerHTML = rows.map(d=>{const p=pri(d);
      return '<tr class="lead" onclick=\\'openLead('+JSON.stringify(d.company)+')\\'>'
      +'<td><b>'+esc(d.company)+'</b><br><span class="empty" style="font-size:11px">'+esc(d.industry)+'</span></td>'
      +'<td><span class="chip">'+esc(d.service||"—")+'</span></td>'
      +'<td><b>'+d.fit.toFixed(0)+'</b></td>'
      +'<td><span class="pill pri-'+p+'">'+p+'</span></td>'
      +'<td>'+pill(d.verdict)+'</td>'
      +'<td>'+(d.hiring||"—")+'</td>'
      +'<td>'+(d.email||d.contact_name?'✅':'<span class="empty">—</span>')+'</td></tr>';}).join("");
  document.getElementById("pcount").textContent = rows.length+" of "+DATA.length+" shown";
}
function sortP(k){sortD=(sortK===k)?-sortD:(k==="fit"?-1:1);sortK=k;renderRows();}

function renderFunnel(){
  const c=counts();
  document.getElementById("funnel").innerHTML =
    '<h1>KPI Funnel</h1><div class="sub">The playbook\\'s 8-stage funnel. Real events only (honesty principle).</div>'
    +'<div class="card">'+funnel().map(f=>barRow(f[0],f[1],c.n)).join("")+'</div>'
    +'<div class="note">Stages 4–8 are 0 because no outreach has actually been sent yet — drafts are ready and awaiting approval. They fill in as real responses/meetings happen.</div>';
}

function renderOutreach(){
  document.getElementById("outreach").innerHTML =
    '<h1>Outreach Studio</h1><div class="sub">Claude-written EN + KR drafts. Approval: Jake → Mel → Rey before any send.</div>'
    +'<input id="qo" placeholder="🔍 Search drafts by company, industry, service… (KR/EN)" oninput="renderOutreachRows()" '
    +'style="width:100%;padding:10px 12px;border:1px solid var(--bd);border-radius:10px;font-size:13px;margin-bottom:14px;outline:none">'
    +'<div id="obody"></div>';
  renderOutreachRows();
}
function renderOutreachRows(){
  const el=document.getElementById("qo"); const t=el?el.value.toLowerCase().trim():"";
  const withM=DATA.filter(d=>d.message && matchLead(d,t));
  document.getElementById("obody").innerHTML = withM.length
    ? withM.map(d=>outreachCard(d)).join("")
    : '<div class="card empty">No matching drafts.</div>';
}
function outreachCard(d){
  return '<div class="card"><h2 style="margin:0 0 8px">'+esc(d.company)
    +' <span class="pill '+(d.verdict||"")+'" style="margin-left:6px">'+(d.verdict||"")+'</span></h2>'
    +'<div class="msg">'+esc(d.message)+'</div></div>';
}
function approvalUI(co){const s=state[co];
  return '<div class="aw">'+AW.map((n,i)=>'<span class="step '+(i<s?"done":"")+'">'+(i<s?"✓ ":"")+n+'</span>').join('<span style="color:#cbd5e1">→</span>')
    +' <button onclick=\\'appr('+JSON.stringify(co)+')\\' style="margin-left:6px;padding:4px 10px;border:1px solid var(--bd);border-radius:8px;background:#fff;cursor:pointer;font-size:11px;font-weight:600">'
    +(s>=3?"Approved":"Approve ("+AW[s]+")")+'</button></div>';
}
function appr(co){if(state[co]<3)state[co]++;renderOutreachRows();}

function renderReco(){
  const c=counts();
  // data-driven provisional recommendation
  let v,cls,why;
  if(c.fit>=3){v="PILOT";cls="pilot";why="There are "+c.fit+" AI-qualified 'fit' leads — enough to run a focused outreach pilot and measure real response before a full Korea visit.";}
  else if(c.fit>=1){v="PILOT";cls="pilot";why="A small number of qualified leads exist; validate with a limited outreach test first.";}
  else {v="NO-GO (yet)";cls="nogo";why="No qualified 'fit' leads yet — keep sourcing before committing.";}
  document.getElementById("reco").innerHTML =
    '<h1>Recommendation (DSS)</h1><div class="sub">Go / Pilot / No-Go — provisional, from current data. Finalizes at project end with real response data.</div>'
    +'<div class="card"><div class="sec-t">Provisional decision</div><div class="rec '+cls+'">'+v+'</div><div class="kv">'+why+'</div></div>'
    +'<div class="row2"><div class="card"><h2>Signals we have</h2>'
    +'<div class="kv">✅ '+c.fit+' qualified fit leads</div><div class="kv">📊 '+c.n+' companies sourced, avg fit '+c.avg+'</div><div class="kv">✉️ '+c.withM+' outreach drafts ready</div></div>'
    +'<div class="card"><h2>Signals we still need (honesty)</h2><div class="kv">⏳ Actual outreach responses</div><div class="kv">⏳ Verification calls / meetings</div><div class="kv">⏳ Confirmed business interest</div>'
    +'<div class="note" style="margin-top:8px">Go requires real response + meeting data — not yet available, so we don\\'t claim it.</div></div></div>';
}

// detail panel
function openLead(co){const d=DATA.find(x=>x.company===co);if(!d)return;
  document.getElementById("detail").innerHTML =
    '<span class="x" onclick="closeD()">×</span><h3>'+esc(d.company)+'</h3>'
    +'<div class="empty" style="font-size:12px">'+esc(d.industry)+' · '+esc(d.region)+'</div>'
    +'<div class="kv"><b>Fit '+d.fit.toFixed(0)+'</b> · '+pill(d.verdict)+' <span class="empty">('+(d.confidence||"-")+')</span> · Priority <span class="pill pri-'+pri(d)+'">'+pri(d)+'</span></div>'
    +'<div class="kv">Service: <span class="chip">'+esc(d.service||"—")+'</span> · Size: '+(d.employees?esc(d.employees):"—")+' · Hiring: '+(d.hiring||"—")+'</div>'
    +'<div class="sec-t">🤖 AI qualification</div><div class="kv">'+(d.reason?esc(d.reason):'<span class="empty">not run</span>')+'</div>'
    +'<div class="sec-t">Open roles</div><div class="kv">'+(esc(d.roles)||'—')+'</div>'
    +'<div class="sec-t">Tech stack</div><div class="kv">'+(esc(d.tech)||'—')+'</div>'
    +'<div class="sec-t">Contact (for crawled data)</div><div class="kv">'+(d.contact_name?esc(d.contact_name):"—")+(d.email?' · '+esc(d.email):"")+'</div>'
    +(d.url?'<div class="kv"><a class="jl" href="'+d.url+'" target="_blank">View job posting →</a></div>':"")
    +'<div class="sec-t">✉️ Outreach draft</div>'+(d.message?'<div class="msg">'+esc(d.message)+'</div>':'<span class="empty">no draft</span>');
  document.getElementById("detail").classList.add("on");
}
function closeD(){document.getElementById("detail").classList.remove("on");}

// nav
document.querySelectorAll(".nav a").forEach(a=>a.onclick=()=>{
  document.querySelectorAll(".nav a").forEach(x=>x.classList.remove("on"));a.classList.add("on");
  const v=a.dataset.v;document.querySelectorAll("section").forEach(s=>s.classList.remove("on"));
  document.getElementById(v).classList.add("on");closeD();
});
renderOverview();renderPipeline();renderFunnel();renderOutreach();renderReco();
</script></body></html>"""


def main() -> None:
    rows = build_dataset()
    emp = _employees()
    for r in rows:
        r["employees"] = emp.get(r["company"], "")
    payload = json.dumps(rows, ensure_ascii=False)
    out = DATA_DIR / "platform.html"
    out.write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
    print(f"Wrote {out} — {len(rows)} leads, 5-view consolidated platform.")


if __name__ == "__main__":
    main()
