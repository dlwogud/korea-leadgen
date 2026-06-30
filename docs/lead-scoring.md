# Lead Scoring — Design v1

How any company gets a **0–100 lead score** so the Business track always works
the most promising leads first. v1 is a transparent heuristic; v2 (Week 3)
re-weights it using real response data.

## Two layers

1. **`service_fit.fit_score`** (per service, 0–100) — how well a company matches
   one offering's ICP. A company can fit several offerings.
2. **`lead_scores.score`** (per company, 0–100) — overall priority = best fit
   plus engagement, used to rank the outreach queue.

## v1 heuristic — fit_score (per service)

Weighted sum of evidence, capped at 100:

| Factor | Weight | Example |
|--------|--------|---------|
| Firmographic match (size / industry / region vs ICP) | 40 | 51–200 SaaS in Seoul for IT Servicing |
| Intent signal strength (`signals`) | 40 | 5+ unfilled dev roles, "급구", AI initiative press |
| Reachability (decision-maker contact found) | 20 | named CTO with email/LinkedIn |

```
fit_score = min(100, 40*firmographic + 40*intent + 20*reachability)
# each component normalised to 0..1 before weighting
```

## v1 heuristic — overall score

```
score = 0.7 * max(fit_score over services)   # best-fit offering
      + 0.3 * engagement_bonus               # any reply / positive touch so far
```

`engagement_bonus` starts at 0 and rises as a lead moves down the funnel
(`pipeline_events`): a company that already replied outranks an untouched one
of equal fit.

## v2 (Week 3) — data-informed re-weight

Once Week-2 outreach produces real replies, recompute weights from what
actually converted:
- Which firmographic segments / titles / signals correlate with replies and
  booked calls? (DS-track weekly analysis, playbook §5.2)
- Adjust the 40/40/20 split and segment multipliers accordingly.
- Bump `model_version` to `v2-fitted`; keep v1 rows for comparison.

Keep it explainable — the Friday sync needs "why is this lead ranked high",
not a black box. Every score stores its `features` JSONB so any ranking can be
traced back to the evidence.

## Guardrail

A long list of low-fit names is worse than a few high-fit relationships
(playbook §2.3). Scoring exists to **focus** outreach, not to inflate target
counts.
