# Gaps & Open Risks — living checklist

An honest, running audit of what's weak or missing. Updated as we go. Each item:
what's missing → why it matters → fix → whether it's blocked on a mentor answer.

Legend: 🔴 high  🟡 medium  🟢 low   ·   🔒 = blocked on mentor decision

---

## A. Pipeline completeness (the source→...→reply loop)

- 🔴 **Reply → re-score feedback loop not built.** Playbook §5.2/§6 wants Week-3
  re-weighting from real responses. Today scoring is a static heuristic; there's
  no mechanism to learn "which segments actually replied" and update weights.
  *Fix:* after Week-2 outreach, compute reply rates per segment/title/signal and
  refit the 40/40/20 weights (model_version → v2-fitted).
- 🟡 **No outreach message generation.** If we own outreach (or all 3 tracks),
  there's no first-touch / follow-up message drafting (the AI-track personalization
  deliverable). *Fix:* templated + AI-personalized drafts, human-approved. 🔒 needs
  track/channel decision.
- 🟡 **Reply tracking is manual.** Funnel events are logged by hand. Fine at small
  scale, but if outreach is via email we can auto-detect replies. 🔒 needs channel.

## B. Coverage (data & signals)

- 🟡 **One signal source, but now scored for all 4 services.** `enrich.py` scores
  fit for IT-Servicing / Manpower / AI-Implementation / Systems-Integration from
  job + tech-stack signals. Still only *job postings* as the source, though —
  AI-Implementation would be sharper with *news/intent* (Naver), SI with
  *legacy/DX* signals. *Fix:* add a news source. 🔒 needs the pod's service area.
- 🟡 **Saramin keyword mode misses title variants** until category mode is wired
  (needs the IT `job_mid_cd`, discoverable with `--list-categories` once a key
  exists). WorkNet client is written but unverified against a live response.
- 🟢 **WorkNet coverage may under-represent hot tech startups** vs Saramin.

  ✅ *Closed:* tech-stack signal extraction, per-service fit scoring (all 4),
  and a continuously-updated DB with first_seen/last_seen (`enrich.py` →
  companies_db.csv) — closes most of DS-track §5.2 item #1.

## C. Data quality / engineering

- 🟡 **Company dedup is by name string.** Same company under variant spellings
  ("(주)온누리페이" vs "온누리페이") counts as two. *Fix:* normalise names /
  match on domain (the schema already has a `domain` unique key — wire it).
- ✅ ~~**Schema vs CSV split.**~~ *Closed:* `build_db.py` loads the CSVs into a
  real SQLite DB (db/schema_sqlite.sql → data/leadgen.db); `query_db.py` runs
  SQL (joins, views, funnel). The DB is now queryable, not just spreadsheets.
- 🟢 **No automated tests.** Pure functions (scoring, reachability, parsing) are
  easily unit-testable. *Fix:* a small pytest suite.
- 🟢 **Firmographic size is a 0.5 placeholder** (Saramin gives no employee count).
  *Fix:* enrich via DART for real size bands.

## D. Compliance / legal (matters most if commercial)

- 🔴 **Data-source licensing.** Saramin free tier forbids commercial resale/charging
  → prototype only. Commercial deployment must use a commercial-OK source
  (WorkNet/public data) or a paid Saramin license. 🔒 company decision.
- 🔴 **Personal data (PIPA / 개인정보보호법).** We plan to store decision-maker
  names/emails. Storing & processing personal data for outreach has consent and
  handling obligations in Korea. *Fix:* minimise stored fields, document purpose,
  follow company policy. 🔒 company/legal owns this.
- 🟡 **Outbound email regulation (정보통신망법).** Unsolicited commercial email to
  Korean recipients has rules (consent, 광고 labelling). B2B has some leeway but
  it's not unrestricted. 🔒 Jake/company handles compliance.

## E. Validation

- 🟡 **Scoring weights are unproven guesses.** 40/40/20 is a hypothesis, not
  validated against outcomes (see A: feedback loop).
- 🟡 **ICP profiles are hypotheses,** to be confirmed/killed by real Week-2
  responses (playbook explicitly expects this).

## F. Organisational unknowns (🔒 — resolve with mentor first)

These gate a lot of the above. See `mentor-questions.md`.
- Which track(s) am I on — one, or all three?
- Which service area(s) is the pod focused on? (drives which signals matter)
- Is this prototype-only, or heading to commercial use? (drives source choice)
- Outreach channel + CRM? (drives reply automation + dashboard target)
- Program end date / capstone date?

---

## Priority order to close (once direction is set)

1. Confirm direction (Section F) — unblocks everything.
2. Contact/firmographic enrichment + name dedup (B/C) — makes leads actionable & clean.
3. Reply → re-score loop (A) — the DS-track intellectual core, Week 3.
4. SQLite wiring + tests (C) — credibility/robustness.
5. Second signal source for the pod's service area (B) — if not IT-Servicing.
