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
| `build_turkey.py` | Parses the archived report PDFs in `raw/` into `turkey-law5651.json`. `--download` refreshes the PDFs from transparency.meta.com first. |

## Coverage

**Meta — Facebook & Instagram**, five half-years **H1 2023 → H1 2025**. Meta's
Türkiye reports are the static English PDFs served from
`transparency.meta.com/sr/<slug>` — the Transparency Center index is a
JavaScript app, but each report PDF is a stable URL (see `SLUGS` in the script).
The earliest reports (H1 2023) covered only the individual-applications stream;
the authority stream was added from the H2 2023 reports on.

Other designated providers (**TikTok**, **X**, **YouTube**) publish their own
Law 5651 reports and slot in as further parsers once a stable machine-readable
source is confirmed — TikTok's and X's are currently only inside their
JavaScript transparency centres.

## Output schema

Tidy-long, one row per measured value:

`[platform, period, section, metric, unit, value]`

- **platform** — the reporting service (`Facebook` / `Instagram`).
- **period** — the reporting half-year (`2024 H2`), parsed from the report's own
  stated coverage window.
- **section** — `individual_requests` (Art. 9/9-A) or `authority_requests`
  (Art. 8/8-A).
- **metric** — e.g. `applications_received`, `requests_total`, `requests_icta`,
  `requests_consumer_policy`, `requests_court_orders`, `reported_entities`,
  `entities_removed`, `entities_restricted`.
- **unit** — `count`.

### Caveats

- **Never sum a total with its parts.** `requests_icta` / `requests_consumer_policy`
  / `requests_court_orders` are components of `requests_total`; `reported_entities`
  is reported separately in each section. Pin a `section` **and** a `metric`
  before aggregating.
- **Parts may not sum to the total.** In some periods Meta does not categorise
  every authority request, so the three named authority buckets sum to less than
  `requests_total` (e.g. FB/IG 2024 H1: 2,336 named vs 2,953 total). Faithful to
  the source.
- **Authority counts can bundle Facebook + Instagram.** Meta notes that requests
  from authorities "in some instances contain both Facebook and Instagram content
  together", so the same aggregate can appear on both platforms' reports.
- The parser anchors on each report's table labels / prose sentences and **fails
  loud** on drift; values are exact integers as filed.

## Reproduce

```bash
python3 build_turkey.py --download   # refresh raw/ PDFs from transparency.meta.com
python3 build_turkey.py              # rebuild turkey-law5651.json from raw/
```

Deterministic from `raw/` (rows sorted; no wall-clock).

The API seeds `turkey-law5651.json` into the queryable `turkey_metrics` table
(behind `POST /api/explore` / `/api/query`) and the `/turkey` dataset page.
