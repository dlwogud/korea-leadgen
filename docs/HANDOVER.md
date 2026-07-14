# Handover Guide — Korea Market Activation Platform

For the Springboard / SyncTalents team taking over after the internship. Follow
the steps in order and the platform runs on your own accounts and machines.

---

## TL;DR (what you must do)

1. **Receive the repo** (transfer to a Springboard GitHub org).
2. **Install** Python deps.
3. **Add your own keys** to `.env` (Anthropic; optionally a licensed data key).
4. **Run it once** to verify.
5. **Schedule** the daily job on a company machine/server.
6. **Redeploy** the demo link under a company account.

Everything is source-agnostic and config-driven — you only swap *keys, repo,
and where it runs* from the intern's personal setup to the company's.

---

## What is this

An AI-powered lead-generation platform: it collects Korean job postings, scores
each company against the ICP, uses Claude to qualify Fit/Maybe/Not-Fit and draft
EN/KR outreach, and presents everything in one shareable app + a delivery sheet.

**Pipeline:** `source → enrich → score → AI qualify → AI outreach → platform + delivery`

**Important:** the AI (Claude) is used only for *qualification and outreach
writing*. Data collection is plain HTTP + JSON parsing (no AI, no browser).

---

## Easiest start — the admin panel (no command line)

After you've cloned the repo and installed deps (Steps 1–2 below), you can run
**everything from a browser** — no terminal commands needed:

```bash
python3 scripts/admin_server.py      # starts a localhost-only admin page
# then open http://localhost:8765
```

On that page you can:
- **Enter your API keys** (Anthropic for AI; optionally Saramin, DART) → saved to `.env`
- **Click "Collect from Wanted"** → runs the whole pipeline and rebuilds the platform
- Open the result at **/platform**

It binds to `127.0.0.1` (localhost) only — internal to that machine, not exposed
to the network or the public. This is the simplest way to hand it off: keys in,
click run, done. (The manual CLI steps below do the exact same thing.)

> Notes: **Wanted needs no key** (works out of the box). **JobKorea has no public
> API** (not supported). **DART (금융감독원)** is not a job source — its key adds
> real company-size data for better scoring.

---

## Step 1 — Repository

The code currently lives at a personal GitHub account. Transfer it to a
Springboard-owned org so the company controls it:

- GitHub → repo **Settings → Transfer ownership** → enter the Springboard org.
- After transfer, clone it:
  ```bash
  git clone https://github.com/<springboard-org>/korea-leadgen.git
  cd korea-leadgen
  ```

## Step 2 — Install

Requires Python 3.9+.
```bash
pip3 install -r requirements.txt
```

## Step 3 — Configure keys (`.env`)

```bash
cp .env.example .env
```
Edit `.env` and set **the company's own** values:
```
ANTHROPIC_API_KEY=sk-ant-...      # REQUIRED for AI qualify + outreach
SARAMIN_API_KEY=                  # optional — only if you license Saramin's API
WORKNET_API_KEY=                  # optional
```
- `.env` is gitignored — never commit real keys.
- Get an Anthropic key at console.anthropic.com (company account + billing).
  Cost is ~a few cents per lead; control it with the `--top` flags below.

## Step 4 — Choose a data source & run once

Pick how leads are sourced (see "Data source options" below), then run the
whole pipeline. Easiest — run the daily script directly once:
```bash
bash scripts/daily_wanted.sh
```
Or step by step:
```bash
python3 scripts/source_wanted.py --pages 5     # collect fresh postings
python3 scripts/enrich.py                       # tech stack + living DB
python3 scripts/score_leads.py                  # ICP score
python3 scripts/qualify_leads.py --top 10       # Claude Fit/Maybe/Not-Fit
python3 scripts/generate_messages.py --top 10   # Claude EN/KR outreach
python3 scripts/build_platform.py                     # build data/platform.html
python3 scripts/export_delivery.py              # data/delivery.csv
python3 scripts/view_delivery.py                # data/delivery.html
```
Outputs land in `data/` — open `data/platform.html` in a browser.

## Step 5 — Automate (daily schedule)

