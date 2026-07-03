# Data-Side Progress Report — Korea Lead-Gen Prototype

A data pipeline that finds Korean companies, ranks them as leads for our four
services, and drafts outreach — end to end. Running on sample data now; built so
the same code runs on live data the moment the Saramin API key arrives.

---

## Pipeline — how it works, stage by stage

**1. Sourcing — where the companies come from**
- Primary: **Saramin** (one of Korea's two largest job boards) via its free API.
  Driven by the ICP config — searches the right roles and can filter by Saramin's
  IT job *category*, so it catches title variants (백엔드 / Java 개발자 / API
  Engineer …), not just exact keywords.
- **Manual import**: takes any company list the business track hands over (a
  spreadsheet; Korean or English column names auto-detected) and runs it through
  the exact same pipeline — so we're not locked to one source.
- **Commercial-safe alternative**: a WorkNet (Korean public-data) source is
  scaffolded for if/when this goes commercial.
- **Dedup**: by company and by posting, so a company found under several searches
  isn't double-counted.

**2. ICP config — the single source of truth**
- One file (`config/icp.json`) defines, per service area (IT servicing / manpower
  / AI / systems integration): search keywords, target industries, buying-signal
  terms, target regions, and scoring weights.
- It drives BOTH what we search AND how we score. When the team confirms the real
  target profile, we edit this one file — no code changes.

**3. Enrichment — raw postings → a usable record**
- Extracts each company's **tech stack** from its postings (Java, AWS, React,
  PyTorch …).
- Scores **fit for all four services** and picks the best-fit one.
- Maintains a **living database**: re-running merges new data and stamps
  first-seen / last-seen, so it stays current instead of overwriting.

**4. Lead scoring — who to contact first**
- Score **0–100** = 40% firmographic fit + 40% hiring-signal strength + 20%
  reachability (do we have a decision-maker contact).
- Fully **explainable** — every score traces back to its evidence.

**5. Contact enrichment**
- Produces a research worksheet of the top leads; once a decision-maker
  (name / email / LinkedIn) is added, that lead's score rises, so **reachable
  leads surface first**.

**6. AI outreach draft**
- A **personalized Korean first-touch message per lead**, tailored to its hiring
  signal and best-fit service. Template-based now; uses Claude to write them when
  an API key is set. Every message is a **draft** requiring Jake / Mel / Rey
  approval before sending.

**7. KPI funnel dashboard**
- The 8-stage funnel from the playbook (§6.1), with stage-to-stage conversion,
  auto-generated as an HTML dashboard.

**8. Database + history**
- Everything loads into a **SQLite** database — queryable with SQL (top leads,
  service breakdown, funnel) and keeps history.

**9. Demo + overview page**
- `python3 scripts/demo.py` runs the whole pipeline on sample data.
- `overview.html` shows top leads + service mix + a sample outreach draft + the
  funnel **on one page** (screenshot-ready). All in a private GitHub repo; live
  demo anytime.

---

## Current status

- Everything above is **built and runs end to end on sample data**.
- Waiting on the free **Saramin API key** (applied — a few days out). The same
  code runs on real Korean companies the moment it lands.
- Scoring is a **v1 heuristic**; it'll be re-weighted with real response data once
  outreach starts (Week 2+).

## Would help to confirm (from the team)

- Which **service area** should we target?
- Who sets the **ICP** (the target profile)? — it's config-driven, so I can plug
  it in immediately.
- Where should results be **delivered** — a shared sheet / CRM?
- **Prototype-only or heading to commercial use?** (changes the data source.)

## Next steps

- Run on real Saramin postings once the key arrives.
- Company-size enrichment (DART) + contact enrichment.
- Week 2+: weekly response / conversion analysis, and feed real replies back into
  the scoring model.

## Honest notes

- Sample data + a v1 heuristic — proven end to end, not yet validated against
  reality.
- Saramin's free API is for the prototype; commercial deployment would use a
  licensed / public-data source (the source layer is swappable).
