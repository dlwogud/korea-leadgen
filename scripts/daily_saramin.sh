#!/bin/bash
# Daily live run — SARAMIN (licensed) path. The DEFAULT is daily_wanted.sh.
# Use this only if the company has licensed the Saramin API (SARAMIN_API_KEY).
# Schedule with cron (see docs/AUTOMATION.md). Logs to data/daily.log.
cd "$(dirname "$0")/.." || exit 1
echo "===== $(date) =====" >> data/daily.log
python3 scripts/run_live.py --ai-top 10 >> data/daily.log 2>&1
echo "" >> data/daily.log
