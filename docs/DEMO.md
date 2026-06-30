# Demo Guide — Korea Lead-Gen (Data Track)

A one-command demo of the full pipeline, running on **sample data** (no API key
needed). With a real Saramin key it produces the same outputs from live Korean
job postings.

---

## Run it

```bash
cd ~/springboard/korea-leadgen
python3 scripts/demo.py        # runs the whole pipeline on sample data
open data/dashboard.html       # the funnel chart (in a browser)
```

That's it. Everything below is what the demo prints / produces.

---

## The pipeline (what runs)

```
sample companies → enrich → score → contacts → re-score → funnel dashboard
```

| Step | Script | Output |
|------|--------|--------|
| Source (sample) | `demo.py` seeds it | `companies_raw.csv` |
| Enrich | `enrich.py` | tech-stack + per-service fit + living DB (`companies_db.csv`) |
| Score | `score_leads.py` | ranked leads (`scored_leads.csv`) |
| Contacts | `make_contact_worksheet.py` → fill → `rescore_with_contacts.py` | `final_leads.csv` |
| Funnel | `dashboard.py` | `dashboard.html` |

---

## What the demo shows (4 things)

**1. Ranked leads** — companies sorted by fit score (who to contact first).

**2. Tech stack + best-fit service** — each company auto-classified:
`메디브릿지 → AI Implementation (PyTorch, ML)`, `그린팩토리 → Systems Integration`,
fintech/game → IT Servicing.

**3. Contact lift** — once a decision-maker is found, the score rises
(온누리페이 70 → 90), so reachable leads surface first.

**4. KPI funnel** — leads by stage with stage-to-stage conversion (the capstone visual).

---

## How the numbers work

### Fit score (0–100)
```
fit = 100 × (0.40 × firmographic + 0.40 × intent + 0.20 × reachability)
```
| Component | Basis |
|-----------|-------|
| firmographic | tech industry = 1.0 else 0.4, blended with size (0.5 placeholder until DART) |
| intent | open dev postings ÷ 5, capped at 1.0 (5+ = strong hiring signal) |
| reachability | email 1.0 · LinkedIn 0.6 · name 0.3 · none 0 (non-decision-maker capped 0.5) |

### Per-service fit
Each company is scored for all 4 offerings (IT Servicing / Manpower /
AI Implementation / Systems Integration) from its industry, job titles, and
tech stack; `best_service` = the highest.

### KPI funnel (8 stages, playbook §6.1)
target identified → contact identified → outreach sent → reply received →
call booked → call held → concrete interest → Korea-visit ready.
Each stage count = leads that reached at least that stage; conversion =
count ÷ previous count.

---

## Honest framing (say this to the mentor)

- **Sample data now** — with the API key it runs on real Saramin postings.
- **Scoring is a v1 heuristic** (40/40/20) — to be re-weighted in Week 3 using
  real response data (which segments/titles actually convert).
- **Saramin free tier = prototype only.** Commercial deployment would use a
  licensed / public-data source (the source layer is swappable).

---

## Files to show

- `data/dashboard.html` — the funnel (visual)
- terminal output of `demo.py` — ranked leads + tech/service + contact lift
- `docs/onepager.md` — the one-page summary
