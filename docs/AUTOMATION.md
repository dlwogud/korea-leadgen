# Automation — daily, hands-off lead generation

The goal: fresh Korean companies hiring developers are sourced, scored,
AI-qualified, drafted, and delivered **automatically every day**.

**Primary source = Wanted** (works today, no API key). Saramin is an optional
licensed alternative (see the bottom).

## The daily pipeline

`scripts/daily_wanted.sh` runs the whole thing and logs to `data/daily.log`:

```
source_wanted.py  → enrich → score → qualify (Claude) → outreach (Claude)
                  → build_platform.py → export_delivery → view_delivery
```

Run it once by hand to verify:
```bash
bash scripts/daily_wanted.sh
```
Outputs land in `data/` — open `data/platform.html`.

## Schedule it (cron)

```bash
chmod +x scripts/daily_wanted.sh        # once
crontab -e                              # add the line below
```
```
# every day at 12:00 (noon)
0 12 * * * /absolute/path/to/korea-leadgen/scripts/daily_wanted.sh
```

Now every day it re-sources fresh postings, re-scores, re-qualifies, and
refreshes the platform + delivery sheet automatically.

- The machine must be **awake** at the scheduled time (cron won't wake it).
- Run it on an **always-on company machine/server** for production — an
  intern's laptop won't be available after handover (see `docs/HANDOVER.md`).
- On macOS, if it silently doesn't run, grant Full Disk Access to `cron`
  (System Settings → Privacy & Security).

## Cost control

The AI steps (qualify + draft) call Claude once per lead, capped by `--top`
(default 10 in the script). Sourcing/scoring are free. Set the AI `--top` to `0`
to run scoring-only on the daily job and draft on demand. Needs `ANTHROPIC_API_KEY`
in `.env` (a company key for production).

## A note on collection

`source_wanted.py` reads Wanted's public listings programmatically. Whether to
run this — and at what scale — is a **company decision** (automated collection
can conflict with a site's ToS; see the script header). It is rate-limited,
capped, and does not collect personal contact data. For a commercial product,
prefer a licensed API.

## Optional: Saramin (licensed) instead of Wanted

If the company licenses Saramin's API, use the Saramin pipeline instead:
```bash
# put SARAMIN_API_KEY in .env, then:
python3 scripts/source_saramin.py --debug      # verify field mapping once
python3 scripts/run_live.py --fresh            # full run on real Saramin data
```
`run_live.py` is the Saramin-based equivalent of `daily_wanted.sh`. The scoring,
AI, and outputs are identical — only the source differs.
