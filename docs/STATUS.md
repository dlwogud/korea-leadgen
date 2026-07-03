# Lead-Gen Pipeline — Status Summary

**Status:** Prototype — built and running end-to-end on sample data, not yet
validated on real leads.

## 1. Sourcing
- **Primary: Saramin API** (free tier, applied for — a few days out). ICP-driven
  search covers role/title variants, not just exact keywords, filtered by
  Saramin's IT job category.
- **Fallback if Saramin API is unavailable:** the **public-data portal
  (data.go.kr)** — e.g. WorkNet job postings — as a Plan B source.
- **Manual import:** any company list from the business team (Korean/English
  columns auto-detected) runs through the same pipeline.
- **Dedup:** by company and by posting, to avoid double-counting across searches.

## 2. ICP Config (single source of truth)
`config/icp.json` defines, per service area (IT servicing / manpower / AI / SI):
search keywords, target industries, buying-signal terms, regions, and scoring
weights. Drives both search and scoring — updating the target profile requires
only editing this file, no code changes.

## 3. Enrichment
- Extracts tech stack per company from postings (Java, AWS, React, PyTorch, etc.)
- Scores fit across all four services, selects best-fit one.
- Living database: reruns merge new data with first-seen/last-seen timestamps
  rather than overwriting.

## 4. Lead Scoring
0–100 = 40% firmographic fit + 40% hiring-signal strength + 20% reachability
(decision-maker contact on file). Fully explainable — every score traces to
evidence.

## 5. Contact Enrichment
Manual step — a research worksheet lists top leads; once a decision-maker
(name/email/LinkedIn) is added by hand, that lead's reachability score rises,
surfacing reachable leads first.

## 6. AI Outreach Draft
Personalized Korean first-touch message per lead, tailored to hiring signal +
best-fit service. Template-based by default; uses Claude if an API key is set.
All drafts require Jake/Mel/Rey approval before sending.

## 7. KPI Funnel Dashboard
8-stage funnel (per playbook §6.1) with stage-to-stage conversion, auto-generated
as an HTML dashboard.

## 8. Database
SQLite backend, queryable via SQL (top leads, service breakdown, funnel), retains
history.

## 9. Demo
`python3 scripts/demo.py` runs the full pipeline on sample data. `overview.html`
shows top leads, service mix, a sample outreach draft, and the funnel on one
screenshot-ready page. Private GitHub repo; live demo available anytime.

## Open Questions for the Team
- Which service area to prioritize?
- Who owns the ICP definition? (config-driven — can plug in immediately)
- Delivery target for results — shared sheet or CRM?
- **Confirmed:** prototype-only for now — not commercial. Data source stays
  Saramin (with the **public-data portal** as backup) rather than a licensed source.

## Next Steps
- Run against real Saramin postings once the key lands.
- Company-size enrichment (**public-data portal** or DART) + manual contact enrichment.
- Week 2+: weekly response/conversion analysis, feeding real replies back into the
  scoring model.

## Honest Notes
- Currently sample data + v1 heuristic scoring — proven end-to-end, not yet
  validated against real outreach results.
- Contact enrichment remains a manual step by design at this stage.
- Data-source layer is swappable; Saramin free API (or the public-data portal as
  backup) is a prototype choice, not a commercial-grade source.
