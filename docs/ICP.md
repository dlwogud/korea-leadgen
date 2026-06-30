# ICP Hypotheses — Korean Market, per Service Area

Ideal Customer Profile **hypotheses** for each offering. These are starting
assumptions to be validated against real Week-2 responses, not facts. Each
profile lists the firmographic fit, the buying signals we can detect, the
likely decision-maker, and the core value proposition for the cold message.

> Priority for this cohort: **IT Servicing (primary)**, **AI Implementation
> (secondary)**. SI and Manpower kept here for completeness.

---

## 1. IT Tech Servicing — staff augmentation / outsourced delivery  ★ PRIMARY

**Who:** Korean tech-enabled SMEs and scale-ups (≈50–500 employees) with more
software demand than they can hire for locally. Product companies, agencies,
and digital teams inside non-tech firms.

**Buying signals (detectable):**
- Many open dev/QA/DevOps roles posted for weeks (unfilled = capacity gap).
- Job posts mentioning "급구" / urgent hiring, or repeated reposting.
- Public roadmap/launch pressure (funding round, new product) without headcount.

**Decision-maker:** CTO, VP Engineering, Head of Dev, or founder (in startups).

**Value prop:** "Add vetted Filipino engineers/QA to your team in weeks, not
months — lower cost than local hiring, English-speaking, time-zone aligned."

**Why first:** Springboard's core competency, and Korea's high dev cost +
talent shortage makes the pain concrete and the pitch easy to open.

---

## 2. AI Implementation — practical AI tools & workflows  ★ SECONDARY

**Who:** Mid-to-large Korean firms (and ambitious startups) that *want* AI but
lack in-house ML/data engineering to ship it. Especially ops-heavy businesses
(retail, logistics, manufacturing, services) sitting on usable data.

**Buying signals:**
- Job posts for "AI/ML" roles they can't fill, or no ML team but public AI ambition.
- Press/blog announcing an "AI 전환" / digital initiative.
- Heavy manual workflows (support, sourcing, document processing) ripe for automation.

**Decision-maker:** CDO/CTO, Head of Innovation/Strategy, DX lead.

**Value prop:** "Get a working AI workflow live without building an ML team —
we scope, build, and hand it over." The cohort's own AI tools are the live demo.

**Why second:** highest 2026 interest = best email open rate, but the build/sell
is heavier, so anchor it as the door-opener rather than the volume play.

---

## 3. Systems Integration — ERP / CRM / cloud migration

**Who:** Traditional mid-large enterprises modernising legacy systems —
manufacturing, distribution, retail, finance back-office.

**Buying signals:** legacy ERP (old SAP/Oracle/homegrown), cloud-migration job
posts, "디지털 전환" RFPs, M&A driving system consolidation.

**Decision-maker:** IT Director, CIO, ERP/PMO lead.

**Value prop:** "Implement and integrate your business systems with a delivery
team that scales." Longer sales cycle — lower priority for a 4-week sprint.

---

## 4. International Skilled Manpower Placement

**Who:** Korean firms with sustained IT hiring they can't fill locally and
openness to foreign talent (E-7 visa track).

**Buying signals:** chronic open reqs, prior foreign-hire history, public
statements about talent shortage.

**Decision-maker:** HR/Talent lead + hiring manager (CTO/Eng).

**Value prop:** "Source, vet, and place skilled Filipino IT professionals into
your team." Visa/relocation friction makes it slower to convert cold — lowest
priority for the sprint, but high-value for accounts already feeling the pain.

---

## How this maps to the database

- `companies.industry / employee_band / hq_region` → firmographic fit
- `signals` (type=`hiring`/`tech_stack`/`news`/`funding`) → the buying signals above
- `service_fit.fit_score` → how strongly a company matches each profile
- `lead_scores.score` → overall prioritisation (see `lead-scoring.md`)
