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

## Status: browser-fetched and archived

`www.esafety.gov.au` resets or hangs plain datacenter-IP requests, but the three
primary pages were recovered through a real Chrome session on 8 August 2026 and
saved under [`raw/`](raw/). `build_esafety.py` now emits the 22 audited numeric
facts from the findings page: 10 user-report counts, four staffing figures, and
eight survey percentages. Qualitative assessments remain in the source archive
and are not coerced into numeric values.

## Output: `au-esafety-ai-companion.json` (tidy-long)

`build_esafety.py` emits the standard
envelope (`{source, coverage, columns, rows}`) with columns:

```
provider, period, section, category, metric, unit, value
```

`section`s:

- **`reports`:** confirmed global user reports by provider and harm category.
- **`staff`:** staff responsible for trust and safety at 30 September 2025.
- **`survey`:** eSafety's 2026 child-survey prevalence figures.

Metric names are the report's own and are **not** comparable across providers or
sections — pin `provider`, `section` **and** `metric` before any aggregation, and
never mix `percent` / `count` / `bool` units.

## Published qualitative context

These source statements are retained as context and are not converted to numeric
rows:

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

## API side

The API already carries the same 22 AI-companion numeric rows alongside eSafety's
CSEA periodic-report stream in `data/esafety-bose.json`.
