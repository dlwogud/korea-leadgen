# Automation — from API key to fully hands-off

The goal: once the Saramin API key is in, fresh Korean job postings are sourced,
scored, AI-qualified, drafted, and delivered **automatically every day** — no
crawling (which is legally risky in Korea and not commercial-safe), just the
official API on a schedule.

## One-time setup (when the key arrives)

1. Put the key in `.env`:
   ```
   SARAMIN_API_KEY=...          # required
   ANTHROPIC_API_KEY=...        # for the AI qualify + draft steps
   ```

2. Confirm Saramin's response shape once (the client was built without a live
   response, so field names may need a small tweak):
   ```bash
   python3 scripts/source_saramin.py --debug
   ```
   Share the output if any field looks off — it's a 5-minute fix.

3. First real run, clean (drops the sample data):
   ```bash
   python3 scripts/run_live.py --fresh
   ```
   → produces `data/delivery.csv`, `data/leads.html`, `data/leadgen.db` on REAL leads.

## Daily automation (macOS cron)

`scripts/daily.sh` runs the whole live pipeline and logs to `data/daily.log`.

```bash
chmod +x scripts/daily.sh              # once
crontab -e                             # add the line below
```
```
# run every day at 9:00am
0 9 * * * /Users/ijaehyeong/springboard/korea-leadgen/scripts/daily.sh
```

Now every morning it re-sources new postings, re-scores, and refreshes the
delivery sheet + app automatically. (The Mac must be on at 9am; for 24/7, run it
on an always-on machine / the company's server later.)

## Why scheduling, not crawling

A crawler and the API both have to re-fetch to catch new postings — scheduling
solves that either way. The API route is the one to automate because:

- **Legal.** Scraping Saramin / JobKorea violates their ToS, and Korea has
  precedent (사람인 vs 잡코리아) treating job-posting crawling as unfair
  competition / DB-rights infringement. For a commercial product, that's real risk.
- **Stable.** APIs don't break when the website's HTML changes, and won't get
  IP-blocked by anti-bot systems.

## Cost control

The AI steps (qualify + draft) call Claude once per lead, so they're capped by
`--ai-top` (default 10). Scoring/sourcing themselves are free. Raise `--ai-top`
for more AI coverage, or set it to `0` to run scoring-only on the daily job and
generate AI drafts on demand.
