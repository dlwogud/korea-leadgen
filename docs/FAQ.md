# Anticipated Q&A — be ready for any question

Prep for the mentor / sync. English = what to say, 한국어 = meaning.
Core message: **it's a working prototype on sample data; the moment the Saramin
API key arrives, the exact same code runs on real Korean companies.**

---

## Status (상태)

**Q. Is it working now?**
> "Yes — the full pipeline runs end to end on sample data. The only thing pending
> is the Saramin API key. The moment it arrives, the same code runs on real
> companies — no rewrite needed."
> *(네, 전체 파이프라인이 샘플 데이터로 다 돌아가요. 사람인 API 키만 대기 중이고, 키 오면
> 똑같은 코드로 진짜 회사에 바로 돌아가요 — 다시 만들 거 없어요.)*

**Q. When will real data be ready?**
> "I applied for the free key; approval takes a few days. After that it's immediate."
> *(무료 키 신청했고 승인까지 며칠 걸려요. 그 다음엔 바로예요.)*

---

## Data source (데이터 소스)

**Q. Why Saramin?**
> "It's one of Korea's two biggest job boards, so coverage is broad — and it has
> a free API, which is ideal for a prototype."
> *(한국 양대 채용 플랫폼 중 하나라 커버가 넓고, 무료 API가 있어서 프로토타입에 딱이에요.)*

**Q. What about Wanted or JobKorea?**
> "Wanted is stronger for tech startups, but it has no free API. JobKorea is broad
> like Saramin but also no easy free API. So Saramin is the best free + broad
> choice. The source is swappable if we want to add others later."
> *(원티드는 테크 스타트업에 강한데 무료 API가 없어요. 잡코리아도 넓지만 무료 API가 어렵고요.
> 그래서 사람인이 무료+넓은 최선이에요. 소스는 나중에 교체 가능하게 설계했어요.)*

**Q. Public data (WorkNet)?**
> "I built a WorkNet version as a commercial-safe fallback, but its data is staler.
> Saramin is fresher for the prototype."
> *(워크넷 버전도 상업용 백업으로 만들어놨는데 데이터가 더 오래된 편이라, 프로토타입엔 사람인이
> 더 신선해요.)*

---

## Licensing / commercial (라이선스 / 상업성)

**Q. Is using the free Saramin API allowed for this?**
> "The free terms forbid reselling the data or charging for a service built on it —
> we do neither. Using it internally to decide who to contact, as a prototype, is
> fine. Whether to use it for ongoing commercial outreach is a company decision."
> *(무료 약관은 데이터 재판매나 그걸로 만든 서비스 요금받기를 금지하는데, 우린 둘 다 안 해요.
> 누구한테 연락할지 내부 판단에 쓰는 프로토타입은 괜찮고, 지속적 상업 아웃리치로 쓸지는 회사
> 결정이에요.)*

**Q. So is this commercial use?**
> "It has a business purpose, but it doesn't break the specific terms (no resale,
> no charging). For commercial scale-up, the company would get a proper license —
> that's not for me to decide."
> *(영업 목적은 있지만 구체적 약관(재판매·요금)은 안 어겨요. 본격 상업화하면 회사가 정식
> 라이선스 받는 거고, 제가 정할 일은 아니에요.)*

**Q. The 500-calls-a-day limit?**
> "We stay well under it — only a handful of calls per run."
> *(한참 안 넘어요 — 한 번 실행에 몇 번 호출뿐이에요.)*

---

## Scoring (점수)

**Q. How does the score work?**
> "40% company fit, 40% hiring-signal strength, 20% reachability. A tech company
> hiring many developers, with a known contact, scores highest."
> *(적합도 40 + 채용신호 40 + 연락가능성 20. 개발자 많이 뽑는 테크 회사에 연락처까지 있으면
> 최고점이에요.)*

**Q. Are the weights validated?**
> "Not yet — it's a v1 heuristic. I'll re-weight it in Week 3 using real response
> data, to learn which segments actually convert."
> *(아직요 — v1 휴리스틱이에요. 3주차에 실제 응답 데이터로 재조정할 거예요.)*

**Q. Why those weights?**
> "They're reasonable starting hypotheses, and every score is explainable — we can
> always trace why a lead ranks high."
> *(합리적 출발 가설이고, 모든 점수가 설명 가능해요 — 왜 높은지 추적돼요.)*

---

## Coverage & tool (커버리지 & 도구)

**Q. Does it cover all 4 services?**
> "Yes — each company is scored for all four. Job postings fit IT-Servicing and
> Manpower best; AI-Implementation and Systems-Integration would be sharper with a
> news signal, which I can add."
> *(네, 회사마다 4개 다 점수 매겨요. 채용공고는 IT서비싱·인력배치에 잘 맞고, AI구축·시스템통합은
> 뉴스 신호 더하면 정확해져요 — 추가 가능.)*

**Q. What did you actually build?**
> "Source → enrich (tech stack + service fit) → score → find contacts → funnel
> dashboard, all backed by a real SQLite database."
> *(소싱 → enrich(기술스택+서비스적합) → 점수 → 연락처 → 퍼널 대시보드, 전부 진짜 SQLite
> DB 위에서요.)*

**Q. Is it a database or a spreadsheet?**
> "Internally it's a real queryable database, but it outputs spreadsheets — so the
> team uses it in their normal workflow. The engine is mine; the deliverable is a
> scored-leads spreadsheet."
> *(내부는 진짜 쿼리되는 DB인데, 출력은 스프레드시트예요 — 팀은 평소대로 쓰면 돼요. 엔진은
> 제 거, 드리는 건 점수 매겨진 리드 스프레드시트.)*

---

## Adoption / next steps (도입 / 다음 단계)

**Q. We work in spreadsheets — does this fit?**
> "Yes. The tool produces a scored-leads spreadsheet you can use as usual; the
> database is just my internal engine. Where should I deliver it?"
> *(네. 점수 매겨진 리드 스프레드시트를 뽑아드려요, 평소대로 쓰시면 돼요. DB는 제 내부 엔진이고요.
> 어디로 드릴까요?)*

**Q. What's missing / what's next?**
> "Company size (via DART), and the weekly response analysis — which needs real
> outreach data from Week 2. Next is the API key, then real data, then contacts."
> *(기업 규모(DART)랑 주간 응답 분석 — 이건 2주차 실제 데이터가 있어야 해요. 다음은 API 키,
> 그다음 실데이터, 연락처예요.)*

**Q. Privacy — you store contact emails?**
> "Minimal fields, and I'll follow whatever company policy you have. Compliance is
> a company/legal matter."
> *(최소 필드만, 회사 방침 따를게요. 컴플라이언스는 회사/법무 영역이고요.)*

---

## If you forget everything, say this (다 까먹으면 이것만)

> "It's a working prototype on sample data. When the API key arrives, the same
> code runs on real companies, and I deliver a scored-leads spreadsheet for the
> team."
> *(샘플 데이터로 도는 프로토타입이에요. 키 오면 똑같은 코드로 진짜 회사에 돌고, 팀엔 점수
> 매겨진 리드 스프레드시트로 드려요.)*
