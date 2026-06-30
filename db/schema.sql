-- Korea Lead-Gen prospect database — schema v1
-- PostgreSQL. Service-area-agnostic: supports all 4 offerings, focus is a
-- strategy choice made in scoring/outreach, not baked into the tables.
--
--   companies → contacts → outreach → pipeline_events
--   companies → signals (firmographic/technographic evidence)
--   companies → service_fit + lead_scores (prioritisation)

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------
CREATE TYPE service_area AS ENUM (
    'it_servicing',        -- outsourced dev / QA / sysadmin / support
    'systems_integration', -- ERP, CRM, cloud migration
    'ai_implementation',   -- practical AI tools & workflows
    'manpower_placement'   -- placing Filipino IT talent into Korean firms
);

CREATE TYPE funnel_stage AS ENUM (
    'target_identified',     -- 1
    'contact_identified',    -- 2
    'outreach_sent',         -- 3
    'reply_received',        -- 4
    'call_booked',           -- 5
    'call_held',             -- 6
    'concrete_interest',     -- 7
    'korea_visit_ready'      -- 8
);

CREATE TYPE outreach_channel AS ENUM ('email', 'linkedin', 'call', 'other');
CREATE TYPE outreach_status  AS ENUM ('queued', 'sent', 'bounced', 'replied', 'no_response');
CREATE TYPE signal_type      AS ENUM ('hiring', 'tech_stack', 'news', 'funding', 'other');

-- ---------------------------------------------------------------------------
-- Core: companies
-- ---------------------------------------------------------------------------
CREATE TABLE companies (
    company_id      BIGSERIAL PRIMARY KEY,
    name_ko         TEXT NOT NULL,
    name_en         TEXT,
    domain          TEXT UNIQUE,              -- natural key for dedupe
    industry        TEXT,
    sub_industry    TEXT,
    employee_band   TEXT,                     -- e.g. '11-50','51-200','201-500'
    revenue_band    TEXT,
    hq_region       TEXT,                     -- e.g. 'Seoul','Gyeonggi','Busan'
    founded_year    INT,
    source          TEXT,                     -- where we found it (AI tool, list, referral)
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Evidence: signals (technographic / firmographic / intent)
-- These are the raw features the lead score is built from.
-- ---------------------------------------------------------------------------
CREATE TABLE signals (
    signal_id     BIGSERIAL PRIMARY KEY,
    company_id    BIGINT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    type          signal_type NOT NULL,
    value         TEXT NOT NULL,              -- e.g. 'hiring: 5x backend engineer'
    source_url    TEXT,
    observed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_signals_company ON signals(company_id);

-- ---------------------------------------------------------------------------
-- Which service(s) a company fits, with a per-service fit score + rationale.
-- A company can fit more than one offering.
-- ---------------------------------------------------------------------------
CREATE TABLE service_fit (
    company_id   BIGINT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    service      service_area NOT NULL,
    fit_score    NUMERIC(5,2),               -- 0-100, see docs/lead-scoring.md
    rationale    TEXT,
    PRIMARY KEY (company_id, service)
);

-- ---------------------------------------------------------------------------
-- Overall lead score (versioned, so we can re-score with Week-3 real data).
-- features stored as JSONB for transparency / model iteration.
-- ---------------------------------------------------------------------------
CREATE TABLE lead_scores (
    score_id      BIGSERIAL PRIMARY KEY,
    company_id    BIGINT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    score         NUMERIC(5,2) NOT NULL,      -- 0-100
    model_version TEXT NOT NULL,              -- e.g. 'v1-heuristic','v2-fitted'
    features      JSONB,
    scored_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_lead_scores_company ON lead_scores(company_id);

-- ---------------------------------------------------------------------------
-- Decision-maker contacts
-- ---------------------------------------------------------------------------
CREATE TABLE contacts (
    contact_id        BIGSERIAL PRIMARY KEY,
    company_id        BIGINT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    full_name         TEXT,
    title             TEXT,
    seniority         TEXT,                   -- 'C-level','VP','Director','Manager'
    is_decision_maker BOOLEAN DEFAULT FALSE,
    email             TEXT,
    linkedin_url      TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_contacts_company ON contacts(company_id);

-- ---------------------------------------------------------------------------
-- Outreach attempts (each send/follow-up is a row)
-- ---------------------------------------------------------------------------
CREATE TABLE outreach (
    outreach_id   BIGSERIAL PRIMARY KEY,
    contact_id    BIGINT NOT NULL REFERENCES contacts(contact_id) ON DELETE CASCADE,
    service       service_area NOT NULL,      -- which offering this touch pitched
    channel       outreach_channel NOT NULL,
    status        outreach_status NOT NULL DEFAULT 'queued',
    template_id   TEXT,                       -- approved sequence reference
    sent_at       TIMESTAMPTZ,
    replied_at    TIMESTAMPTZ,
    sent_by       TEXT,                       -- intern who owns this touch
    notes         TEXT
);
CREATE INDEX idx_outreach_contact ON outreach(contact_id);

-- ---------------------------------------------------------------------------
-- Funnel movement: one row each time a lead enters a stage.
-- Powers stage-by-stage conversion in the dashboard (Week-4 deliverable).
-- ---------------------------------------------------------------------------
CREATE TABLE pipeline_events (
    event_id     BIGSERIAL PRIMARY KEY,
    company_id   BIGINT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    service      service_area NOT NULL,
    stage        funnel_stage NOT NULL,
    entered_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    note         TEXT
);
CREATE INDEX idx_pipeline_company ON pipeline_events(company_id);
CREATE INDEX idx_pipeline_stage   ON pipeline_events(stage);

-- ---------------------------------------------------------------------------
-- Convenience view: current furthest stage per company+service
-- ---------------------------------------------------------------------------
CREATE VIEW current_pipeline AS
SELECT DISTINCT ON (company_id, service)
       company_id, service, stage, entered_at
FROM   pipeline_events
ORDER  BY company_id, service, entered_at DESC;