Run it on an **always-on company machine or server** (an intern's laptop will
not be available):
```bash
chmod +x scripts/daily_wanted.sh
crontab -e
# add this line for 12:00 daily:
0 12 * * * /absolute/path/to/korea-leadgen/scripts/daily_wanted.sh
```
- Logs to `data/daily.log`.
- The machine must be awake at the scheduled time.
- On macOS, if it silently doesn't run, grant Full Disk Access to `cron` in
  System Settings → Privacy & Security.

## Step 6 — Redeploy the demo link (optional)

The shareable link should live under a company account:
- **GitHub Pages:** put `data/platform.html` as `index.html` in a repo →
  Settings → Pages → deploy from `main` / root.
- **Netlify Drop:** drag `data/platform.html` onto app.netlify.com/drop.
Both give a permanent URL. `platform.html` is self-contained (no server needed).

---

## Data source options

| Source | How | Notes |
|--------|-----|-------|
| **Wanted (scraping)** | `source_wanted.py` | No key needed. **Whether to run this is a company/legal decision** — automated collection can conflict with ToS (see the script header). Best fit for tech-SME/developer ICP. |
| **Saramin (official API)** | `source_saramin.py` | Cleanest for commercial use, but needs an API key/license. Free tier is non-commercial and was unresponsive to intern-level requests — pursue a **paid/partnership license** as the company. Note: Korean APIs may require a Korean business number / entity. |
| **Manual / business list** | `import_list.py` | Import any CSV of companies (fully legal, no scraping). Good fallback. |

The pipeline is identical regardless of source — each writes
`data/companies_raw.csv` in the shared schema (`scripts/_common.py`).

---

## Updating the KPI funnel (real events)

Funnel stages 1–3 are computed automatically (leads / contacts / drafts).
Stages 4–8 reflect **real events only** — log each one as it actually happens:

```bash
python3 scripts/log_event.py --company "앤서스랩코리아" --service it_servicing --stage outreach_sent
```

`--stage` values and where they land in the funnel:

| `--stage` | Funnel stage |
|-----------|--------------|
| `outreach_sent` | 4 · Outreach Sent |
| `reply_received` | 5 · Response |
| `call_booked` | 6 · Verification Call |
| `concrete_interest` | 7 · Meeting / Interest |
| `korea_visit_ready` | 8 · Korea Visit |

Events accumulate in `data/pipeline_events.csv`. Rerun `scripts/build_platform.py`
(or wait for the daily cron) and the funnel updates. **Honesty principle: only
log events that actually happened** — never pre-fill the funnel. (The file
starts empty; do not seed it with fake data.)

---

## Personal → company swap checklist

| Item | Intern setup (now) | Company setup (target) |
|------|--------------------|------------------------|
| GitHub repo | personal account | Springboard org |
| Anthropic API key | personal key in `.env` | company key + billing |
| Data source key | none / personal | company-licensed (if using an API) |
| Cron schedule | intern's Mac | always-on company machine/server |
| Demo link | intern's GitHub Pages / tunnel | company account redeploy |

---

## File map

```
config/icp.json         The ICP (size, industries, roles, weights). Edit to tune targeting.
scripts/
  source_wanted.py      Wanted scraper (data collection)
  source_saramin.py     Saramin API client (if licensed)
  import_list.py        Import a manual CSV of companies
  enrich.py             Tech-stack extraction + living DB (first/last seen)
  score_leads.py        ICP scoring
  qualify_leads.py      Claude Fit/Maybe/Not-Fit
  generate_messages.py  Claude EN/KR outreach drafts
  build_platform.py           Builds the consolidated 5-view app (data/platform.html)
  export_delivery.py    Team delivery CSV
  view_delivery.py      Delivery sheet (HTML)
  daily_wanted.sh       Runs the whole pipeline (for cron)
  _common.py            Shared schema + helpers
data/                   All generated outputs (gitignored)
docs/                   This guide, ICP notes, automation, reports
.env                    Keys (gitignored — create from .env.example)
```

---

## Tuning

- **Targeting:** edit `config/icp.json` (firm size, industries, roles, weights).
- **AI cost/volume:** the `--top N` flags cap how many leads get Claude calls.
  Set `--top 0` to skip AI entirely and run scoring only.
- **Scrape volume:** `source_wanted.py --pages N` controls how much is collected.

## Support

Built during the Springboard × SyncTalents Korea Market Activation internship.
The code is documented and self-contained; `docs/AUTOMATION.md` has more on
scheduling. For questions, contact the internship team.
