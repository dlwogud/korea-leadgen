"""One-command demo on SAMPLE data — no API key needed.

Runs the whole pipeline end to end so you can show it live:
  sample companies → score → contacts → re-score → funnel dashboard

    python scripts/demo.py

Then open data/dashboard.html in a browser. Everything here is SAMPLE data;
with a real Saramin key, `source_saramin.py` produces the same files from live
job postings.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
DATA.mkdir(exist_ok=True)

# ---- sample Korean companies (stand-in for live Saramin output) -------------
SAMPLE_COMPANIES = [
    # name, industry, locations, hiring_count, sample_titles
    ("온누리페이", "핀테크", "서울 > 강남구", 6, "백엔드 개발자 Java/Spring;서버 개발자 AWS;DevOps 엔지니어 Kubernetes"),
    ("스타라이트게임즈", "게임 소프트웨어", "경기 > 성남시", 4, "서버 개발자 Java;백엔드 개발자 Kotlin"),
    ("클라우드웍스", "IT 솔루션", "서울 > 마포구", 3, "DevOps AWS/Terraform;백엔드 Node.js;데이터 엔지니어 Kafka"),
    ("한빛로지스", "물류", "서울 > 송파구", 2, "백엔드 개발자 Java;데이터 엔지니어 SQL"),
    ("메디브릿지", "헬스케어 플랫폼", "서울 > 강남구", 3, "백엔드 개발자 Spring;ML 엔지니어 PyTorch;QA 엔지니어"),
    ("그린팩토리", "제조업", "경남 > 창원시", 1, "전산 담당자"),
    ("데이터노바", "데이터 솔루션", "서울 > 영등포구", 5, "데이터 엔지니어 Spark/Airflow;ML 엔지니어 TensorFlow;백엔드 Python"),
    ("핀콘", "이커머스", "서울 > 강남구", 2, "프론트엔드 개발자 React/TypeScript;QA"),
]


def seed_companies() -> None:
    path = DATA / "companies_raw.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["company_name", "industry", "locations", "hiring_count",
                    "sample_titles", "source", "source_url"])
        for i, (name, ind, loc, cnt, titles) in enumerate(SAMPLE_COMPANIES, 1):
            w.writerow([name, ind, loc, cnt, titles, "sample", f"https://example.com/{i}"])
    print(f"[demo] seeded {len(SAMPLE_COMPANIES)} sample companies")


def fill_some_contacts() -> None:
    """Pretend we researched 2 decision-makers, to show the score rising."""
    path = DATA / "contacts_worksheet.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        if r["company_name"] == "온누리페이":
            r.update(full_name="김철수", title="CTO", email="cto@onnuri.example",
                     linkedin_url="", is_decision_maker="y")
        elif r["company_name"] == "데이터노바":
            r.update(full_name="박영희", title="Head of Eng", email="",
                     linkedin_url="linkedin.com/in/yh", is_decision_maker="y")
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print("[demo] filled 2 sample decision-maker contacts")


def seed_pipeline_events() -> None:
    """Sample funnel: 8 leads dropping off through the stages."""
    stages_for = {
        "온누리페이": "concrete_interest", "데이터노바": "call_held",
        "클라우드웍스": "call_booked", "스타라이트게임즈": "reply_received",
        "메디브릿지": "reply_received", "핀콘": "outreach_sent",
        "한빛로지스": "outreach_sent", "그린팩토리": "contact_identified",
    }
    path = DATA / "pipeline_events.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["company_name", "service", "stage", "entered_at", "note"])
        for name, stage in stages_for.items():
            w.writerow([name, "it_servicing", stage, "2026-07-08T09:00:00+00:00", ""])
    print(f"[demo] seeded {len(stages_for)} sample funnel events")


def run(script: str, *args: str) -> None:
    print(f"\n{'='*64}\n▶ {script} {' '.join(args)}\n{'='*64}")
    r = subprocess.run([sys.executable, str(HERE / script), *args])
    if r.returncode != 0:
        sys.exit(f"demo step failed: {script}")


def main() -> None:
    print("\n### KOREA LEAD-GEN — DEMO (sample data, no API key needed) ###")
    seed_companies()
    run("enrich.py")
    run("score_leads.py")
    run("make_contact_worksheet.py", "--top", "8")
    fill_some_contacts()
    run("rescore_with_contacts.py")
    seed_pipeline_events()
    run("dashboard.py")
    run("build_db.py")
    print(f"\n{'#'*64}")
    print("DEMO COMPLETE. Show these:")
    print("  • terminal output above (ranked leads + contact lift + funnel)")
    print("  • data/dashboard.html   ← open in a browser (the visual)")
    print("  • docs/onepager.md      ← the summary")
    print('#'*64)


if __name__ == "__main__":
    main()
