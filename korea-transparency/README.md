# South Korea — Naver & Kakao transparency reports (government data requests)

South Korea's network laws — the **Telecommunications Business Act
(전기통신사업법)** and the **Protection of Communications Secrets Act
(통신비밀보호법)** — let investigative agencies request user data from platform
operators. **Naver** and **Kakao** each publish a half-yearly transparency
report covering the same four legal request types:

| Canonical key | Korean | What it is |
|---|---|---|
| `comm_user_information` | 통신자료 | Subscriber identity data (voluntary; **both platforms stopped providing it in 2012**, so later periods report zero/none — agencies moved to warrants instead) |
| `comm_confirmation_data` | 통신사실확인자료 | Communications metadata (court permission) |
| `comm_restriction` | 통신제한조치 | Communication-restricting measures / interception (court permission) |
| `seizure_warrant` | 압수수색영장 | Search & seizure warrants |

Neither company publishes a bulk history file, but both report pages are thin
JS front ends over **public JSON endpoints**, which is what the extractor
scrapes — no browser needed:

- **Kakao** — `privacy.kakao.com/api/transparency/{year}/{half}` (one payload
  per half-year; rows per service corp **다음/Daum, 카카오/Kakao** × request
  type, with requests / processed / accounts counts).
- **Naver** — `privacy.naver.com/api/pages/TRANSPARENCY_REPORT_STATISTICS`
  (a CMS payload whose `specificAreaJson.statistics` array holds **every**
  period, with per-type counts plus a compliance rate and an
  accounts-per-processed-request average).

## Layout

| Path | What |
|------|------|
| `raw/kakao-<year>-h<n>.json` | Archived Kakao API payloads (one per half-year, 2012–2025). |
| `raw/naver-statistics.json` | Archived Naver CMS payload (all periods in one). |
| `build_korea.py` | Pure-stdlib extractor → `korea-transparency.json`. `--download` refreshes `raw/` from the live endpoints. |
| `korea-transparency.json` | The dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_korea.py              # rebuild korea-transparency.json from raw/
python3 build_korea.py --download   # refresh raw/ from the live endpoints first
```

Deterministic from the archived `raw/` files (rows sorted; `coverage` = latest
period; no wall-clock), so re-running is byte-identical — CI re-derives it and
fails on drift.

## Schema (tidy long)

`[platform, service, period, category, metric, unit, value]`

- **platform** — `Naver` / `Kakao` (the reporting company).
- **service** — Kakao splits its figures by service corp (`Daum` / `Kakao`);
  Naver reports company-wide (empty string).
- **period** — `YYYY-H1` / `YYYY-H2` (half-year).
- **category** — one of the four canonical request types above.
- **metric** — `requests` (received), `processed` (complied with), `accounts`
  (accounts/items provided), plus Naver-only `processed_rate` and
  `accounts_per_processed`.
- **unit** — `count` (exact), `percent` (compliance rates), or `average`
  (accounts per processed request). **Never sum non-count units**, and pin a
  `metric` before aggregating (requests ≠ accounts).

A `'-'` in the source (not reported / not applicable) is skipped; a true `0`
(e.g. zero 통신자료 provided after 2012) is kept — absence and zero mean
different things.

## Coverage & verification

**2012-H1 → 2025-H2** (28 half-years) for both platforms; 1,152 rows. Spot
values were verified against press coverage of the reports (e.g. Naver 2024-H1
seizure-warrant items provided = 104,537 and confirmation-data items = 1,545,
both exact matches). Naver's internal arithmetic (rate = processed/requests,
average = accounts/processed) reproduces from the raw counts.
