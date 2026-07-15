# Australia — eSafety Basic Online Safety Expectations (BOSE) transparency notices

Australia's **eSafety Commissioner** issues legally-enforceable **transparency
notices** under the **Basic Online Safety Expectations (BOSE)** determination
(made under the *Online Safety Act 2021*, Part 4). A notice requires an online
service provider to report on how it is meeting any or all of the Expectations;
eSafety then publishes a **findings report** summarising the responses. Notices
are *periodic* (recurring reports) or *non-periodic* (one-off), and non-compliance
is backed by civil penalties.

Landing page: <https://www.esafety.gov.au/industry/basic-online-safety-expectations/responses-to-transparency-notices>

## Scope of this dataset: AI companion apps (non-periodic, October 2025)

The first slice built here is eSafety's **findings from the non-periodic
transparency notices on AI companion apps**. eSafety gave notices on
**16 October 2025** to the four AI companion service providers most used by
children in Australia, and published its findings report in **March 2026** (the
survey figures on the page were revised in **July 2026** after a weighting
adjustment to the child-survey data).

**Providers noticed (4):**

| Provider (display) | Legal entity | Service |
|---|---|---|
| Character.AI | Character Technologies, Inc. | character.ai |
| Nomi | Glimpse.AI, Inc. (Glimpse AI) | Nomi |
| Chai | Chai Research Corp. | Chai |
| Chub AI | Chub.AI, Inc. | Chub AI |

**Primary sources**

- Findings report page — *Findings from transparency notices on AI companion
  apps: October 2025 (non-periodic)*:
  <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services/findings-october-2025>
- AI-services hub — *Responses to transparency notices: Artificial intelligence
  services*:
  <https://www.esafety.gov.au/industry/basic-online-safety-expectations/ai-services>
- Media release — *eSafety report shows AI companions are putting children at
  risk*:
  <https://www.esafety.gov.au/newsroom/media-releases/esafety-report-shows-ai-companions-are-putting-children-at-risk>
- Notice announcement — *eSafety requires providers of AI companion chatbots to
  explain how they are keeping Aussie kids safe*:
  <https://www.esafety.gov.au/newsroom/media-releases/esafety-requires-providers-of-ai-companion-chatbots-to-explain-how-they-are-keeping-aussie-kids-safe>

## ⚠️ Status: source not yet fetched (browser-gated)

`www.esafety.gov.au` sits behind a WAF that **resets/hangs every request from a
datacenter IP** (verified: HTTP/2 stream reset, HTTP/1.1 hang, static PDFs
included; `web.archive.org` is also egress-blocked from the build sandbox). This
is the "needs a residential IP + real browser" case documented in the repo's
[`BROWSER-FETCH-RUNBOOK.md`](../BROWSER-FETCH-RUNBOOK.md). The source has been
added to [`SOURCES-NEEDING-BROWSER.md`](../SOURCES-NEEDING-BROWSER.md) **Section
E**.

**Therefore no data rows are committed yet, and none are fabricated.** The
report is largely a *qualitative* per-provider compliance assessment with a small
number of survey statistics, so the exact per-provider Yes/No cells and the
survey percentages must be read from the published report itself — not from press
coverage — before they go in. See [`raw/FETCH.md`](raw/FETCH.md) for the exact
retry-from-residential-box steps.

## Intended output — `au-esafety-ai-companion.json` (tidy-long)

Once `raw/` holds the fetched report, `build_esafety.py` emits the standard
envelope (`{source, coverage, columns, rows}`) with columns:

```
provider, period, section, category, metric, unit, value
```

Planned `section`s (final taxonomy to be confirmed against the report):

- **`survey`** — eSafety's 2026 child-survey figures (`provider='All'`): share of
  children who have used an AI companion / an AI companion-or-assistant
  (`unit='percent'`), and the derived estimated number of children
  (`unit='count'`). `period` = the survey window.
- **`compliance`** — the per-provider assessment against each BOSE expectation
  checked in the report (e.g. age assurance, self-harm/crisis-support referral,
  protections against explicit material, reporting/complaint mechanisms).
  Encoded as booleans (`unit='bool'`, `value` 0/1) where the report states a
  clear Yes/No, keeping each expectation as its own `metric`. `period` = the
  notice/response window.
- **`provider_action`** — material remediation each provider took after the
  notice (e.g. age-assurance changes, geo-blocking Australia, paywalling),
  captured as flags where the report states them.

Metric names are the report's own and are **not** comparable across providers or
sections — pin `provider`, `section` **and** `metric` before any aggregation, and
never mix `percent` / `count` / `bool` units.

## Known published facts (context only — verify against the report before ingesting)

These are drawn from eSafety's media release and reputable coverage, recorded
here as *context to guide extraction*, **not** as committed dataset values:

- eSafety's 2026 survey (~1,950 children aged 10–17): **79%** had used an AI
  companion *or* AI assistant; **8%** had used an AI companion (~**200,000**
  Australian children). (A separate figure was revised 1%→2% in July 2026.)
- **None** of the four providers had robust age-verification measures (relied on
  app-store ratings / self-declaration at signup).
- **Chai, Chub AI and Nomi** did not direct users to mental-health / crisis
  support when self-harm was detected in prompts.
- Post-notice actions: Character.AI added age assurance for Australian users and
  removed chat for under-18s; Chub AI geo-blocked/withdrew from Australia; Chai
  moved AI-companion chat behind a paid subscription; Nomi committed to further
  age-assurance functionality.

## API side (deferred until data exists)

When rows are produced, wire it into `transparency-report-api` the same way the
Singapore online-safety dataset is (vendored JSON snapshot → `build_*_db` in
`seed.py` → a `TableSpec` in `main.py` → a `/au-esafety` static page, English-only
like `/singapore`). Not done here because seeding an empty table would ship
untested code — it belongs in the same change that lands the real rows.
