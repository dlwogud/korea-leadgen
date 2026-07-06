#!/bin/bash
# Daily live run — sources fresh Saramin postings and refreshes the leads.
# Schedule with cron (see docs/AUTOMATION.md). Logs to data/daily.log.
cd "$(dirname "$0")/.." || exit 1
echo "===== $(date) =====" >> data/daily.log
python3 scripts/run_live.py --ai-top 10 >> data/daily.log 2>&1
echo "" >> data/daily.log
