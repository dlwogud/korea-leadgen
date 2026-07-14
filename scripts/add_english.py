"""Add English glosses to the Korean lead data so an English-speaking team can
read it, without mistranslating names.

For each company it adds four columns to companies_db.csv:
  company_en   — the company's official English name, or a clean romanization
                 (NOT a meaning-translation)
  industry_en  — industry translated to natural English
  location_en  — place names romanized (e.g. 서울 강남구 → "Seoul, Gangnam-gu")
  roles_en     — job titles translated to English (';'-separated, order kept)

Translations are cached in data/translations.csv keyed by company, so reruns
only translate NEW companies (cheap). Run AFTER enrich.py (which rebuilds
companies_db) and before export/build.

Uses Claude when ANTHROPIC_API_KEY is set; otherwise leaves the *_en blank
(the pipeline still works, just Korean-only).

    python scripts/add_english.py
"""
from __future__ import annotations

import csv
import json
import os

from _common import DATA_DIR, load_dotenv

DB = DATA_DIR / "companies_db.csv"
CACHE = DATA_DIR / "translations.csv"
EN_FIELDS = ["company_en", "industry_en", "location_en", "roles_en"]

SYSTEM = (
    "You add English to Korean B2B lead data for an English-speaking sales team. "
    "Rules: for the company name give its OFFICIAL English name if you know it, "
    "otherwise a clean romanization — never a meaning-translation. For the "
    "location, romanize place names (e.g. '서울 강남구' → 'Seoul, Gangnam-gu'). "
    "For industry and job titles, translate to natural English. Keep job titles "
    "in the same order, separated by '; '. Be concise; no notes."
)
SCHEMA = {
    "type": "object",
    "properties": {
        "company_en": {"type": "string"},
        "industry_en": {"type": "string"},
        "location_en": {"type": "string"},
        "roles_en": {"type": "string"},
    },
    "required": EN_FIELDS,
    "additionalProperties": False,
}


def load_cache() -> dict:
    if not CACHE.exists():
        return {}
    with CACHE.open(encoding="utf-8") as f:
        return {r["company_name"]: r for r in csv.DictReader(f)}


def save_cache(cache: dict) -> None:
    with CACHE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_name"] + EN_FIELDS)
        w.writeheader()
        for name, r in cache.items():
            w.writerow({"company_name": name, **{k: r.get(k, "") for k in EN_FIELDS}})


def translate(client, row: dict) -> dict:
    facts = (f"Company (Korean): {row.get('company_name','')}\n"
             f"Industry: {row.get('industry','')}\n"
             f"Location: {row.get('locations','')}\n"
             f"Job titles: {row.get('sample_titles','')}")
    resp = client.messages.create(
        model="claude-opus-4-8", max_tokens=512, system=SYSTEM,
        messages=[{"role": "user", "content": facts}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    return json.loads(text)


def main() -> None:
    load_dotenv()
    if not DB.exists():
        raise SystemExit("companies_db.csv not found — run enrich.py first.")
    with DB.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        cols = list(rows[0].keys()) if rows else []

    cache = load_cache()
    client = None
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
        except Exception as e:
            print(f"[warn] Claude unavailable ({e}); leaving *_en blank.")

    new = 0
    for r in rows:
        name = r["company_name"]
        if name not in cache:
            if client:
                try:
                    cache[name] = {"company_name": name, **translate(client, r)}
                    new += 1
                except Exception as e:
                    print(f"[warn] {name}: {e}")
                    cache[name] = {"company_name": name, **{k: "" for k in EN_FIELDS}}
            else:
                cache[name] = {"company_name": name, **{k: "" for k in EN_FIELDS}}
        for k in EN_FIELDS:
            r[k] = cache[name].get(k, "")

    save_cache(cache)
    out_cols = cols + [c for c in EN_FIELDS if c not in cols]
    with DB.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in out_cols})

    print(f"Added English glosses to {len(rows)} companies "
          f"({new} newly translated, rest from cache) → companies_db.csv")


if __name__ == "__main__":
    main()
