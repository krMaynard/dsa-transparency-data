#!/usr/bin/env python3
"""Refresh the harmonised EU DSA VLOP/VLOSE reports for 2026 H1.

Sources are first-party publication endpoints except for Meta's expiring CDN
links, which use stable public mirrors of the publisher files. Archives are
validated for the eleven Annex I tables before the existing snapshot is replaced.
"""

from __future__ import annotations

import io
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).parent
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; transparency-report-api/1.0)"}

ZIP_SOURCES = {
    "AliExpress": (
        "https://files.alicdn.com/tpsservice/474273ced7af5400e2be5c4d371ad158.zip",
        "aliexpress",
    ),
    "Amazon": (
        "https://trustworthyshopping.aboutamazon.com/eu-transparency-report-amazon-jan-jun-2026",
        "amazon",
    ),
    "Booking.com": (
        "https://q-xx.bstatic.com/data/mobile/DSA_Transparency_Report_-_7th_report_-_28_August_2026.zip",
        "booking-com",
    ),
    "LinkedIn": (
        "https://delivery-p143253-e1476319.adobeaemcloud.com/adobe/assets/urn:aaid:aem:5a48363c-f3e8-494e-8373-d3719fe2e64b/original/as/LinkedIn-August-2026-Digital-Services-Act-Transparency-Report%201.zip",
        "microsoft/linkedin",
    ),
    "Facebook": (
        "https://www.dropbox.com/scl/fo/sn8obizepy0b820ghx7hl/ANt4esTxKgumB24j_Gc02V0?rlkey=7psfjcho7dxbzr30m5k6azp39&dl=1",
        "meta/facebook",
    ),
    "Instagram": (
        "https://www.dropbox.com/scl/fo/r17ikmgoh8t82wp3xdb3k/ALeZS649LWW0_1IweAxOdmg?rlkey=2c6k20t0bbrtodnuwq7leaafu&dl=1",
        "meta/instagram",
    ),
    "Pinterest": (
        "https://cdn.sanity.io/files/26f0hyrt/pinpolicy_prod/a3222c3ee1b4b5a9385fc4194174751ec71d1cbb.zip",
        "pinterest",
    ),
    "Pornhub": (
        "https://ei.phncdn.com/static/misc/legal/Pornhub_DSA_Transparency_Report_August_2026_1787935691.zip",
        "pornhub",
    ),
    "Temu": (None, "temu"),
    "TikTok": (
        "https://sf16-va.tiktokcdn.com/obj/eden-va2/zayvwlY_fjulyhwzuhy%5B/ljhwZthlaukjlkulzlp/DSA_H1_2026/TikTok%20DSA%20Transparency%20Report%20Jan-June%202026_.zip",
        "tiktok",
    ),
    "WhatsApp Channels": (None, "whatsapp-channels"),
    "X": (
        "https://transparency.x.com/content/dam/transparency-twitter/dsa/transparency-report/DSA-Transparency-Report-H1-2026.zip",
        "x",
    ),
    "XNXX": (
        "https://public-assets.xnxx-cdn.com/transparency/XNXX+-+Transparency+report+-+January-June+2026.zip",
        "xnxx",
    ),
    "XVideos": (
        "https://public-assets.xvideos-cdn.com/transparency/XVideos+-+Transparency+report+-+January-June+2026.zip",
        "xvideos",
    ),
    "Zalando": (
        "https://corporate.zalando.com/sites/default/files/media-download/zalando-se_dsa-transparency-report-august-2026.zip",
        "zalando",
    ),
}

XLSX_SOURCES = {
    "App Store": (
        "https://www.apple.com/legal/dsa/transparency/eu/App-Store-August-2026.xlsx",
        "apple/app-store.xlsx",
    ),
    "Bing": (
        "https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/CY2026-H1-Microsoft-Bing-EU-DSA-Report1.xlsx",
        "microsoft/bing.xlsx",
    ),
    "SHEIN": (
        "https://shein.ltwebstatic.com/tinypic/2026/09/02/17883154343995654501.xlsx",
        "shein.xlsx",
    ),
    "Snapchat": (
        "https://assets.ctfassets.net/kw9k15zxztrs/6x5387aq1lqbPysLxLJ2dd/1a6a4bf6918b6f98e41250d5f0fe570f/Snap_DSA_TR_H1_2026.xlsx",
        "snapchat.xlsx",
    ),
}


def get(session: requests.Session, url: str) -> bytes:
    response = session.get(url, headers=HEADERS, timeout=120)
    response.raise_for_status()
    return response.content


