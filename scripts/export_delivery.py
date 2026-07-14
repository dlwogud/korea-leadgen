"""Export the operational lead list for the sales team — the real deliverable.

The website is the demo/visualization; THIS CSV is what the sales team filters,
reviews, and works from. One row per Korean IT lead with the full field set:
firmographics + contact + hiring signal + AI qualification + outreach draft +
pipeline stage. Saved as UTF-8-with-BOM so it opens cleanly in Excel (Korean
text intact).

Columns that aren't collected yet (website, phone, HR email/name, search
keyword) are included as blank columns for the team / enrichment to fill.

    python scripts/export_delivery.py   →   data/delivery.csv  (opens in Excel)
"""
from __future__ import annotations

import csv
from urllib.parse import quote

from _common import DATA_DIR

OUT = DATA_DIR / "delivery.csv"

# Full operational schema (order matches the sales-team spec).
FIELDS = [
    "company_name",       # 회사명
    "industry",           # 업종
    "company_size",       # 회사 규모 (approx. employees)
    "website",            # 공식 웹사이트 (enrichment pending)
    "job_posting_url",    # 채용공고 링크
    "hr_email",           # HR 이메일
    "phone",              # 전화번호 (enrichment pending)
    "hr_contact_name",    # HR 담당자명
    "roles",              # 채용 직무
    "location",           # 근무 위치
    "tech_stack",         # 기술스택
    "open_roles",         # 채용 인원 / 채용 중인 역할 수
    "source",             # 데이터 출처
    "search_keyword",     # 검색 키워드 (enrichment pending)
    "summary",            # 회사/채용공고 요약 (AI)
    "best_service",       # 가장 적합한 Springboard 서비스
    "fit_score",          # ICP 적합도 점수
    "ai_verdict",         # AI 판정 (fit / maybe / not_fit)
    "outreach_angle",     # 아웃리치 관점
    "outreach_message",   # 이메일 초안 (Claude)
    "pipeline_stage",     # 현재 파이프라인 단계
    "notes",              # 비고 (blank — team fills)
]

# Short outreach angle per best-fit service.
ANGLE = {
    "it_servicing": "Take over dev delivery with a vetted Filipino team — faster & cheaper than local hiring",
    "manpower": "Place vetted Filipino developers directly into their team",
    "ai_implementation": "Build practical AI tools & workflows for them",
    "systems_integration": "Build & integrate their systems (ERP, cloud, modernization)",
}


def _read(name):
    p = DATA_DIR / name
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def _bi(kr, en):
    """'Korean (English)' when an English gloss exists, else just Korean."""
    kr = (kr or "").strip()
    en = (en or "").strip()
    return f"{kr} ({en})" if en and en != kr else kr


def main() -> None:
    leads = _read("final_leads.csv") or _read("scored_leads.csv")
    db = {r["company_name"]: r for r in _read("companies_db.csv")}
    drafts = {d["company_name"]: d.get("message", "") for d in _read("outreach_drafts.csv")}
    contacts = {c["company_name"]: c for c in _read("contacts_worksheet.csv")}
    quals = {q["company_name"]: q for q in _read("qualified_leads.csv")}

    rows = []
    for lead in leads:
        name = lead.get("company_name", "")
        d, c, q = db.get(name, {}), contacts.get(name, {}), quals.get(name, {})
        service = lead.get("best_service", "") or d.get("best_service", "")
        msg = drafts.get(name, "")
        rows.append({
            "company_name": _bi(name, d.get("company_en", "")),
            "industry": _bi(lead.get("industry", "") or d.get("industry", ""), d.get("industry_en", "")),
            "company_size": d.get("employees", ""),
            "website": "",                                   # enrichment pending
            "job_posting_url": d.get("source_url", "") or ("https://www.wanted.co.kr/search?query=" + quote(name)),
            "hr_email": lead.get("email", "") or c.get("email", ""),
            "phone": c.get("phone", ""),                     # enrichment pending
            "hr_contact_name": lead.get("contact_name", "") or c.get("full_name", ""),
            "roles": _bi((d.get("sample_titles", "") or lead.get("sample_titles", "") or "").replace(";", ", "),
                         (d.get("roles_en", "") or "").replace("; ", ", ").replace(";", ", ")),
            "location": _bi(d.get("locations", "") or lead.get("locations", ""), d.get("location_en", "")),
            "tech_stack": (d.get("tech_stack", "") or lead.get("tech_stack", "") or "").replace(";", ", "),
            "open_roles": lead.get("hiring_count", "") or d.get("hiring_count", ""),
            "source": d.get("source", "") or lead.get("source", ""),
            "search_keyword": "",                            # not tracked yet
            "summary": q.get("reason", ""),                  # AI qualification reasoning
            "best_service": service,
            "fit_score": lead.get("fit_score", ""),
            "ai_verdict": q.get("verdict", ""),
            "outreach_angle": ANGLE.get(service, ""),
            "outreach_message": msg,
            "pipeline_stage": "Outreach Drafted" if msg else "Target Identified",
            "notes": "",
        })

    DATA_DIR.mkdir(exist_ok=True)
    # utf-8-sig so Excel renders Korean correctly
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    with_msg = sum(1 for r in rows if r["outreach_message"])
    fit = sum(1 for r in rows if r["ai_verdict"] == "fit")
    print(f"Wrote {len(rows)} leads → data/delivery.csv  "
          f"({fit} fit, {with_msg} with an outreach draft). Opens in Excel.")


if __name__ == "__main__":
    main()
