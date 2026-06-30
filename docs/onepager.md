# Korea Lead-Gen — Automated Prospecting (Data Track)

**Problem:** Finding Korean target companies by hand is slow, and it's hard to
know who to contact *first*.

**What I built:** a pipeline that sources real Korean companies, detects a
buying signal, and ranks them — so outreach starts with the best leads.

```
  Saramin API  →  companies + hiring signal  →  lead score 0–100  →  ranked list
  (job postings)      (open dev roles)          (fit + intent)       (who to contact first)
```

## Live demo — ranked leads

| Rank | Company | Fit score | Open dev roles | Why |
|-----:|---------|----------:|---------------:|-----|
| 1 | 온누리페이 (fintech) | **70** | 6 | tech company, hiring many engineers = needs capacity |
| 2 | 스타라이트게임즈 (game) | 62 | 4 | tech company, strong hiring signal |
| 3 | 클라우드웍스 (IT solution) | 54 | 3 | IT company, hiring |
| 4 | 한빛로지스 (logistics) | 34 | 2 | weaker fit / fewer roles |
| 5 | 대성제조 (manufacturing) | 26 | 1 | low fit, almost no IT hiring |

*(sample data shown — same output with real Saramin data once the API key is added)*

## How the score works (transparent, not a black box)

`score = 40% industry/firmographic fit + 40% hiring-signal strength + 20% reachability`

Every score can be traced back to its evidence (stored per company).

## Why it matters

- Plugs straight into the program's **8-stage KPI funnel** — each lead's stage
  is tracked, so stage-by-stage conversion comes for free.
- Shared data backbone: **Business** track works the top-ranked leads,
  **AI** track feeds new companies in, **Data** track measures conversion.

## Safe & extensible

- Saramin **free tier**, prototype use only (≤500 calls/day, no resale).
  Commercial scale-up = company licensing decision.
- Data source is **swappable** — can move to public-data WorkNet or a licensed
  source without changing the scoring.

## Status & next

- ✅ Sourcing + scoring pipeline working
- ⏳ Add free API key → run on real postings
- ⏭ Contact enrichment (decision-makers), funnel dashboard
