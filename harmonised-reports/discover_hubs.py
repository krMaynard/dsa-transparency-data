#!/usr/bin/env python3
"""Discover direct template-file links on the hub-pending landing pages.

For each `hub-pending` platform in sources.csv, fetch the landing page and scan
the HTML for links to a harmonised-template file (.xlsx/.xls/.csv/.zip). Prints
one line per platform with any candidate file URLs found (resolved to absolute).
Static-HTML only — JS-rendered hubs will show no candidates.
"""
import csv, os, re, subprocess, sys, json
from urllib.parse import urljoin

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = "/root/.ccr/ca-bundle.crt"
EXT_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+\.(?:xlsx|xls|csv|tsv|ods|zip))(?:\?[^"\']*)?["\']', re.I)


def fetch(url: str) -> tuple[int, str]:
    try:
        p = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "40", "-A", UA, "--cacert", CA,
             "-w", "\n%{http_code}", url],
            capture_output=True, text=True, timeout=50)
        out = p.stdout
        code = out.rsplit("\n", 1)[-1].strip()
        return (int(code) if code.isdigit() else 0, out.rsplit("\n", 1)[0])
    except Exception:
        return (0, "")


def main() -> int:
    rows = list(csv.DictReader(open(os.path.join(HERE, "sources.csv"), encoding="utf-8-sig")))
    hubs = [r for r in rows if r["status"] == "hub-pending"]
    found = {}
    for r in hubs:
        url = r["source_url"]
        if url.lower().endswith(".pdf"):
            print(f"{r['platform']:42} PDF (narrative, not template)")
            continue
        code, html = fetch(url)
        cands = []
        seen = set()
        for m in EXT_RE.findall(html):
            absu = urljoin(url, m)
            if absu not in seen:
                seen.add(absu); cands.append(absu)
        if cands:
            found[r["platform"]] = cands
            print(f"{r['platform']:42} {code} -> {len(cands)} candidate(s)")
            for c in cands[:4]:
                print(f"{'':44}{c}")
        else:
            print(f"{r['platform']:42} {code} -> no static file link")
    print(f"\n{len(found)} platforms with candidate file links")
    with open(os.path.join(HERE, "hub_candidates.json"), "w", encoding="utf-8") as f:
        json.dump(found, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
