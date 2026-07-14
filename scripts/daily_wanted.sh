#!/bin/bash
# Daily live run — scrapes fresh Wanted dev postings and refreshes the whole
# pipeline (score → AI qualify → outreach → platform → delivery sheet).
# Scheduled via cron at 12:00 daily. Logs to data/daily.log.
#
# NOTE: whether to run this (crawling Wanted) is a company decision — see the
# header of source_wanted.py. Rate-limited and capped by design.

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"
cd "$(dirname "$0")/.." || exit 1

# Optional auto-publish: set PAGES_DIR to a local clone of your GitHub Pages repo.
# If set, the daily run pushes the refreshed platform + leads there so the shared
# link auto-updates every day. Leave empty to skip publishing.
PAGES_DIR="${PAGES_DIR:-}"

LOG=data/daily.log
echo "===== $(date) — Wanted daily run =====" >> "$LOG"

python3 scripts/source_wanted.py --pages 5   >> "$LOG" 2>&1   # scrape fresh postings
python3 scripts/enrich.py                    >> "$LOG" 2>&1   # tech stack + living DB merge
python3 scripts/add_english.py               >> "$LOG" 2>&1   # English glosses (KR→EN) for the team
python3 scripts/score_leads.py               >> "$LOG" 2>&1   # ICP score
python3 scripts/qualify_leads.py --top 10    >> "$LOG" 2>&1   # Claude fit/maybe/not_fit
python3 scripts/generate_messages.py --top 10 >> "$LOG" 2>&1  # Claude EN/KR outreach
python3 scripts/export_delivery.py           >> "$LOG" 2>&1   # team delivery CSV (embedded into platform)
python3 scripts/build_platform.py            >> "$LOG" 2>&1   # rebuild consolidated app (embeds CSV)
python3 scripts/view_delivery.py             >> "$LOG" 2>&1   # delivery sheet HTML

# auto-publish to the shared GitHub Pages link (only if PAGES_DIR is a git clone)
if [ -n "$PAGES_DIR" ] && [ -d "$PAGES_DIR/.git" ]; then
  cp data/platform.html "$PAGES_DIR/index.html"
  cp data/leads.html    "$PAGES_DIR/leads.html"
  git -C "$PAGES_DIR" add -A >> "$LOG" 2>&1
  git -C "$PAGES_DIR" commit -q -m "Auto-update $(date +%F)" >> "$LOG" 2>&1 \
    && git -C "$PAGES_DIR" push -q origin main >> "$LOG" 2>&1 \
    && echo "published to Pages" >> "$LOG"
fi

echo "done $(date)" >> "$LOG"
echo "" >> "$LOG"
