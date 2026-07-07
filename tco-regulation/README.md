# EU Terrorist Content Online Regulation (TCOR) — transparency reports

Regulation **(EU) 2021/784** ("TCOR", in application since **7 June 2022**)
creates two annual transparency-reporting duties around *terrorist content*
(content that incites, solicits, instructs on, or threatens terrorist offences):

- **Article 7** — every **hosting service provider** that took action against
  terrorist content in a calendar year must publish a transparency report before
  1 March of the following year: measures to identify/remove content, the number
  of items removed and reinstated, removal orders received & actioned, complaints
  handled under Art. 10, and administrative/judicial review proceedings.
- **Article 8** — every Member State's **competent authority** publishes an
  annual report on its activity (removal orders issued, Art. 5(4) exposure
  decisions, reviews, penalties). The **European Commission** additionally
  reports on the Regulation's implementation, aggregating the per-Member-State
  removal-order counts.

## What's built

`build_tco.py` → `tco-regulation.json`, tidy-long
(`publisher, role, period, section, category, metric, unit, value`), from the
reports archived in `raw/`. Two streams (`role`):

- **`authority`** — the Art. 8 / Commission side:
  - **European Commission** implementation report (COM(2024) 64 final, 14 Feb
    2024): per-Member-State **removal orders issued** for 7 Jun 2022 – 31 Dec
    2023. Six of the 23 Member States with designated authorities issued orders:

    | Member State | Removal orders issued |
    |---|--:|
    | Germany | 249 |
    | Spain | 62 |
    | France | 26 |
    | Austria | 8 |
    | **Romania** (ANCOM) | **2** |
    | Czechia | 2 |
    | **EU total** | **349** |

  - **Ireland — Coimisiún na Meán**, Art. 8 report 2024: as Ireland's Art.
    12(1)(c)/(d) authority it reports Art. 5(4) exposure decisions (3 HSPs:
    Meta/Facebook+Instagram, TikTok, X), 0 reviews, 0 penalties.

- **`platform`** — the Art. 7 side, each publisher's enforcement figures by the
  report's own breakdown:
  - **Spotify** (2024), per sub-service (Spotify, Spotify for Creators, Spotify
    for Artists, Findaway Voices): content removed proactively for terrorism/
    violent extremism, content removed via EU removal orders, appeals, reviews,
    reversals.
  - **Meta / Facebook** (2023): 143 order requests received via its dedicated
    channel, of which **15 were valid** Competent-Authority orders and **10** led
    to removal/restriction; 6.1M proactive removals (a broader policy scope —
    Dangerous Organizations, Violence & Incitement, Coordinating Harm — that
    overlaps Meta's CSER, hence `approx_count`), 857.2k appeals, 156k reinstated,
    0 Art. 10 complaints, 0 reviews.
  - **Google** (whole-Google, **2022–2025**, from the public GCS bucket
    `storage.googleapis.com/transparencyreport/report-downloads/pdf-report-26_*`):
    removal orders received (0 / 0 / 3 / 12-items), and exact proactive removals
    of terrorist/extremist content that grew 1.4M → 16.3M → 55.3M → **181.3M**,
    plus complaints handled (appeals) and decisions overturned. Google reports
    exact counts (not banded), so `unit=count`.

### Method & caveats

- The reported figures are **sparse and scattered** across heterogeneous prose
  PDFs (each vendor's transparency centre, each authority's own site, EUR-Lex).
  Rather than fragile prose-parsing, the figures are **transcribed** into
  `SOURCES` and each source is **verified** with fail-loud anchor checks (a
  distinctive phrase/number that must still appear in the archived PDF) — the
  same contract as `japan-info-platform/build_japan_narratives.py`. If a vendored
  report drifts, the build raises.
- Metric **scope is each report's own** and not strictly comparable across
  publishers — Spotify's `content_removed_proactive` is terrorism-only, Meta's
  covers three broader policy areas. `unit` is `count` (exact) or `approx_count`
  (Meta's rounded millions/thousands). Pin `publisher` before aggregating.
- **Coverage is a starting set.** More Art. 7 platforms (X, TikTok, Google,
  Microsoft, LinkedIn, …) and more national Art. 8 authorities slot in as their
  reports are archived under `raw/`.

## Refresh

```bash
python build_tco.py     # re-reads raw/*.pdf → tco-regulation.json
```

Sources: TCOR text — <https://eur-lex.europa.eu/eli/reg/2021/784/oj> ·
Commission implementation report COM(2024) 64 —
<https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52024DC0064>.
