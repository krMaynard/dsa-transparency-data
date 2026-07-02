#!/usr/bin/env python3
"""Build korea-transparency.json from Naver's and Kakao's transparency reports.

South Korea's network laws — the Telecommunications Business Act (전기통신사업법)
and the Protection of Communications Secrets Act (통신비밀보호법) — let
investigative agencies request user data from platform operators. Naver and
Kakao each publish a half-yearly **transparency report** with the same four
legal request types:

  * 통신자료      (communications user information — voluntary; both platforms
                   stopped providing it in 2012, so later periods report 0/none)
  * 통신사실확인자료 (communications confirmation data — metadata, court permit)
  * 통신제한조치   (communication-restricting measures — interception, court permit)
  * 압수수색영장   (search & seizure warrants)

Neither publishes a bulk file with history, but both sites are thin JS front
ends over **public JSON endpoints**, which is what this extractor scrapes:

  * Kakao: https://privacy.kakao.com/api/transparency/{year}/{half}
    (one JSON per half-year; rows per service corp 다음/카카오 × request type,
    with requests / processed / accounts counts)
  * Naver: https://privacy.naver.com/api/pages/TRANSPARENCY_REPORT_STATISTICS
    (one CMS JSON whose `specificAreaJson.statistics` holds every period, with
    per-type request/processed/accounts counts plus a compliance rate and an
    accounts-per-processed-request average)

Both feed one **tidy-long** table — one row per measured value:

  platform, service, period, category, metric, unit, value

`unit` is `count` (exact), `percent` (Naver's compliance rates) or `average`
(Naver's accounts-per-processed-request) — never sum non-count units, and pin a
`metric` before aggregating. Coverage: 2012-H1 → 2025-H2 for both platforms.

Deterministic: builds purely from the archived raw/ JSON (rows sorted); no
wall-clock. `--download` refreshes raw/ from the live endpoints. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_JSON = os.path.join(HERE, "korea-transparency.json")

COLUMNS = ["platform", "service", "period", "category", "metric", "unit", "value"]

KAKAO_YEARS = range(2012, 2026)
KAKAO_URL = "https://privacy.kakao.com/api/transparency/{year}/{half}"
NAVER_URL = "https://privacy.naver.com/api/pages/TRANSPARENCY_REPORT_STATISTICS"

# Kakao's English category labels (whitespace-mangled in the API) → canonical keys.
KAKAO_CATEGORIES = {
    "comm. user information": "comm_user_information",
    "comm. restricting measure": "comm_restriction",
    "comm. confirmation data": "comm_confirmation_data",
    "search and seizure warrant": "seizure_warrant",
}
KAKAO_CORPS = {"다음": "Daum", "카카오": "Kakao"}

# Naver's per-type field prefixes → the same canonical keys.
NAVER_CATEGORIES = {
    "commData": "comm_user_information",
    "commRestriction": "comm_restriction",
    "commConfirmationData": "comm_confirmation_data",
    "warrant": "seizure_warrant",
}
# Field suffix → (metric, unit). `ProvideCount` is the number of accounts/items
# provided; `ProcessingCount` is the number of requests complied with.
NAVER_METRICS = {
    "RequestCount": ("requests", "count"),
    "ProcessingCount": ("processed", "count"),
    "ProvideCount": ("accounts", "count"),
    "Rate": ("processed_rate", "percent"),
    "AverageCount": ("accounts_per_processed", "average"),
}


def _num(v) -> int | float | None:
    """Parse an API value: ints pass through; strings may carry commas; '-' and
    blanks mean not-reported (skipped, unlike a true 0 which is kept)."""
    if v is None or isinstance(v, bool):
        return None  # bool is an int subclass — a JSON true/false is not a count
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip().replace(",", "")
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        return None  # '-', '', or narrative text
    f = float(s)
    return int(f) if f.is_integer() else f


def _canon_kakao_category(label: str) -> str:
    key = re.sub(r"\s+", " ", (label or "")).strip().lower()
    if key not in KAKAO_CATEGORIES:
        raise SystemExit(f"unrecognised Kakao category: {label!r}")
    return KAKAO_CATEGORIES[key]


def _parse_kakao(path: str, year: int, half: int) -> list[list]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if not payload.get("success"):
        raise SystemExit(f"{path}: API payload not successful")
    period = f"{year}-H{half}"
    rows: list[list] = []
    # Safe nested access: format drift lands in the zero-rows guard below with a
    # descriptive error instead of a bare KeyError/TypeError.
    for r in (payload.get("data") or {}).get("reports") or []:
        service_corp = r.get("serviceCorp") or ""
        corp = KAKAO_CORPS.get(service_corp, service_corp)
        cat = _canon_kakao_category(r.get("enCategory") or r.get("category") or "")
        for field, metric in (("numberOfRequests", "requests"),
                              ("numberOfProcesses", "processed"),
                              ("numberOfAccounts", "accounts")):
            n = _num(r.get(field))
            if n is not None:
                rows.append(["Kakao", corp, period, cat, metric, "count", n])
    if not rows:
        raise SystemExit(f"{path}: parsed zero rows (format drift?)")
    return rows


def _parse_naver(path: str) -> list[list]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    stats = (payload.get("specificAreaJson") or {}).get("statistics") or []
    rows: list[list] = []
    for rec in stats:
        half = 1 if rec.get("period") == "상반기" else 2
        period = f"{rec['year']}-H{half}"
        for prefix, cat in NAVER_CATEGORIES.items():
            for suffix, (metric, unit) in NAVER_METRICS.items():
                n = _num(rec.get(prefix + suffix))
                if n is not None:
                    rows.append(["Naver", "", period, cat, metric, unit, n])
    if not rows:
        raise SystemExit(f"{path}: parsed zero rows (format drift?)")
    return rows


def build(raw_dir: str) -> dict:
    rows: list[list] = []
    for year in KAKAO_YEARS:
        for half in (1, 2):
            path = os.path.join(raw_dir, f"kakao-{year}-h{half}.json")
            if not os.path.isfile(path):
                raise SystemExit(f"missing expected raw file: {path}")
            rows.extend(_parse_kakao(path, year, half))
    naver_path = os.path.join(raw_dir, "naver-statistics.json")
    if not os.path.isfile(naver_path):
        raise SystemExit(f"missing expected raw file: {naver_path}")
    rows.extend(_parse_naver(naver_path))
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
    return {
        "source": "https://privacy.naver.com/report/report/transparency-statistics"
                   " + https://privacy.kakao.com/transparency",
        "coverage": max(r[2] for r in rows),
        "columns": COLUMNS,
        "rows": rows,
    }


def _download(raw_dir: str) -> None:
    import time
    os.makedirs(raw_dir, exist_ok=True)

    def fetch(url: str, dest: str) -> None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                   "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp, \
                open(os.path.join(raw_dir, dest), "wb") as f:
            f.write(resp.read())

    for year in KAKAO_YEARS:
        for half in (1, 2):
            fetch(KAKAO_URL.format(year=year, half=half), f"kakao-{year}-h{half}.json")
            time.sleep(0.5)  # be polite: don't hammer the endpoint / trip bot protection
    fetch(NAVER_URL, "naver-statistics.json")
    print(f"downloaded {2 * len(KAKAO_YEARS) + 1} JSON payloads -> {raw_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=RAW_DIR, help="Dir of archived raw API JSON")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    ap.add_argument("--download", action="store_true",
                    help="Refresh raw/ from the live privacy.naver/kakao endpoints")
    args = ap.parse_args()
    if args.download:
        _download(args.raw)
    data = build(args.raw)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} rows, "
          f"{len({r[0] for r in data['rows']})} platforms, "
          f"{len({r[2] for r in data['rows']})} periods (coverage {data['coverage']})")


if __name__ == "__main__":
    main()
