# Korea Market Activation Platform — One-Pager

**Problem:** Finding Korean target companies by hand is slow, and it's hard to
know who to contact *first* and *what to say*.

**What we built:** one platform that sources real Korean companies actively
hiring developers, scores them against the ICP, uses AI to qualify and draft
outreach, and presents it all in a single shareable app.

```
  Wanted postings  →  companies + hiring signal  →  ICP score  →  Claude qualify  →  EN/KR outreach  →  platform + delivery sheet
  (developer roles)      (open dev roles)          (fit + intent)   (fit/maybe/no)     (what to say)
```

## Data source

- **Primary: Wanted** — where Korean tech SMEs hiring developers actually post.
  Collected directly (no API key needed). Best match for our ICP.
- **Optional: Saramin** — cleaner for commercial scale, but needs a paid/licensed
  API (free tier was unresponsive; Korean APIs may require a Korean business
  entity). Kept as a drop-in alternative.
- The source layer is **swappable** — every source writes the same schema, so
  the scoring/AI pipeline is unchanged whichever feed is used.

## Live demo — ranked leads (from real Wanted postings)

| Rank | Company | Fit | Verdict | Why |
|-----:|---------|----:|---------|-----|
| 1 | 앤서스랩코리아 (blockchain/gaming) | **70** | ✅ fit | 90-person SME, 5 open dev/data roles |
| 2 | 택토 (SaaS) | 54 | ✅ fit | multiple mid-level dev roles |
| 3 | 콜로세움코퍼레이션 (logistics tech) | 46 | ✅ fit | backend + infra hiring |
| … | (senior-only / single-role) | | 🟡 maybe | strict rubric — not rubber-stamped |

## How the score works (transparent, not a black box)

`score = firmographic fit (industry, 20–300 size) + hiring-signal strength + reachability`

Every score traces back to its evidence. AI qualification adds a strict
Fit/Maybe/Not-Fit verdict with written reasoning.

## The platform (5 views)

Overview · Pipeline (CRM) · KPI Funnel · Outreach Studio · Recommendation (DSS) —
one self-contained app, shareable by link.

## Status

- ✅ Sourcing + scoring + AI qualify/outreach + consolidated platform — working
- ✅ Runs automatically (daily cron on Wanted data)
- 🔴 Company decisions to productionize: licensed data path, company Anthropic
  key, repo transfer (see `docs/jake-update.md`)
