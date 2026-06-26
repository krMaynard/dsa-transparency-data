#!/usr/bin/env python3
"""Download the curated latest harmonised-template file per hub-discovered platform.

Picks one representative file per catalogue platform (newest period; flagship
brand for multi-app providers). Saves into raw/ and reports HTTP status + type.
"""
import os, subprocess

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
CA = "/root/.ccr/ca-bundle.crt"

# slug -> url  (one representative, newest file per platform)
TARGETS = {
    "ceneo":       "https://shops.ceneo.pl/documents/Annex_I__Transparency_reports_templates%20-%20Ceneo%202025.xlsx",
    "cloudflare":  "https://cf-assets.www.cloudflare.com/slt3lc6tev37/1PrXCOS9RyhI2mQL7fz90h/8b49e28625ea35cd1d2055ca3b3e7853/dsa_template-transparency_report-H2_2025-v4.xlsx",
    "discord":     "https://cdn.discordapp.com/assets/2025/Discord-DSA_Transparency_Report.zip",
    "duckduckgo":  "https://duckduckgo.com/duckduckgo-help-pages/static-assets/reports/DSA_Transparency_Report-Feb_2026-DuckDuckGo-Search.xlsx",
    "expedia":     "https://legal.expediagroup.com/sites/default/files/Expedia%2C%20Inc.%20.xlsx",
    "hotelscom":   "https://legal.expediagroup.com/sites/default/files/Hotels.com%2C%20L.P.%20.xlsx",
    "vrbo":        "https://legal.expediagroup.com/sites/default/files/EG%20Vacation%20Rentals%20Ireland%20Ltd.%20.xlsx",
    "heise":       "https://www.heise.de/downloads/02/4/9/3/4/5/0/3/DSA-Reporting_2025.csv",
    "hometogo":    "https://cdn.hometogo.net/assets/media/xlsx/cc867bd70e505a6c09a0af479ebb54c1.xlsx",
    "hostelworld": "https://assets-us-01.kc-usercontent.com:443/7d675a4d-6977-00f0-abbc-5a21e22ae2eb/6ad19403-fbf2-47f3-b707-db099226be3c/Annex_I__Transparency_reports_HW%2031122025_ME0vKI0A1K5vzNvP3VciJ7y26R4_109690.xlsx",
    "hostinger":   "https://storage.googleapis.com/assets.hostinger.com/dsa-transparency-report/HOSTINGER-Transparency-Report-2025.xlsx",
    "imdb":        "https://imdb.com/static-exp/IMDb-EU-DSA-Transparency+Report+2025+H2+csv+format.zip",
    "konami":      "https://legal.konami.com/kde/eudsa/pdf/DSA_FY2025_TransparencyReport.xlsx",
    "lilo":        "https://lilo.org/rapport-transparence-2026.xlsx",
    "line":        "https://www.lycorp.co.jp/en/company/transparency/dsa-transparency/LY-DSA-Transparency-Report-Jan-2025-Dec-2025.xlsx",
    "matchgroup":  "https://cdn.prod.website-files.com/67c577f5d5cf176437c09b66/69a37ad1062c16c28feead18_tr_tinder_20250101_20251231.xlsx",
    "niantic":     "https://storage.googleapis.com/nianticweb-homesite-public/legal/20260305t1600/Annex_I__Transparency_Report_PokemonGO_2025.xlsx",
    "qwant":       "https://about.qwant.com/wp-content/uploads/2026/02/Qwant-Rapport-de-transparence-2025-.xlsx",
    "roblox":      "https://cms-media.roblox.com/assets/ioi8qk6q6qlkfbbfvghw.xlsx",
    "shopify":     "https://cdn.shopify.com/b/shopify-brochure2-assets/3a876f00221e2812a3451266238eceb1.xlsx",
    "skroutz":     "https://www.skroutz.gr/dsa-ekthesi-diafanias-periodos-anaforas-2025.xlsx",
    "wordpress":   "https://transparency.automattic.com/wp-content/uploads/2014/01/49ae2-wordpress.com-transparency-report-csv-files-jul-dec-2025.zip",
    "yahoo":       "https://s.yimg.com/cv/apiv2/default/20250828/DSA_Transparency_Report_Search_17_February_2025-31_December_2025.zip",
    "nintendo":    "https://www.nintendo.com/eu/media/downloads/legal_1/DSA_Transparency_Report_as_at_27th_February_2026_27022026.xlsx",
    "squareenix":  "https://static.square-enix-games.com/DSA_Transparency_Report_2025.xlsx",
    "alibabacloud": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/en-US/20260228/givrzs/EU+DSA+Transparency+Report+%282026%29_AlibabaCloud.zip",
}


def main() -> None:
    os.makedirs(RAW, exist_ok=True)
    for slug, url in sorted(TARGETS.items()):
        ext = ".zip" if url.lower().split("?")[0].endswith(".zip") else \
              ".csv" if url.lower().split("?")[0].endswith(".csv") else ".xlsx"
        dest = os.path.join(RAW, f"{slug}{ext}")
        p = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "90", "-A", UA, "--cacert", CA,
             "-o", dest, "-w", "%{http_code} %{content_type} %{size_download}",
             url], capture_output=True, text=True)
        print(f"{slug:14}{ext:5} {p.stdout or p.stderr.strip()}")


if __name__ == "__main__":
    main()
