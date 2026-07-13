# Korea Market Activation Platform — Status Summary

**Status:** Consolidated platform running end-to-end on **real Wanted data**
(27 companies, 3 AI-qualified Fit). Prototype-grade data; not yet validated on
real outreach outcomes.

## 1. Sourcing
- **Primary: Wanted** (`source_wanted.py`) — collects developer postings, filters
  to the ICP via Wanted's dev category, captures company, industry, location,
  posting count, and the real job URL. No API key required.
- **Optional: Saramin** (`source_saramin.py` + `run_live.py`) — cleaner for
  commercial scale but needs a licensed API (free tier was unresponsive; Korean
  APIs may need a Korean business entity). Drop-in alternative.
- **Manual import** (`import_list.py`): any company CSV (KR/EN columns
  auto-detected) runs through the same pipeline.
- **Dedup** by company and posting.

## 2. ICP Config (single source of truth)
`config/icp.json` defines size band (20–300), target industries, roles,
buying-signal terms, regions, and scoring weights — for all four services.
Drives search + scoring; retargeting = edit this file, no code changes.

## 3. Enrichment
- Tech-stack extraction per company from posting text.
- Per-service fit; selects best-fit service.
- **Firmographic size** (`employees`) carried through for the 20–300 ICP check.
- Living database: reruns merge with first-seen/last-seen (no overwrite).

## 4. Lead Scoring
0–100 = firmographic fit + hiring-signal strength + reachability. Fully
explainable — every score traces to evidence.

## 5. AI Qualification + Outreach (real Claude)
- **Qualify** (`qualify_leads.py`): Claude returns Fit / Maybe / Not-Fit **with
  reasoning**, under a strict rubric (tech industry + confirmed 20–300 size +
  2+ mid-level dev roles). Discriminates — doesn't rubber-stamp.
- **Outreach** (`generate_messages.py`): Claude drafts an **English + Korean**
  first-touch message per lead. All drafts require human approval before sending.

## 6. Consolidated Platform (`platform.py`)
One self-contained app, five views: Overview · Pipeline (CRM) · KPI Funnel ·
Outreach Studio · Recommendation (DSS). Searchable (KR/EN), fit-first ranking,
shareable by link.

## 7. KPI Funnel
8-stage funnel. Stages 1–3 auto-computed; stages 4–8 reflect **real events only**,
logged via `log_event.py` (honesty principle — no fake data).

## 8. Automation
`daily_wanted.sh` runs the full pipeline; scheduled via cron (12:00 daily).
Logs to `data/daily.log`. See `docs/AUTOMATION.md`.

## Open questions for the team (see `docs/jake-update.md`)
- **Commercial data path** — pay for a licensed API as a foreign company, or
  contract through a Korean partner?
- **Company Anthropic key** — for production AI (currently a personal key).
- **Repo transfer** to Springboard + confirm this platform as the deliverable.

## Honest limitations
- Prototype-grade data: 27 companies, sizes partly estimated, contacts pending.
- API-ready but sourcing is currently on-demand, not yet a licensed live feed.
- No real outreach outcomes yet (funnel honestly empty past "drafted").
- Consolidation is at the feature/UI level; deeper data integration plugs in next.
