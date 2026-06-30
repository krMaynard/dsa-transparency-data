# Apple Transparency Report

Apple's [Transparency Report](https://www.apple.com/legal/transparency/) — government
and private-party requests for device/account/financial/push-token data, emergency
and preservation requests, digital-content-provider requests, US national-security
and UK IPA-warrant requests, and App Store takedown requests — biannually since
**2013 H1**.

Apple publishes the underlying data as a single zip of per-request-type CSVs (keyed
by `TR Period` × `Country/Region`). Unlike the DSA harmonised template, each request
type carries its own column set, so the extractor normalises them onto one canonical
measure vocabulary.

## Layout

| Path | What |
|------|------|
| `raw/Apple_Transparency_Report.zip` | The original report zip, exactly as downloaded from Apple. |
| `build_apple.py` | Extractor — reads the zip and emits the interned `apple-transparency.json`. Pure stdlib. |
| `apple-transparency.json` | The interned dataset the API is seeded from (vendored into `transparency-report-api/data/`). |

## Reproduce

```bash
python3 build_apple.py                 # rebuild apple-transparency.json from raw/
python3 build_apple.py --download      # fetch a fresh zip from Apple first, then rebuild
```

The build is deterministic from the archived zip (the `coverage` stamp is the latest
period in the data, not a wall-clock time), so re-running without `--download`
produces a byte-identical JSON — CI re-derives it and fails on drift.

## Schema notes

- **One row per `(period, country, request_type)`** in `rows`, with a wide-sparse set
  of canonical measures (`requests_received`, `items_specified`,
  `requests_data_provided`, `pct_data_provided`, plus type-specific columns like
  `apps_removed` / `appeals_received` / `accounts_deleted`). Measures not reported for
  a given request type are `null`.
- **National-security / IPA rows are banded ranges** (e.g. `0 - 249`), not integers, so
  they live in a separate `ns_rows` list with parsed `low`/`high` bounds for the
  request and account counts.
- `pct_data_provided` is a percentage — average it, never sum it.
