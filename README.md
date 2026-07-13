# Korea Market Activation Platform

AI-powered lead generation for the **Springboard × SyncTalents** Korea
market-entry internship. It sources Korean companies that are actively hiring
developers, scores them against an Ideal Customer Profile (ICP), uses Claude to
qualify and draft outreach, and presents everything in one shareable app.

```
Wanted postings → enrich → ICP score → Claude qualify (fit/maybe/no) → EN/KR outreach → platform + delivery sheet
```

**Live demo:** https://dlwogud.github.io/km-platform-demo/

## The platform (5 views)

`scripts/platform.py` builds a single self-contained app (`data/platform.html`):

- **Overview** — KPIs, top leads, service/priority mix, funnel
- **Pipeline (CRM)** — searchable leads: priority, AI verdict, evidence, detail
- **KPI Funnel** — the playbook's 8-stage funnel (real events only)
- **Outreach Studio** — Claude EN/KR drafts, searchable
- **Recommendation (DSS)** — data-driven Go / Pilot / No-Go

## Quick start

```bash
pip3 install -r requirements.txt
cp .env.example .env          # add ANTHROPIC_API_KEY (for the AI steps)

# run the whole pipeline on fresh Wanted data:
bash scripts/daily_wanted.sh
# then open data/platform.html
```

## Data source

- **Primary: Wanted** (`source_wanted.py`) — where Korean tech SMEs hiring
  developers post. No API key needed. Best fit for the ICP. *Whether to run
  automated collection is a company decision — see the script header.*
- **Optional: Saramin** (`source_saramin.py` + `run_live.py`) — for teams that
  license the Saramin API. Same pipeline, different source.
- **Manual** (`import_list.py`) — import any company CSV. Fully legal fallback.

The source layer is swappable — every source writes the same schema
(`scripts/_common.py`), so scoring + AI are identical whichever feed is used.

## Automation

`scripts/daily_wanted.sh` runs the full pipeline; schedule it with cron
(12:00 daily). See `docs/AUTOMATION.md`.

## Repository layout

```
config/icp.json   The ICP (size, industries, roles, weights) — edit to retarget
scripts/          Pipeline: source_* / enrich / score / qualify / generate / platform / ...
data/             Generated outputs (gitignored)
docs/             Handover, reports, automation, ICP notes
```

## Key docs

- **`docs/HANDOVER.md`** — how the company takes this over (repo, keys, run, schedule)
- **`docs/jake-update.md`** — progress report + open decisions
- **`docs/AUTOMATION.md`** — scheduling
- **`docs/ICP.md`** — the target profile

## Status

Consolidated platform running on real Wanted data (prototype-grade). API-ready;
productionizing needs a licensed data path + company Anthropic key. Honest
limitations and open decisions are in `docs/jake-update.md`.
