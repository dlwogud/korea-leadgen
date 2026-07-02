# Demo Script — what to say (English + 한국어)

Open `docs/onepager.md` and run `python3 scripts/demo.py`, then read these lines
in order. English = what to say, 한국어 = meaning.

---

## ① Intro (뭔지)
> "This is a tool that finds Korean companies for our services, and ranks them
> by how good a lead they are."

*(우리 서비스에 맞는 한국 기업을 찾아서, 좋은 리드 순으로 순위 매기는 툴이에요.)*

## ② Ranked leads (순위 보여주며)
> "It looks at job postings. Companies hiring many developers need more
> capacity — so they are strong leads. Here they are, ranked by score."

*(채용공고를 봐요. 개발자 많이 뽑는 회사는 인력이 더 필요하니까 좋은 리드예요. 점수순으로 나와요.)*

## ③ Tech stack + service (기술·서비스 분류)
> "For each company, it also detects the tech stack and picks the best-fit
> service — IT servicing, AI, or systems integration."

*(회사마다 기술스택도 잡고, 제일 맞는 서비스를 골라줘요 — IT서비싱, AI, 시스템통합.)*

## ④ Contact lift (연락처 효과 — 제일 인상적)
> "When we find the decision-maker's contact, the score goes up — from 70 to 90.
> So reachable leads come first."

*(담당자 연락처 찾으면 점수가 올라가요 — 70에서 90으로. 연락되는 리드가 먼저 와요.)*

## ⑤ AI outreach draft (초안 카드 가리키며)
> "It even drafts a personalized Korean outreach message per lead. Template now,
> and with an API key it uses Claude to write them. Every message is a draft that
> gets approved before sending."

*(리드마다 맞춤 한국어 메시지 초안까지 만들어요. 지금은 템플릿, 키 넣으면 Claude가 써요.
모든 메시지는 승인 후 발송하는 초안이고요.)*

## ⑥ KPI funnel (dashboard.html 열며)
> "This is the KPI funnel from the playbook. It shows how many leads reach each
> stage, and the conversion rate. It updates automatically."

*(문서의 KPI 퍼널이에요. 단계별 도달 수랑 전환율을 보여줘요. 자동으로 갱신돼요.)*

## ⑦ Honest closing (정직한 마무리 — 점수 따는 포인트)
> "Right now it runs on sample data. With the API key, it works the same on real
> companies. The scoring is a first version — I'll improve the weights using
> real response data later."

*(지금은 샘플 데이터예요. 키 넣으면 진짜 회사로 똑같이 작동해요. 점수는 1차 버전이고,
나중에 실제 응답 데이터로 가중치 개선할 거예요.)*


## If you only memorise 3 lines (3문장만)
1. "It finds and ranks Korean companies as leads." (찾고 순위 매긴다)
2. "Reachable leads with strong hiring signals score higher." (연락되고 채용 많은 회사가 높은 점수)
3. "Sample data now — same thing with the real API key." (지금 샘플, 키 넣으면 진짜)

---

## Run order (실행 순서)
```
1. open docs/onepager.md          # 배경 요약 띄우기
2. python3 scripts/demo.py        # 파이프라인 실행 → ②③④ 보여주기
3. open data/dashboard.html       # ⑤ 퍼널 보여주기
4. say ⑥                          # 정직한 마무리
```
