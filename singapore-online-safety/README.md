# Singapore — IMDA Online Safety Reports

Singapore's **Code of Practice for Online Safety** (issued by the Infocomm Media
Development Authority, **IMDA**, under the Broadcasting Act 1994 s.45, effective
July 2023) designates six **Designated Social Media Services (DSMSs)** —
**Facebook, Instagram, TikTok, X, YouTube and HardwareZone** — which must each
file an **annual online safety report** on the measures they take against harmful
content (especially to minors). IMDA in turn publishes its own **Online Safety
Assessment Report (OSAR)** benchmarking the six services.

Landing page: <https://www.imda.gov.sg/regulations-and-licensing-listing/content-standards-and-classification/standards-and-classification/internet/online-safety>

## What's built

`build_singapore.py` produces the tidy-long `singapore-online-safety.json`
(`columns` = `service, period, section, category, metric, unit, value`) from the
PDFs archived verbatim in `raw/`. Two streams (`section`):

### 1. `assessment` — IMDA's OSAR cross-service benchmark

The normalised, directly comparable figures. From IMDA's **"Mystery Shopper"**
tests, per service, for both assessment rounds:

- **`action_rate`** (`percent`) — share of legitimate user reports (content that
  violated the service's own community guidelines) that the service acted on.
- **`time_to_action`** (`days`) — average turnaround to resolve a user report.

`period` is the coverage window: `2023-08..2024-07` (OSAR 2024, the first report)
and `2024-04..2025-03` (OSAR 2025). These live as **charts** in the OSAR PDFs, so
the values are transcribed from the published tables (OSAR 2025 → *"Areas where
DSMSs have Improved"* → Table 1 *Action Rate* and Table 2 *Time to Action*) rather
than text-scraped. Verified against the rendered pages.

| Service | Action rate 2024→2025 | Time to action 2024→2025 |
|---|---|---|
| Facebook | 53% → 81% | 9d → 4d |
| Instagram | 2% → 54% | 7d → 4d |
| TikTok | 39% → **25%** (only decline) | 5d → 4d |
| X | 54% → 74% | 10d → 5d |
| YouTube | 46% → 68% | 5d → 4d |
| HardwareZone | 89% → 93% | 3d → 2d |

### 2. `platform_report` — each DSMS's own Singapore figures

Singapore-specific statistics from the six services' year-2 reports (period
**1 Apr 2024 – 31 Mar 2025**). These are **heterogeneous per vendor**, so metric
names are kept per-service and are **not comparable across services**:

- **Meta (Facebook / Instagram)** — per Community Standards category: content
  *created in Singapore* that was actioned (`content_actioned_sg`, count) and the
  Singapore proactive-detection rate (`proactive_rate_sg`, percent). Parsed from
  the report text layer.
- **YouTube** — by YouTube's own reason categories: end-user flags from a
  Singapore IP (`flags_received_sg`) and videos removed that were uploaded from a
  Singapore IP (`videos_removed_sg`). From Tables 1.1 and 1.2.
- **TikTok** — a few headline Singapore figures (videos removed / removed
  proactively, reports found violative, under-13 accounts removed).
- **X** — only its single clearly-scoped Singapore figure (median time to
  action, 69h) is captured. X's report otherwise gives per-*policy* counts
  ("Accessible by" / "Originated from Singapore") that repeat across content
  categories and are footnoted as covering more than one, so they can't be
  cleanly attributed or summed — left as prose.
- **HardwareZone** — reports essentially **no** Singapore statistics (IMDA
  flagged it for not yet collecting the required data); it appears only in the
  `assessment` stream.

## Caveats

- **Pin `service`, `section` and `metric` before aggregating**, and never sum
  across the `count` / `percent` / `days` / `hours` unit mix. `assessment` and
  `platform_report` are different grains; the per-service harm categories are
  each vendor's own taxonomy, not a shared one.
- Only **one** period of per-service data is machine-available (2024-04..2025-03);
  year-1 per-service PDFs were not published separately. The next tranche is due
  30 Jun 2026.

## Refresh

```bash
python build_singapore.py     # re-parses raw/*.pdf → singapore-online-safety.json
```

The eight source PDFs (OSAR 2024, OSAR 2025, and the six 2025 service reports)
are archived in `raw/`. IMDA's server returns 403 to some fetchers; download with
a browser `User-Agent` (`curl -A "Mozilla/5.0 …"`).