def temu_url(session: requests.Session) -> str:
    landing = "https://www.temu.com/de/transparency-center-reports.html"
    session.get(landing, headers={**HEADERS, "Accept-Language": "de-DE,de;q=0.9"}, timeout=60).raise_for_status()
    response = session.post(
        "https://www.temu.com/api/bg-marmot-api/legal/report/query/all",
        json={"biz_id": 1},
        headers={**HEADERS, "Accept-Language": "de-DE,de;q=0.9", "Referer": landing},
        timeout=60,
    )
    response.raise_for_status()
    reports = response.json()["result"]["report_map"]["4"]["report_list"]
    match = next(
        item for item in reports
        if "2026" in item["effective_start_date"] and item["file_path_url"].endswith(".zip")
    )
    return match["file_path_url"]


def whatsapp_url(session: requests.Session) -> str:
    landing = "https://www.whatsapp.com/legal/transparencyreports?lang=en"
    soup = BeautifulSoup(get(session, landing), "html.parser")
    for anchor in soup.select("a[href]"):
        label = " ".join(anchor.get_text(" ", strip=True).split())
        if (
            "1 January 2026" in label
            and "30 June 2026" in label
            and ".zip" in anchor["href"].lower()
        ):
            return urljoin(landing, anchor["href"])
    raise RuntimeError("WhatsApp Channels 2026 H1 VLOP archive was not found")


def google_sources(session: requests.Session) -> list[tuple[str, str, str]]:
    endpoint = (
        "https://transparencyreport.google.com/transparencyreport/"
        "api/v3/shareddata/pdf/allfilepaths?report_id=27"
    )
    response = session.get(endpoint, headers=HEADERS, timeout=60)
    response.raise_for_status()
    payload = response.text.removeprefix(")]}'\n\n")
    rows = response.json() if not payload.startswith("[[") else __import__("json").loads(payload)
    details = rows[0][1]
    destinations = {
        "Google Maps": "google/maps",
        "Google Play": "google/play",
        "Google Search": "google/search",
        "Google Shopping": "google/shopping",
        "Multi-Services": "google/multi-services",
        "YouTube": "google/youtube",
    }
    current = []
    for start, end, locale, url, service in details:
        if start == [2026, 1, 1] and end == [2026, 6, 30] and locale == "en":
            current.append((service, url, destinations[service]))
    if len(current) != len(destinations):
        raise RuntimeError(f"Google: expected {len(destinations)} current reports, found {len(current)}")
    return current


def table_number(filename: str) -> int | None:
    name = Path(filename).name
    match = re.search(r"(?:^|[- ]\s*)(1[01]|[1-9])(?:[_. -])", name)
    return int(match.group(1)) if match else None


def install_zip(name: str, payload: bytes, target: Path) -> None:
    if not zipfile.is_zipfile(io.BytesIO(payload)):
        raise RuntimeError(f"{name}: response is not a ZIP archive")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        members = [
            m for m in archive.infolist()
            if not m.is_dir()
            and m.filename.lower().endswith(".csv")
            and not Path(m.filename).name.startswith("._")
        ]
        tables = {table_number(m.filename) for m in members}
        if not set(range(1, 12)).issubset(tables):
            raise RuntimeError(f"{name}: missing Annex I tables; found {sorted(t for t in tables if t)}")
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp)
            for member in members:
                output = staging / Path(member.filename).name
                output.write_bytes(archive.read(member))
            target.mkdir(parents=True, exist_ok=True)
            for old in target.glob("*.csv"):
                old.unlink()
            for csv_file in staging.glob("*.csv"):
                shutil.copy2(csv_file, target / csv_file.name)
    print(f"{name}: installed {len(members)} CSV tables in {target.relative_to(ROOT)}")


def validate_xlsx(name: str, payload: bytes) -> None:
    if not zipfile.is_zipfile(io.BytesIO(payload)):
        raise RuntimeError(f"{name}: response is not an XLSX workbook")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
    for table in range(1, 12):
        if f'name="{table}_' not in workbook:
            raise RuntimeError(f"{name}: workbook is missing table {table}")


def main() -> None:
    session = requests.Session()
    dynamic = {
        "Temu": temu_url(session),
        "WhatsApp Channels": whatsapp_url(session),
    }
    for name, (url, destination) in ZIP_SOURCES.items():
        resolved = url or dynamic[name]
        install_zip(name, get(session, resolved), ROOT / destination)
    for name, url, destination in google_sources(session):
        install_zip(name, get(session, url), ROOT / destination)
    for name, (url, destination) in XLSX_SOURCES.items():
        payload = get(session, url)
        validate_xlsx(name, payload)
        output = ROOT / destination
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        print(f"{name}: installed workbook in {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
