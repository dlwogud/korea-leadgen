# Presentation Guide — tomorrow (내일 발표용)

Everything for the demo in one place. English = what to say, 한국어 = for you.

---

## TL;DR — do this

1. Open `data/overview.html` (screenshot / on screen)
2. Run `python3 scripts/demo.py` (live)
3. Open `data/dashboard.html` (the funnel)
4. Read the 6 lines below. Done.

```bash
cd ~/springboard/korea-leadgen
python3 scripts/demo.py
open data/overview.html
open data/dashboard.html
```

---

## 30-second pitch (memorise this)

> "I built a data tool that finds Korean companies from job postings and ranks
> them as leads by how well they fit our services. It's a working prototype on
> sample data — when the API key arrives, it runs the same on real companies."

*(채용공고로 한국 기업 찾아서 우리 서비스 적합도로 리드 순위 매기는 데이터 툴이에요.
샘플 데이터로 도는 프로토타입이고, 키 오면 진짜 회사로 똑같이 작동해요.)*

---

## What to say, in order (demo script)

**1. Intro** — "I built a tool that finds Korean companies and ranks them as leads."
*(한국 기업 찾아서 리드로 순위 매기는 툴 만들었어요.)*

**2. Ranked leads** (terminal) — "Companies hiring many developers need more capacity, so they're strong leads. It ranks them by score."
*(개발자 많이 뽑는 회사 = 인력 필요 = 좋은 리드. 점수로 순위 매겨요.)*

**3. Tech + service** — "It also detects each company's tech stack and best-fit service — IT servicing, AI, or systems integration."
*(회사별 기술스택이랑 제일 맞는 서비스도 잡아요.)*

**4. Contact lift** — "When we add the decision-maker's contact, the score goes up, 70 to 90 — reachable leads come first."
*(담당자 연락처 넣으면 점수 올라가요, 70→90. 연락되는 리드가 먼저.)*

**5. Funnel** (dashboard.html) — "This is the KPI funnel from the playbook, with stage-by-stage conversion. It updates automatically."
*(문서의 KPI 퍼널이에요, 단계별 전환율. 자동 갱신돼요.)*

**6. Close** — "It's ICP-based, so once we agree the target profile, it produces the right leads. And it takes data from the API or a manual list — same pipeline."
*(ICP 기반이라 타겟 정해지면 맞는 리드 나와요. API든 수동 리스트든 같은 파이프라인이고요.)*

---

## If they ask (top answers)

- **"Is it commercial-legal?"** → free API = prototype only; no reselling. Commercial = company license decision.
  *(무료 API는 프로토타입용, 재판매 안 함. 상업화는 회사 결정.)*
- **"How's the score made?"** → 40% fit + 40% hiring signal + 20% contact. v1 heuristic, re-weighted later with real data.
  *(적합도40+채용40+연락20. v1이고 나중에 실데이터로 조정.)*
- **"Do we work in spreadsheets?"** → yes — it outputs a scored-leads spreadsheet; the database is just my engine.
  *(네, 점수 매긴 스프레드시트로 출력. DB는 제 엔진.)*
- **Full answers:** see `docs/FAQ.md`.

---

## What to ask them (see docs/mentor-questions.md)

Priority: **is my direction right? / which service area? / who sets the ICP?**
Plus (5-person cohort): **how are we split into tracks/teams?**

---

## Checklist

**Tonight**
- [ ] `python3 scripts/demo.py` runs cleanly
- [ ] `overview.html` + `dashboard.html` open fine
- [ ] read the 6 lines out loud once
- [ ] screenshot overview.html as backup

**Right before**
- [ ] terminal open in ~/springboard/korea-leadgen
- [ ] overview.html + dashboard.html ready in browser tabs
- [ ] GitHub link handy: github.com/dlwogud/korea-leadgen

**If English freezes:** "Let me show you" → point at the screen. The visuals carry it.
