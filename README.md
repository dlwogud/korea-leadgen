# Korea Lead-Gen — Data Backbone 

Data foundation for the Springboard × SyncTalents Korea market-entry internship
(2026-06-29 → 2026-07-17). Owns the **prospect database, lead scoring, and
pipeline/funnel dashboard** that the Business and AI tracks build on top of.

## Why this exists

Every outreach decision in the program should be data-driven:
- **Business track** works the highest-scored leads first.
- **AI track** writes sourced prospects into this schema.
- **Capstone** is judged partly on cross-track synergy — a shared data backbone
  is the cleanest way to make that synergy real instead of three silos.

## Target service areas (priority for this cohort)

1. **IT Tech Servicing** (staff augmentation / outsourced dev, QA, sysadmin) — primary.
   Springboard's core strength; clearest cold-outreach value prop for Korea
   (high local dev cost + talent shortage).
2. **AI Implementation** — secondary, high-interest door-opener. The team's own
   AI tooling doubles as proof-of-concept.
3. Systems Integration / Skilled Manpower Placement — longer cycle, kept in schema
   but not the initial outreach focus.

The schema supports all four; the *focus* is a strategy choice we can re-tune.

## The 8-stage funnel (program-wide shared language, playbook §6.1)

1. Target identified → 2. Contact identified → 3. Outreach sent → 4. Reply received
→ 5. Validation call booked → 6. Validation call held → 7. Concrete interest
(proposal/demo/pricing requested) → 8. Korea-visit ready.

`pipeline_events` tracks every lead's movement through these stages so the
dashboard can show stage-by-stage conversion (the Week-4 deliverable).

## Layout

```
korea-leadgen/
├── db/
│   └── schema.sql        # prospect DB: companies, signals, contacts, scores, funnel
├── docs/
│   ├── ICP.md            # ideal-customer-profile hypotheses per service area
│   └── lead-scoring.md   # how a company gets its 0–100 lead score
└── scripts/              # (later) ingestion + scoring + dashboard refresh
```

## Quickstart

```bash
cd korea-leadgen
pip install -r requirements.txt
cp .env.example .env          # then paste your free Saramin key into .env

python scripts/run.py         # source from Saramin → score → ranked CSV
# or step by step:
python scripts/source_saramin.py --keywords "백엔드,데이터 엔지니어" --pages 2
python scripts/score_leads.py
```

Outputs (gitignored, under `data/`):
- `companies_raw.csv` — companies + hiring signals from Saramin
- `scored_leads.csv` — same, ranked by IT-Servicing fit score

> The scoring step runs on its own against any `companies_raw.csv`, so the
> pipeline is demoable without a key (seed a sample CSV).

## Two data sources (swappable)

Both emit the same company schema (`_common.COMPANY_FIELDS`), so scoring /
contacts / dashboard are identical regardless of source:

| Source | Script | Commercial use | When |
|--------|--------|----------------|------|
| **Saramin** (free API) | `source_saramin.py` | ❌ prototype only (≤500 calls/day, no resale) | now — best tech-company coverage for the POC |
| **WorkNet** (public data) | `source_worknet.py` | ✅ public data permits commercial use | if/when this goes commercial |

**Plan:** validate with Saramin (prototype), swap to WorkNet if the program
decides on commercial deployment. The WorkNet client is written but its API
field mappings are marked `# VERIFY` until run against a live key.

> Commercial deployment is a **company decision** (licensing + outreach
> compliance), not something to run on a personal free key. See `docs/GAPS.md`.

## Status

- [x] DB schema v1
- [x] ICP hypotheses v1 (to validate against Week-2 real responses)
- [x] Lead-scoring design v1
- [x] Saramin sourcing script (`source_saramin.py`)
- [x] Scoring script (`score_leads.py`) — verified on sample data
- [x] Contact enrichment workflow (`make_contact_worksheet.py` → fill → `rescore_with_contacts.py`)
- [x] Funnel logging + dashboard (`log_event.py`, `dashboard.py` → terminal + HTML)
- [x] Living DB: tech-stack signal + per-service fit (all 4) + first/last_seen (`enrich.py`)
- [x] One-command demo on sample data (`demo.py`)
- [ ] Add free Saramin key and run on real postings
- [ ] Firmographic enrichment via DART (company size — still a placeholder)
- [ ] Weekly response/conversion analysis (DS §5.2 #4 — needs Week-2 reply data)
- [ ] Optional: auto reply-tracking if outreach goes via email (Gmail API)

> Draft v1 — built day 1 to bring to the mentor / Friday sync as a concrete
> proposal, not a finished system. Everything here is meant to be tuned with
> real outreach data from Week 2 onward.
