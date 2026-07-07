# Japan — Information Distribution Platform Act (情報流通プラットフォーム対処法)

Japan's amended Provider Liability Limitation Act — the **Information
Distribution Platform Act** ("情プラ法", in force **1 April 2025**) — requires
MIC-designated *large specified telecommunications service providers* to
publicise their content-moderation operations. MIC (総務省) designated the core
five on 2025-04-30 — **Google (YouTube), LY Corporation (LINE/Yahoo! Japan),
Meta, TikTok, X** — and four more in May 2025 (Dwango/Niconico, CyberAgent/Ameba,
Pinterest, Bakusai).

There are two disclosure duties:

- **Art. 21** — publish your deletion-request window (送信防止措置の申出窓口) and
  deletion criteria (実施基準). *Qualitative.* Live since ~late July 2025.
- **Art. 28** — publish implementation-status **statistics** once a year, within
  two months of fiscal-year end. Japan's FY ends 31 Mar, so the first mandatory
  statistical cycle is **FY2025 (Apr 2025 – Mar 2026), due ~end May 2026**.

## Status of the data (as of this snapshot)

**Only LY Corporation currently publishes statistics.** Its **Media Transparency
Report** (メディア透明性レポート) gives per-service post and deletion counts —
split into self-detected vs. user-reported deletions — explicitly restructured to
match the 情プラ法 施行規則 categories. The FY2024 edition (published May 2025) is
archived here in `raw/lycorp-transparency-2024.pdf`
(<https://www.lycorp.co.jp/ja/company/transparencyreport2024.pdf>). It is a
**Japanese-only PDF** with no HTML/CSV data table.

**Google, Meta, TikTok and X** publish only the qualitative Art. 21 criteria /
window pages — **no statistics yet**. There is **no common MIC template, no
aggregated MIC dataset, and no CSV/JSON feed**; MIC's own collated PDFs
(e.g. <https://www.soumu.go.jp/main_content/001031570.pdf>) are image-like and
not text-extractable.

MIC materials:
- Hub: <https://www.soumu.go.jp/main_sosiki/joho_tsusin/d_syohi/ihoyugai.html>
- English designation notice: <https://www.soumu.go.jp/main_sosiki/joho_tsusin/eng/pressrelease/2025/4/30_3.html>

## Why there's no builder yet

A harmonised cross-platform dataset can't be assembled today: four of the five
core providers publish no figures, and the one that does (LY Corp) is a
heterogeneous Japanese-only PDF. This directory **archives the one real report**
and documents the regime; a builder is deferred until the first Art. 28
statistical disclosures land (expected H2 2026), at which point this can be
modelled like the Türkiye Law 5651 single-platform dataset.
