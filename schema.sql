-- Relational schema for the DSA transparency-report locations database.
-- Built by build_reports_db.py from REPORT_LOCATIONS.md into dsa_reports.db.
--
-- Model: a platform belongs to one company and one category, has one
-- confidence rating, and one or more report URLs (hub page + direct file, etc.).

PRAGMA foreign_keys = ON;

CREATE TABLE category (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE company (
    company_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);

CREATE TABLE platform (
    platform_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    company_id      INTEGER NOT NULL REFERENCES company(company_id),
    category_id     INTEGER NOT NULL REFERENCES category(category_id),
    format_period   TEXT,                       -- e.g. "PDF; CY2024"
    confidence      TEXT NOT NULL CHECK (confidence IN ('verified','likely','uncertain')),
    confidence_note TEXT,                        -- parenthetical caveat, if any
    -- Uses the EU harmonised machine-readable template (Reg. (EU) 2024/2835,
    -- Annex I)? 'partial' = latest report only / unverified file.
    harmonised_template TEXT NOT NULL DEFAULT 'unknown'
        CHECK (harmonised_template IN ('yes','no','partial','unknown')),
    UNIQUE (name, category_id)
);

CREATE TABLE report_url (
    url_id      INTEGER PRIMARY KEY,
    platform_id INTEGER NOT NULL REFERENCES platform(platform_id),
    label       TEXT,                            -- e.g. "Hub", "PDF", "2025 XLSX"
    url         TEXT NOT NULL
);

CREATE INDEX idx_platform_company  ON platform(company_id);
CREATE INDEX idx_platform_category ON platform(category_id);
CREATE INDEX idx_report_platform   ON report_url(platform_id);

-- Flat, alphabetical join of everything (one row per report URL).
CREATE VIEW v_reports AS
SELECT p.name        AS platform,
       co.name       AS company,
       ca.name       AS category,
       p.confidence  AS confidence,
       p.harmonised_template,
       p.format_period,
       ru.label      AS url_label,
       ru.url        AS url
FROM   platform p
JOIN   company  co ON co.company_id = p.company_id
JOIN   category ca ON ca.category_id = p.category_id
LEFT JOIN report_url ru ON ru.platform_id = p.platform_id
ORDER BY p.name COLLATE NOCASE, ru.url_id;
