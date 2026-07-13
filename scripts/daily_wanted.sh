#!/bin/bash
# Daily live run — scrapes fresh Wanted dev postings and refreshes the whole
# pipeline (score → AI qualify → outreach → platform → delivery sheet).
# Scheduled via cron at 12:00 daily. Logs to data/daily.log.
#
# NOTE: whether to run this (crawling Wanted) is a company decision — see the
# header of source_wanted.py. Rate-limited and capped by design.

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"
cd "$(dirname "$0")/.." || exit 1

LOG=data/daily.log
echo "===== $(date) — Wanted daily run =====" >> "$LOG"

python3 scripts/source_wanted.py --pages 5   >> "$LOG" 2>&1   # scrape fresh postings
python3 scripts/enrich.py                    >> "$LOG" 2>&1   # tech stack + living DB merge
python3 scripts/score_leads.py               >> "$LOG" 2>&1   # ICP score
python3 scripts/qualify_leads.py --top 10    >> "$LOG" 2>&1   # Claude fit/maybe/not_fit
python3 scripts/generate_messages.py --top 10 >> "$LOG" 2>&1  # Claude EN/KR outreach
python3 scripts/platform.py                  >> "$LOG" 2>&1   # rebuild consolidated app
python3 scripts/export_delivery.py           >> "$LOG" 2>&1   # team delivery CSV
python3 scripts/view_delivery.py             >> "$LOG" 2>&1   # delivery sheet HTML

echo "done $(date)" >> "$LOG"
echo "" >> "$LOG"
