"""AI-track: generate a personalized Korean first-touch message per top lead.

Two modes, chosen automatically:
  • CLAUDE mode  — if ANTHROPIC_API_KEY is set and the `anthropic` SDK is
    installed, uses Claude (claude-opus-4-8) to write a tailored message.
  • TEMPLATE mode — otherwise, fills a Korean template from the company's
    signals. Works with no key, so it's demo-ready today.

Reads scored_leads.csv (or companies_db.csv), writes data/outreach_drafts.md.
Every message is a DRAFT — the playbook requires human approval before sending.

Run:
    python scripts/generate_messages.py --top 3
    # to use Claude: export ANTHROPIC_API_KEY=...  (pip install anthropic)
"""
from __future__ import annotations

import argparse
import csv
import os

from _common import DATA_DIR, RAW_CSV, load_dotenv

DRAFTS_MD = DATA_DIR / "outreach_drafts.md"
DRAFTS_CSV = DATA_DIR / "outreach_drafts.csv"

# Value proposition per best-fit service (Korean)
SERVICE_VALUE = {
    "it_servicing": "개발 업무를 검증된 필리핀 팀이 통째로 맡아 처리하는 아웃소싱",
    "manpower": "검증된 필리핀 개발자를 귀사 팀에 직접 배치하는 인력 지원",
    "ai_implementation": "실용적인 AI 도구와 워크플로우를 만들어 드리는 AI 구축",
    "systems_integration": "ERP·클라우드 등 시스템을 구축·통합해 드리는 서비스",
}
SERVICE_LABEL = {
    "it_servicing": "IT 서비싱", "manpower": "인력 배치",
    "ai_implementation": "AI 구축", "systems_integration": "시스템 통합",
}


def _leads(top: int) -> list[dict]:
    db = DATA_DIR / "companies_db.csv"
    src = db if db.exists() else RAW_CSV
    with src.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # already ranked if from scored_leads; else sort by hiring_count
    scored = DATA_DIR / "scored_leads.csv"
    if scored.exists():
        with scored.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return rows[:top]


def template_message(lead: dict) -> str:
    name = lead.get("company_name", "")
    titles = (lead.get("sample_titles", "") or "").split(";")
    role = titles[0] if titles and titles[0] else "개발"
    hiring = lead.get("hiring_count", "")
    best = lead.get("best_service", "it_servicing")
    value = SERVICE_VALUE.get(best, SERVICE_VALUE["it_servicing"])
    return (
        f"안녕하세요, {name} 채용 담당자님.\n\n"
        f"{name}에서 '{role}' 등 개발 포지션을 채용 중이신 것을 보고 연락드립니다. "
        f"인력 충원이 빠르게 필요하신 상황일 것 같습니다.\n\n"
        f"저희 Springboard는 이런 부분을 도와드립니다 — {value}. 한국에서 직접 "
        f"채용하시는 것보다 빠르고 비용 효율적으로 팀을 확장하실 수 있습니다.\n\n"
        f"혹시 15분 정도 짧게 이야기 나눠볼 수 있을까요? 감사합니다."
    )


def claude_message(client, lead: dict) -> str:
    name = lead.get("company_name", "")
    facts = (
        f"Company: {name}\n"
        f"Industry: {lead.get('industry','')}\n"
        f"Open roles (signal): {lead.get('sample_titles','')}\n"
        f"Number of IT openings: {lead.get('hiring_count','')}\n"
        f"Tech stack: {lead.get('tech_stack','')}\n"
        f"Best-fit service: {SERVICE_LABEL.get(lead.get('best_service',''), lead.get('best_service',''))}"
    )
    system = (
        "You write B2B outbound for Springboard Philippines, which provides vetted "
        "Filipino IT talent and services to Korean companies. Write a short, warm, "
        "professional first-touch cold email IN KOREAN (정중한 존댓말), 4-6 sentences. "
        "Personalize to the company's hiring signal. Natural, not salesy. No subject "
        "line. End with a soft ask for a 15-minute call."
    )
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": f"Write the message for:\n{facts}"}],
    )
    return next((b.text for b in resp.content if b.type == "text"), "").strip()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate personalized outreach drafts.")
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()

    # pick mode
    use_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
    client = None
    if use_claude:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except Exception as e:
            print(f"[warn] Claude unavailable ({e}); using template mode.")
            use_claude = False
    mode = "Claude (claude-opus-4-8)" if use_claude else "template"

    leads = _leads(args.top)
    DATA_DIR.mkdir(exist_ok=True)
    lines = [f"# Outreach drafts — {mode} mode\n",
             "> DRAFTS. Every message must be approved by Jake / Mel / Rey before sending.\n"]
    drafts = []
    for i, lead in enumerate(leads, 1):
        msg = claude_message(client, lead) if use_claude else template_message(lead)
        service = SERVICE_LABEL.get(lead.get("best_service", ""), "")
        lines.append(f"\n## {i}. {lead.get('company_name','')} "
                     f"(fit {lead.get('fit_score','')}, {service})\n")
        lines.append(f"```\n{msg}\n```\n")
        drafts.append({"company_name": lead.get("company_name", ""),
                       "fit_score": lead.get("fit_score", ""),
                       "service": service, "mode": mode, "message": msg})

    DRAFTS_MD.write_text("\n".join(lines), encoding="utf-8")
    with DRAFTS_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company_name", "fit_score", "service", "mode", "message"])
        w.writeheader()
        w.writerows(drafts)
    print(f"[{mode}] wrote {len(drafts)} drafts → data/outreach_drafts.md (+ .csv)")
    if drafts:
        print("\n" + "-" * 60)
        print(f"Sample draft — {drafts[0]['company_name']}:\n")
        print(drafts[0]["message"])


if __name__ == "__main__":
    main()
