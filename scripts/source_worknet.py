"""Data source: WorkNet (고용노동부) job postings → company hiring signals.

This is the COMMERCIAL-SAFE alternative to source_saramin.py. WorkNet data is
served through Korea's public-data programme (work.go.kr / data.go.kr), whose
terms generally permit commercial use — unlike the Saramin free tier. Use this
source if the tool is deployed for real commercial lead-gen.

It emits the SAME company schema (_common.COMPANY_FIELDS) as the Saramin
source, so scoring / contacts / dashboard are unchanged. That is the whole
point of the swappable source layer.

⚠️ VERIFY-BEFORE-RUN
--------------------
This client is written from the documented shape of the WorkNet Open API but
has NOT been run against a live key yet. The three things to confirm against
the official docs / first --debug response are marked `# VERIFY`:
  - API_URL (endpoint)
  - request param names (authKey / callTp / returnType / paging / filters)
  - response field paths in _parse_items()
Get a free key at https://www.data.go.kr (search "워크넷 채용정보") or
https://www.work.go.kr (고용24 오픈API).

Run:
    export WORKNET_API_KEY=...            # or korea-leadgen/.env
    python scripts/source_worknet.py --debug      # confirm response shape first
    python scripts/source_worknet.py --pages 3
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import xml.etree.ElementTree as ET

import requests

from _common import load_dotenv, write_companies

# VERIFY: WorkNet 채용정보 Open API endpoint (XML list service)
API_URL = "https://openapi.work.go.kr/opi/opi/opiservice/wantedApi.do"

DISPLAY_PER_CALL = 100        # rows per call (VERIFY max)
SAFETY_MAX_CALLS = 50         # hard stop well under fair-use
SLEEP_BETWEEN_CALLS = 0.4

# VERIFY: occupation filter for IT/dev roles. WorkNet uses 직종코드 (occupation
# codes). Left blank = all postings; set once the IT code is confirmed.
IT_OCCUPATION_CODE = ""       # e.g. "133" family for 정보통신 — confirm in docs


def worknet_call(key: str, start_page: int, debug: bool = False) -> str:
    """One API call → raw XML text."""
    params = {
        "authKey": key,            # VERIFY param name
        "callTp": "L",             # VERIFY: 'L' = list
        "returnType": "XML",       # VERIFY
        "startPage": start_page,    # VERIFY paging param
        "display": DISPLAY_PER_CALL,  # VERIFY
    }
    if IT_OCCUPATION_CODE:
        params["occupation"] = IT_OCCUPATION_CODE  # VERIFY filter param name
    resp = requests.get(API_URL, params=params, timeout=20)
    resp.raise_for_status()
    if debug:
        print(f"[debug] start_page={start_page} status={resp.status_code} "
              f"first 400 chars:\n{resp.text[:400]}\n", file=sys.stderr)
    return resp.text


def _text(node, *tags):
    """Return the first non-empty child text among candidate tag names."""
    for tag in tags:
        el = node.find(tag)
        if el is not None and (el.text or "").strip():
            return el.text.strip()
    return ""


def _parse_items(xml_text: str) -> list[dict]:
    """Extract postings from the XML. VERIFY tag names against a real response."""
    root = ET.fromstring(xml_text)
    items = root.findall(".//wanted") or root.findall(".//item")  # VERIFY container tag
    out = []
    for it in items:
        out.append({
            "company": _text(it, "company", "coNm", "companyName"),   # VERIFY
            "title":   _text(it, "title", "wantedTitle", "empWantedTitle"),  # VERIFY
            "industry": _text(it, "industry", "indTpNm", "industryName"),    # VERIFY
            "region":  _text(it, "region", "workRegion", "areaNm"),          # VERIFY
            "url":     _text(it, "wantedInfoUrl", "empWantedHomepgDetail", "url"),  # VERIFY
            "id":      _text(it, "wantedAuthNo", "empSeqno", "id"),          # VERIFY
        })
    return out


def fetch_companies(key: str, pages: int, debug: bool = False) -> list[dict]:
    by_company: dict = {}
    seen_ids: set = set()
    calls = 0

    for page in range(1, pages + 1):
        if calls >= SAFETY_MAX_CALLS:
            print(f"[guard] hit SAFETY_MAX_CALLS={SAFETY_MAX_CALLS}; stopping.", file=sys.stderr)
            break
        xml_text = worknet_call(key, page, debug=debug)
        calls += 1
        items = _parse_items(xml_text)
        if not items:
            break
        for it in items:
            jid = it["id"]
            if jid and jid in seen_ids:
                continue
            if jid:
                seen_ids.add(jid)
            name = it["company"].strip()
            if not name:
                continue
            rec = by_company.setdefault(name, {
                "company_name": name, "industry": it["industry"], "_locations": set(),
                "hiring_count": 0, "_titles": [], "source": "worknet", "source_url": it["url"],
            })
            rec["hiring_count"] += 1
            if it["region"]:
                rec["_locations"].add(it["region"])
            if it["title"] and len(rec["_titles"]) < 5:
                rec["_titles"].append(it["title"])
            if not rec["industry"] and it["industry"]:
                rec["industry"] = it["industry"]
        time.sleep(SLEEP_BETWEEN_CALLS)

    rows = []
    for rec in by_company.values():
        rec["locations"] = ";".join(sorted(rec.pop("_locations")))
        rec["sample_titles"] = ";".join(rec.pop("_titles"))
        rows.append(rec)
    rows.sort(key=lambda r: r["hiring_count"], reverse=True)
    print(f"[ok] worknet: {calls} call(s) → {len(rows)} unique companies", file=sys.stderr)
    return rows


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Source Korean companies from WorkNet (public data).")
    parser.add_argument("--pages", type=int, default=3, help="pages to fetch")
    parser.add_argument("--debug", action="store_true", help="dump raw response to confirm shape")
    args = parser.parse_args()

    key = os.getenv("WORKNET_API_KEY")
    if not key:
        sys.exit("ERROR: set WORKNET_API_KEY (env var or korea-leadgen/.env). "
                 "Free key: https://www.data.go.kr (search 워크넷 채용정보).")

    rows = fetch_companies(key, args.pages, debug=args.debug)
    if not rows:
        print("No rows parsed. Run with --debug and share the raw XML so the "
              "field mappings (# VERIFY) can be corrected.", file=sys.stderr)
    write_companies(rows)
    print(f"Wrote {len(rows)} companies → data/companies_raw.csv")
    print("Next: python scripts/score_leads.py")


if __name__ == "__main__":
    main()
