# Türkiye — Law No. 5651 platform transparency reports

Türkiye's **Law No. 5651** (Regulation of Broadcasts via Internet and Prevention
of Crimes Committed through Such Broadcasts), as amended in 2020/2022, requires
social-network providers with **more than one million daily accesses from
Türkiye** to publish a **six-monthly transparency report** (Additional Article 4)
on the content-removal and access-blocking decisions notified to them. Two
request streams are reported:

- **Individual applications (Art. 9 / 9-A)** — natural or legal persons in
  Türkiye ask the platform, via a dedicated reporting form, to remove content
  that violates their personality or privacy rights.
- **Judicial & administrative authorities (Art. 8 / 8-A)** — removal requests
  from the **ICTA** (Bilgi Teknolojileri ve İletişim Kurumu), the **Consumer
  Policy** channel (Pharmaceuticals & Medical Devices Administration, Board of
  Advertisement, Directorate General of Domestic Trade), and **court orders**
  received through the Internet Access Providers Union.

## Pipeline

| Script | What |
|--------|------|
| `build_turkey.py` | Parses the archived report PDFs in `raw/` into `turkey-law5651.json`. `--download` refreshes the PDFs from the publishers first. |

## Coverage

**Meta — Facebook & Instagram**, five half-years **H1 2023 → H1 2025**. Meta's
Türkiye reports are the static English PDFs served from
`transparency.meta.com/sr/<slug>` — the Transparency Center index is a
JavaScript app, but each report PDF is a stable URL (see `META_SLUGS` in the
script). The earliest reports (H1 2023) covered only the individual-applications
stream; the authority stream was added from the H2 2023 reports on.

**X / Twitter**, nine half-years **H1 2021 → H1 2025** — the static English
country reports served from `transparency.x.com` (see `X_SLUGS`). X reports only
the **individual** stream (Art. 9/9-A), but broken down by **issue category**
(Abuse, Hateful Conduct, Copyright, …) with a **request volume** and an **action
rate** per category — richer than Meta's report-level totals in that dimension,
but with no authority-request data. X's coverage windows are shifted (older
reports run Dec–May / Jun–Nov), so the reporting half-year is derived from each
report's **end date**.

Other designated providers publish under Law 5651 too, but not in a retrievable
machine-readable form and so are **not** included:

- **TikTok** files no dedicated Türkiye Law 5651 report — its Turkish compliance
  figures appear only inside its **global** Government Removal Requests report
  (carried separately as `tiktok_metrics` in the API).
- **Google / YouTube** publishes no Turkey-specific Law 5651 statistics file;
  Turkish removals appear only in Google's **global** government-removals tool,
  and YouTube isn't isolated within it.

They slot in as further parsers if a stable statutory source appears.

## Output schema

Tidy-long, one row per measured value:

`[platform, period, section, category, metric, unit, value]`

- **platform** — the reporting service (`Facebook` / `Instagram` / `X`).
- **period** — the reporting half-year (`2024 H2`), parsed from the report's own
  stated coverage window.
- **section** — `individual_requests` (Art. 9/9-A) or `authority_requests`
  (Art. 8/8-A).
- **category** — X's per-issue breakdown label (kept verbatim: `Abuse`,
  `Hateful Conduct`, `Copyright`, …). **Blank** for Meta's report-level totals.
- **metric** — Meta: `applications_received`, `requests_total`, `requests_icta`,
  `requests_consumer_policy`, `requests_court_orders`, `reported_entities`,
  `entities_removed`, `entities_restricted`. X: `requests` (volume) and
  `action_rate`.
- **unit** — `count`, or `percent` (X action rates).

### Caveats

- **Never sum a total with its parts, or a percent with anything.**
  `requests_icta` / `requests_consumer_policy` / `requests_court_orders` are
  components of Meta's `requests_total`; `reported_entities` is reported
  separately in each section; X's `action_rate` is a per-category percentage. Pin
  a `section`, a `category` **and** a `metric` before aggregating.
- **Parts may not sum to the total.** In some periods Meta does not categorise
  every authority request, so the three named authority buckets sum to less than
  `requests_total` (e.g. FB/IG 2024 H1: 2,336 named vs 2,953 total). Faithful to
  the source.
- **Authority counts can bundle Facebook + Instagram.** Meta notes that requests
  from authorities "in some instances contain both Facebook and Instagram content
  together", so the same aggregate can appear on both platforms' reports.
- **X and Meta aren't like-for-like.** X reports the individual stream by issue
  category (no authority data, no absolute removal counts); Meta reports both
  streams as report-level totals (no per-issue split). They're the same statutory
  obligation filed in different shapes — compare within a platform.
- Both parsers **fail loud** on template drift (Meta anchors on table labels /
  prose sentences; X reads the report's data table, gathering rows across page
  breaks and validating each issue label against a known set); values are exact
  as filed.

## Reproduce

```bash
python3 build_turkey.py --download   # refresh raw/ PDFs from the publishers
python3 build_turkey.py              # rebuild turkey-law5651.json from raw/
```

Deterministic from `raw/` (rows sorted; no wall-clock).

The API seeds `turkey-law5651.json` into the queryable `turkey_metrics` table
(behind `POST /api/explore` / `/api/query`) and the `/turkey` dataset page.
