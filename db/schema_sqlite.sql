-- SQLite schema for the living lead-gen DB (runnable version of schema.sql).
-- Postgres schema.sql stays as the target design; this is what build_db.py runs.
-- Idempotent: drops and recreates everything.

DROP VIEW  IF EXISTS v_top_leads;
DROP VIEW  IF EXISTS v_lead_furthest;
DROP TABLE IF EXISTS pipeline_events;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS lead_scores;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS stages;

-- Companies = the living prospect DB (from enrich.py → companies_db.csv)
CREATE TABLE companies (
    company_name             TEXT PRIMARY KEY,      -- natural key (we dedupe by name)
    industry                 TEXT,
    locations                TEXT,
    hiring_count             INTEGER,
    sample_titles            TEXT,
    tech_stack               TEXT,
    fit_it_servicing         REAL,
    fit_manpower             REAL,
    fit_ai_implementation    REAL,
    fit_systems_integration  REAL,
    best_service             TEXT,
    source                   TEXT,
    source_url               TEXT,
    first_seen               TEXT,
    last_seen                TEXT
);

-- Overall lead scores (from score_leads.py → scored_leads.csv)
CREATE TABLE lead_scores (
    company_name   TEXT REFERENCES companies(company_name),
    fit_score      REAL,
    firmographic   REAL,
    intent         REAL,
    reachability   REAL,
    overall        REAL
);

-- Decision-maker contacts (from contacts_worksheet.csv, filled rows)
CREATE TABLE contacts (
    company_name      TEXT REFERENCES companies(company_name),
    full_name         TEXT,
    title             TEXT,
    email             TEXT,
    linkedin_url      TEXT,
    is_decision_maker TEXT,
    status            TEXT,
    notes             TEXT
);

-- Funnel movement (from log_event.py → pipeline_events.csv)
CREATE TABLE pipeline_events (
    company_name  TEXT REFERENCES companies(company_name),
    service       TEXT,
    stage         TEXT REFERENCES stages(stage),
    entered_at    TEXT,
    note          TEXT
);

-- Reference table: the 8 funnel stages and their order (playbook §6.1)
CREATE TABLE stages (
    stage  TEXT PRIMARY KEY,
    ord    INTEGER
);
INSERT INTO stages (stage, ord) VALUES
    ('target_identified', 0),
    ('contact_identified', 1),
    ('outreach_sent', 2),
    ('reply_received', 3),
    ('call_booked', 4),
    ('call_held', 5),
    ('concrete_interest', 6),
    ('korea_visit_ready', 7);

-- Furthest stage reached per company+service
CREATE VIEW v_lead_furthest AS
SELECT pe.company_name, pe.service, MAX(s.ord) AS furthest_ord
FROM   pipeline_events pe
JOIN   stages s ON s.stage = pe.stage
GROUP  BY pe.company_name, pe.service;

-- Ranked leads with their score and best-fit service
CREATE VIEW v_top_leads AS
SELECT c.company_name, c.best_service, c.industry, c.tech_stack,
       c.hiring_count, ls.fit_score, ls.reachability
FROM   companies c
LEFT   JOIN lead_scores ls ON ls.company_name = c.company_name
ORDER  BY ls.fit_score DESC;
