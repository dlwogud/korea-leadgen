"""AI lead qualifier — Claude judges each company against the ICP, with reasoning.

Complements the numeric score: instead of just 0-100, Claude reads the company
and returns a verdict (fit / maybe / not_fit) + confidence + a short reason in
Korean. Directly answers the team's ask for "qualified leads."

Uses Claude (claude-opus-4-8) when ANTHROPIC_API_KEY is set; falls back to a
simple rule-based verdict otherwise (so it still runs for a demo without a key).

    python scripts/qualify_leads.py --top 5
"""
from __future__ import annotations

import argparse
import csv
import json
import os

from _common import DATA_DIR, RAW_CSV, load_dotenv

QUALIFIED_CSV = DATA_DIR / "qualified_leads.csv"

# The confirmed ICP, in plain text for the model
ICP_TEXT = """Ideal Customer Profile (confirmed by the team):
- Target: Korean tech SMEs / mid-market with an acute developer/IT talent shortage.
- Firm size: 20-300 employees (the segment under the most hiring pressure).
- Industries: tech-enabled — SaaS, fintech, gaming, e-commerce platforms,
  IT services / system integrators. NOT heavy manufacturing or chaebol-adjacent.
- Roles needed: mid-level developers, QA, DevOps, customer support (CX),
  back-office ops — expensive/slow to fill domestically.
- Buying trigger: actively hiring but blocked by cost or time-to-fill
  (several open roles, long-open positions).
- Priority services: IT servicing + manpower placement."""

SYSTEM = (
    "You qualify B2B leads for Springboard Philippines, which supplies vetted "
    "Filipino IT talent and services to Korean companies. Given one company, "
    "judge how well it fits the Ideal Customer Profile below. Give the reason in "
    "English, one or two sentences.\n\n" + ICP_TEXT + "\n\n"
    "Apply this STRICT verdict rubric (default to the lower verdict when unsure):\n"
    "- 'fit' ONLY IF ALL THREE hold: (1) clearly a tech-enabled industry "
    "(SaaS / fintech / gaming / e-commerce / IT-services); (2) size CONFIRMED "
    "within 20-300 employees (unknown size => NOT fit); (3) a STRONG hiring-"
    "pressure signal = at least TWO open MID-LEVEL developer/QA/DevOps/CX roles. "
    "Senior-only roles, a single opening, or unconfirmed size can NEVER be 'fit'.\n"
    "- 'maybe' if tech-enabled and plausibly in range, but the signal is weak "
    "(only 1 role), roles are senior-only, or size is unconfirmed.\n"
    "- 'not_fit' if non-tech industry, clearly outside 20-300, or no dev-hiring signal.\n"
    "Reserve 'high' confidence for cases that plainly satisfy or plainly fail the rubric."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["fit", "maybe", "not_fit"]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "confidence", "reason"],
    "additionalProperties": False,
}

TECH_INDUSTRY_HINTS = ["it", "정보통신", "소프트웨어", "솔루션", "플랫폼", "게임",
                       "인터넷", "모바일", "핀테크", "이커머스", "saas", "데이터", "헬스케어"]


def _facts(company: dict) -> str:
    return (
        f"Company: {company.get('company_name','')}\n"
        f"Industry: {company.get('industry','')}\n"
        f"Open roles: {company.get('sample_titles','')}\n"
        f"Number of IT openings: {company.get('hiring_count','')}\n"
        f"Tech stack: {company.get('tech_stack','')}\n"
        f"Region: {company.get('locations','')}\n"
        + (f"Approx. employees: {company.get('employees')}"
           if (company.get('employees') or "").strip()
           else "(size unknown from job data)")
    )


def qualify_claude(client, company: dict) -> dict:
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user",
                   "content": f"Qualify this company against the ICP:\n\n{_facts(company)}"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    text = next((b.text for b in resp.content if b.type == "text"), "{}")
    return json.loads(text)


def qualify_rule(company: dict) -> dict:
    """Fallback without a key — a rough verdict from the fields we have."""
    industry = (company.get("industry", "") or "").lower()
    hiring = int(company.get("hiring_count") or 0)
    is_tech = any(h in industry for h in TECH_INDUSTRY_HINTS) or bool(company.get("tech_stack"))
    if is_tech and hiring >= 3:
        return {"verdict": "fit", "confidence": "medium",
                "reason": "Tech company hiring several engineers — a clear talent-shortage signal (rule-based estimate)."}
    if is_tech and hiring >= 1:
        return {"verdict": "maybe", "confidence": "low",
                "reason": "Tech company but few openings, so the hiring-pressure signal is weak (rule-based estimate)."}
    return {"verdict": "not_fit", "confidence": "medium",
            "reason": "Not a tech company or no dev-hiring signal, so it's outside the ICP (rule-based estimate)."}


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="AI-qualify leads against the ICP.")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    use_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
    client = None
    if use_claude:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except Exception as e:
            print(f"[warn] Claude unavailable ({e}); using rule-based verdicts.")
            use_claude = False
    mode = "Claude (claude-opus-4-8)" if use_claude else "rule-based"

    db = DATA_DIR / "companies_db.csv"
    src = db if db.exists() else RAW_CSV
    with src.open(encoding="utf-8") as f:
        companies = list(csv.DictReader(f))[: args.top]

    rows = []
    for c in companies:
        v = qualify_claude(client, c) if use_claude else qualify_rule(c)
        rows.append({"company_name": c.get("company_name", ""),
                     "verdict": v["verdict"], "confidence": v["confidence"],
                     "reason": v["reason"]})

    DATA_DIR.mkdir(exist_ok=True)
    with QUALIFIED_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_name", "verdict", "confidence", "reason"])
        w.writeheader()
        w.writerows(rows)

    icon = {"fit": "✅", "maybe": "🟡", "not_fit": "❌"}
    print(f"[{mode}] qualified {len(rows)} leads → data/qualified_leads.csv\n")
    for r in rows:
        print(f"{icon.get(r['verdict'],'?')} {r['company_name']}  ({r['verdict']}, {r['confidence']})")
        print(f"   {r['reason']}\n")


if __name__ == "__main__":
    main()
