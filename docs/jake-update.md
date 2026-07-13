# Progress Update + Open Questions — Korea Market Activation Platform

_For Jake. What's new since last review, one structural finding, and the few
decisions we still need from you (resolved items dropped)._

---

## 1. Headline: one consolidated platform

Working from what we each built, the team combined the **strongest parts of our
work** into a single **Korea Market Activation Platform** — one navigable app
covering the full BD flow. (It brings together the best features and structure
we developed; the remaining data layers, e.g. contact enrichment, plug in next.)

| View | What it does |
|------|--------------|
| **Overview** | KPIs, top leads, service/priority mix, funnel at a glance |
| **Pipeline (CRM)** | Searchable lead table: priority (High/Med/Low), AI verdict, evidence, detail |
| **KPI Funnel** | The playbook's 8-stage funnel (real events only — honesty principle) |
| **Outreach Studio** | Claude EN/KR drafts, searchable |
| **Recommendation (DSS)** | Go / Pilot / No-Go, data-driven |

It runs as a **single self-contained file** (no server) and is shareable by link.
Contact/evidence columns are wired and ready for the contact data to plug in.

## 2. What's inside (capabilities)

- **ICP-driven** scoring (size 20–300, tech industries, dev-hiring signal) — config-driven.
- **Real Claude AI** (`claude-opus-4-8`): qualifies each lead fit/maybe/not_fit **with reasoning**, and writes an **English + Korean** outreach draft.
- **Strict, defensible qualification**: 'fit' requires tech industry + confirmed 20–300 size + 2+ mid-level dev roles → on the current demo set, 3 fit / rest maybe (it discriminates, doesn't rubber-stamp).
- **Search** (KR↔EN) across pipeline and drafts; **fit-first ranking**.
- **API-ready**: drop a data key in `.env` → the whole pipeline runs automatically; `daily_wanted.sh` schedules it.
- Live demo on **27 real Korean companies** (sourced from live listings).

## 3. Structural finding — data sourcing for a PH company ⚠️

Springboard **and** SyncTalents are both Philippine entities — **no Korean
business registration**. Every official Korean job-data API is gated accordingly:

| Source | Barrier |
|--------|---------|
| Saramin (free API) | Applied → **ignored for a week**, follow-up email still unread |
| WorkNet (public data) | Needs Korean identity verification (본인인증); also commercial-prohibited license |
| Wanted OpenAPI | Needs a Korean business number (사업자등록번호) |

→ **Fully-automated + legal Korean sourcing needs either a paid B2B license or a
Korean contracting entity.** Crawling works for the prototype (small, internal,
no resale — low risk), but is **not a clean foundation for a commercial product**.

---

## 4. Decisions we still need from you

_(Budget/entity/contact are now one cluster; the "is semi-auto OK" and generic
"do we have a Korean entity" questions are resolved and dropped.)_

**Q1 — Commercial data path.** For automated, legal, sellable sourcing we need a
licensed feed. Two options, both need you:
  (a) pursue a **paid B2B license** with Saramin/Wanted **as a foreign company**
      — can a **company rep** make this inquiry? (our intern-level requests were ignored), or
  (b) is there **any Korean partner/client** we could contract the license through?

**Q2 — Claude (Anthropic) key.** The AI runs on a personal key (demo only). For
production the company needs its **own Anthropic key + billing** (~a few cents
per lead, controllable). Can we set up a company account to switch to?

**Q3 — Consolidation + repo.** We've merged into one team platform. OK to
continue on this as the single deliverable — and proceed with the **repo transfer
to Springboard**?

---

## 5. Current limitations (known — and how each closes)

Being upfront about where the prototype stands:

- **Prototype-grade data.** Runs on 27 companies sourced once by hand; employee sizes are approximate estimates and contact details aren't filled in yet. → closes with a licensed feed + contact enrichment.
- **Not yet live-automated.** The pipeline is API-ready but currently sourced manually — automation is proven in design, not yet running end-to-end. → closes once a data key is added.
- **Small scale.** 27 companies is a demo set; real BD needs hundreds. Scale is untested. → closes with the automated feed.
- **No outcomes yet.** No real responses or meetings — the funnel is honestly near-empty past "drafted." A working tool, not yet traction (expected at this stage).
- **Consolidation is at the feature/UI level.** The platform unifies the strongest features and structure; deeper data integration (e.g., contact enrichment) plugs in next.

## 6. Status at a glance

- ✅ **Done:** unified platform (5 views), ICP scoring, real Claude qualify + outreach, search, delivery sheet, automation scripts, handoff docs.
- 🟡 **Proven via prototype data:** live demo on 27 real companies.
- 🔴 **Needs your decision:** commercial data license (Q1), company Anthropic key (Q2), consolidation/repo (Q3).

_Q1–Q3 answered → we wire the licensed source + company key → the platform runs
fully automatically._
