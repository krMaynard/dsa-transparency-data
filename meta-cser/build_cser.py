#!/usr/bin/env python3
"""Build meta-cser.json from Meta's Community Standards Enforcement Report.

The **Community Standards Enforcement Report (CSER)** is Meta's flagship
*voluntary* transparency report — how much violating content it actioned on
**Facebook** and **Instagram** across ~16 policy areas, quarterly since
2017 Q4. It is not filed under any single law (unlike the EU-DSA or Türkiye
Law 5651 reports); Meta publishes it of its own accord, now under the umbrella
"Integrity Reports". Five headline metric families:

- **Prevalence** — how often violating content is *seen* (a rate, reported as a
  lower/upper bound, or an "approximately N%" estimate in the oldest quarters).
- **Content actioned / removed** — how many pieces Meta took action on.
- **Proactive rate** — the share found by Meta before a user reported it.
- **Appealed / restored** — content people appealed, and that Meta put back
  (with or without an appeal).
- **Enforcement precision / false positives** — accuracy bounds (sparse).

## Source

The CSER has no static CSV/ZIP download; its charts are drawn client-side from a
same-origin **GraphQL** feed. One persisted query,
``TransparencyReportCSERRootCSVQuery``, returns the *entire* dataset as a single
CSV (``app,policy_area,metric,period,value``) — every chart's series at once.
``_download`` replays it deterministically with two requests and no login:

1. GET a CSER page with browser headers; scrape the ``lsd`` token from the HTML.
2. POST the persisted query to ``/api/graphql/`` with that token; the response's
   ``data.csv.content`` field is the CSV.

The persisted-query ``doc_id`` rotates when Meta redeploys the site; if a refresh
returns no CSV, re-derive it by grepping the page's JS bundles for the
``TransparencyReportCSERRootCSVQuery`` operation id (see ``_DOC_ID`` below). The
archived ``raw/cser.csv`` makes the *build* fully deterministic regardless.

## Output

Tidy-long, one row per measured value:

  app, policy_area, metric, period, unit, value

``unit`` is ``count`` or ``percent`` (derived per row: a ``%`` value — including
the lone "approximately N%" — is a percent, everything else a count).
``N/A`` cells (a metric not reported for that policy × quarter) are dropped.
``value`` is a number. Rows sorted; no wall-clock. Pure stdlib.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_CSV = os.path.join(HERE, "raw", "cser.csv")
OUT_JSON = os.path.join(HERE, "meta-cser.json")

SOURCE = "https://transparency.meta.com/reports/community-standards-enforcement/"
COLUMNS = ["app", "policy_area", "metric", "period", "unit", "value"]

# The persisted GraphQL query that returns the whole CSER as one CSV, and a page
# to scrape the per-session `lsd` token from. doc_id rotates on redeploys.
_GRAPHQL = "https://transparency.meta.com/api/graphql/"
_LSD_PAGE = (SOURCE + "hateful-conduct/facebook/")
_DOC_ID = "31742207542036840"
_FRIENDLY = "TransparencyReportCSERRootCSVQuery"
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def _period(p: str) -> str:
    """`2017Q4` -> `2017 Q4` (faithful, just spaced for readability)."""
    m = re.fullmatch(r"(\d{4})(Q[1-4])", p.strip())
    if not m:
        raise ValueError(f"unexpected period {p!r}")
    return f"{m.group(1)} {m.group(2)}"


def _value(raw: str) -> tuple[str, float] | None:
    """Parse a CSER value cell into (unit, number), or None for an N/A cell.

    Counts come as `20,800,000` or `17600000`; rates as `94.40%`; the oldest
    Prevalence estimates as `approximately 4%`. Fail loud on anything else so a
    format shift can't slip through as a silent drop."""
    v = raw.strip()
    if v == "" or v.upper() == "N/A":
        return None
    m = re.fullmatch(r"(?:approximately\s+)?(\d+(?:\.\d+)?)%", v, re.I)
    if m:
        return "percent", float(m.group(1))
    if re.fullmatch(r"[\d,]+", v):
        return "count", float(v.replace(",", ""))
    raise ValueError(f"unparseable CSER value {raw!r}")


def build(raw_csv: str) -> dict:
    with open(raw_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != ["app", "policy_area", "metric", "period", "value"]:
            raise ValueError(f"unexpected CSER CSV header {header}")
        rows: list[list] = []
        for app, policy_area, metric, period, value in reader:
            parsed = _value(value)
            if parsed is None:
                continue
            unit, num = parsed
            rows.append([app, policy_area, metric, _period(period), unit, num])
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    periods = sorted({r[3] for r in rows})
    return {
        "source": SOURCE,
        "coverage": (f"{periods[0]}..{periods[-1]}" if len(periods) > 1
                     else periods[0] if periods else ""),
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_csv: str) -> None:
    """Refresh raw/cser.csv from Meta's GraphQL feed (see module docstring)."""
    import urllib.parse
    import urllib.request

    def _get(url: str, headers: dict) -> tuple[bytes, str]:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            cookie = resp.headers.get("set-cookie", "")
            return resp.read(), cookie

    # 1. scrape the lsd token (browser headers required or Meta returns a shell).
    page_headers = {
        "User-Agent": _UA,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "document", "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none", "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }
    html, set_cookie = _get(_LSD_PAGE, page_headers)
    m = re.search(rb'"LSD",\[\],\{"token":"([^"]+)"', html)
    if not m:
        raise RuntimeError("could not scrape the lsd token from the CSER page")
    lsd = m.group(1).decode()
    cookie = "; ".join(c.split(";", 1)[0] for c in set_cookie.split(", ") if "=" in c)

    # 2. POST the persisted query; data.csv.content is the whole CSV.
    body = urllib.parse.urlencode({
        "lsd": lsd,
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": _FRIENDLY,
        "variables": "{}",
        "doc_id": _DOC_ID,
    }).encode()
    req = urllib.request.Request(_GRAPHQL, data=body, headers={
        "User-Agent": _UA,
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://transparency.meta.com",
        "referer": _LSD_PAGE,
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-fb-lsd": lsd, "x-fb-friendly-name": _FRIENDLY,
        "cookie": cookie,
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.load(resp)
    csv_field = (payload.get("data") or {}).get("csv") or {}
    content = csv_field.get("content")
    if not content:
        raise RuntimeError(
            "GraphQL returned no csv.content — the doc_id may have rotated; "
            "re-derive it from the page's JS bundles (see module docstring)")
    os.makedirs(os.path.dirname(raw_csv), exist_ok=True)
    with open(raw_csv, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    n = len(list(csv.reader(io.StringIO(content)))) - 1
    print(f"downloaded {csv_field.get('filename', 'cser.csv')} -> {raw_csv} "
          f"({n} rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raw", default=RAW_CSV, help="Archived CSER CSV path")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh the raw CSV from Meta's GraphQL feed first")
    args = ap.parse_args()

    if args.download:
        _download(args.raw)

    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    rows = data["rows"]
    print(f"wrote {args.out}: {len(rows)} values across "
          f"{len({r[0] for r in rows})} apps, "
          f"{len({r[1] for r in rows})} policy areas, "
          f"{len({r[3] for r in rows})} quarters (coverage {data['coverage']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
