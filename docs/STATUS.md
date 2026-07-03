# Status — Data Side (Korea Lead-Gen)

_Prototype on sample data. Saramin API key applied for; same code runs on real
data once it arrives._

## Done ✅

- **Sourcing** — pulls Korean companies from Saramin job postings (ICP-driven,
  keyword + category modes). Also imports a manual/business-provided company list
  (KR/EN columns auto-detected), so it's not tied to one source. A commercial-safe
  WorkNet (public-data) source is scaffolded for later.
- **ICP config** — one file (`config/icp.json`) drives both sourcing and scoring;
  update it when the target profile is confirmed, no code changes.
- **Enrichment** — detects each company's tech stack and scores fit for all four
  services (IT servicing / manpower / AI / systems integration); keeps a living DB
  with first/last-seen timestamps.
- **Lead scoring** — 0–100 per company (firmographic fit + hiring signal +
  reachability); ranked list of who to contact first.
- **Contact workflow** — turns top leads into a research worksheet; reachable
  leads score higher once a decision-maker is added.
- **AI outreach draft** — a personalized Korean first-touch message per lead
  (template now; uses Claude when an API key is set). Every message is a draft
  requiring approval before sending.
- **KPI funnel dashboard** — leads by stage with stage-to-stage conversion (HTML).
- **Real database + SQL** — loads everything into SQLite for querying.
- **One-command demo + overview page** — `python3 scripts/demo.py` runs it all on
  sample data; `overview.html` shows top leads + service mix + a sample outreach
  draft + the funnel on one page. Private GitHub repo; live demo anytime.

## In progress / waiting ⏳

- Saramin API key (applied — a few days) → then real Korean company data.
- Direction to confirm: which service area to target, and who sets the ICP
  (built config-driven so it plugs straight in).

## Next ⏭

- Run on real postings once the key lands.
- Contact + company-size enrichment (DART).
- Week-2 onward: weekly response/conversion analysis + re-weight the scoring with
  real reply data.

## Honest notes

- Everything is on **sample data** for now; scoring is a **v1 heuristic** to be
  validated with real responses.
- Saramin free API = prototype use; commercial deployment would use a licensed /
  public-data source (the source layer is swappable).
