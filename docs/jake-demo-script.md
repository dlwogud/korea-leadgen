# Jake Demo Script — Korea Lead-Gen Tool

A ~4-minute live walkthrough + the two things the company must own to run it in
production (the data-source API and the Claude API).

---

## 0. One-line pitch (say this first)

> "This tool takes real Korean job postings, uses AI to qualify which companies
> fit our ICP, and auto-drafts outreach — so the team gets a ranked, ready-to-
> action lead list instead of manually hunting. The engine is done; today I'll
> show it running on real companies."

---

## 1. Live demo — click by click (~2 min)

Open `data/leads.html`.

1. **The list** — "These are 27 real companies pulled from live Wanted postings.
   Ranked by fit score, and on ties the AI-qualified 'fit' leads rank above 'maybe'."
2. **Stat cards** — point at *AI-qualified fit* count (3) and *Avg fit score*.
3. **Click 앤서스랩코리아 (top ✅ fit)** — show the detail panel:
   - 🤖 **AI qualification**: "fit, high — 90-employee blockchain SME hiring 5
     dev/data roles." → "This reasoning is written live by Claude, not a template."
   - ✉️ **AI outreach draft**: English + Korean, naming their actual 5 roles.
4. **Click a 🟡 maybe (e.g. 센트비)** — "The AI says *maybe* because the roles are
   senior-only. It's strict — it doesn't rubber-stamp." (This sells credibility.)
5. **Search / filter** — type "AI" or "핀테크", or filter verdict = fit. Typo-
   tolerant, Korean↔English.

**Key line:** "It's not just a list — it scores, judges, and drafts. A teammate
opens this and knows who to contact and what to say."

---

## 2. How it works (~30 sec)

`source (job API) → enrich → score vs ICP → AI qualify → AI outreach → delivery sheet`

- ICP-driven (size 20-300, tech industries, dev-hiring signal) — all configurable.
- Outputs a `delivery.csv` the team pastes into the shared Google Sheet.
- Runs end-to-end automatically; `daily.sh` can schedule it every morning.

---

## 3. The AI = real Claude (the Claude API talk)

> "The qualification and outreach are powered by **Claude (Anthropic's API)** —
> model `claude-opus-4-8`. It's live AI, not canned text."

**Two honest points:**

1. **Right now it runs on MY personal Anthropic key** (just for this demo).
2. **For production, the company needs its own Anthropic API key + billing** —
   same as the data source. I built it so you just drop the company key into
   `.env` and it switches over. No code change.

**Cost (Claude):** roughly **a few cents per lead** (each lead = 1 qualify call +
1 outreach draft on Opus 4.8, ~$0.03–0.05/lead all-in).

| Daily AI volume | Approx. Claude cost |
|---|---|
| 20 leads/day | ~$0.6–1.0/day (~$20–30/mo) |
| 100 leads/day | ~$3–5/day (~$90–150/mo) |

**Cost controls already built in:**
- `--ai-top N` — only AI-qualify the top N leads (scoring/sourcing are free).
- Set `--ai-top 0` to run scoring-only and generate drafts on demand.
- Can switch to a cheaper model (Sonnet 4.6 / Haiku 4.5) if we want lower cost.

---

## 4. What the company must own for production (the ask)

Two API keys — both a company decision, not something an intern can license:

| # | API | Why | Note |
|---|-----|-----|------|
| 1 | **Job-data API** (Saramin paid / Wanted OpenAPI / WorkNet) | Legal auto-sourcing of postings | Free tiers forbid commercial use; crawling is legally risky (사람인 vs 잡코리아 precedent). Wanted OpenAPI needs a 사업자번호 → company applies. |
| 2 | **Anthropic (Claude) API** | Powers AI qualify + outreach | Company key + billing; ~a few cents/lead. |

> "Today's demo uses my personal keys + a small hand-collected sample to prove
> the engine. To run it for real, daily, at scale, the company plugs in these two
> keys — and it's fully automated from there."

---

## 5. Closing / next steps

- ✅ Engine, automation, and handoff docs are done and in the repo.
- 🔜 Decisions for the team: (a) which job-data API to license, (b) approve an
  Anthropic key, (c) repo transfer to Springboard.
- Ask Jake: "Which data source should we pursue, and can we get a company
  Anthropic key so I can wire production billing?"

---

*Files to have open: `data/leads.html` (main), `data/overview.html` (summary
screenshot). Repo: github.com/dlwogud/korea-leadgen.*
