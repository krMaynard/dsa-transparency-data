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
  two months of fiscal-year end (Japan's FY ends 31 Mar).

## What's built (LY Corporation only)

**Only LY Corporation currently publishes statistics.** Its **Media Transparency
Report** (メディア透明性レポート, FY2024, published May 2025) gives, per service, a
quarterly table (『四半期ごとの投稿件数・投稿削除件数及び投稿削除割合』) with the
FY2024 quarters and the annual total. `build_japan.py` parses those five tables
(archived in `raw/lycorp-transparency-2024.pdf`) into the tidy-long
`japan-info-platform.json` (`columns` = `service, period, metric, unit, value`):

- **Services**: Yahoo! Chiebukuro (知恵袋), Yahoo! Finance boards (ファイナンス
  掲示板), LINE OpenChat (オープンチャット), LINE VOOM, Yahoo! News comments
  (ヤフコメ).
- **`period`**: the FY2024 quarters (`2024-04..2024-06` … `2025-01..2025-03`) and
  the annual total (`2024-04..2025-03`).
- **`metric`** / **`unit`**: `posts` (投稿件数, count), `posts_removed`
  (投稿削除件数, count), `removal_rate` (投稿削除割合, percent).

FY2024 annual headline figures (verified against the report's prose summary — the
builder raises if a parsed annual total doesn't match):

| Service | Posts | Removed | Rate |
|---|--:|--:|--:|
| Yahoo! Chiebukuro | 66,199,309 | 444,727 | 0.7% |
| Yahoo! Finance boards | 29,415,652 | 487,773 | 1.7% |
| LINE OpenChat | 5,514,828,787 | 6,980,935 | 0.1% |
| LINE VOOM | 403,331,897 | 3,055,002 | 0.8% |
| Yahoo! News comments | 113,995,832 | 1,277,396 | 1.1% |

### Caveats

- **LY Corporation only.** Google, Meta, TikTok and X publish only the
  qualitative Art. 21 criteria/window pages — **no statistics yet**. There is no
  common MIC template, aggregated MIC dataset, or CSV/JSON feed to harmonise
  against; MIC's own collated PDFs (e.g.
  <https://www.soumu.go.jp/main_content/001031570.pdf>) are image-like and not
  text-extractable.
- `removal_rate` is a **percent** (posts-removed ÷ posts, per the report's own
  definition) — never SUM it. Removals may act on posts from earlier years, so
  the rate is an approximation of the current-year ratio (the report notes this).
- The report also carries deletion-by-reason breakdowns and court/disclosure
  request counts per service; this first pass captures the headline
  posts/removals/rate tables. Additional providers slot in as they publish their
  first Art. 28 statistics (expected H2 2026 onward).

## Refresh

```bash
python build_japan.py     # re-parses raw/lycorp-transparency-2024.pdf
```

MIC materials: hub
<https://www.soumu.go.jp/main_sosiki/joho_tsusin/d_syohi/ihoyugai.html> ·
English designation notice
<https://www.soumu.go.jp/main_sosiki/joho_tsusin/eng/pressrelease/2025/4/30_3.html>.
