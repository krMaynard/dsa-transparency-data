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

## What's built (LY Corporation + Google/YouTube + Meta)

**Three providers now publish statistics: LY Corporation, Google (YouTube) and
Meta.** `build_japan.py` writes the tidy-long `japan-info-platform.json`, whose
`columns` are `service, period, section, category, metric, unit, value` — LY
Corp's rows sit in section `posts_activity` (category `All`); YouTube's and
Meta's carry a `section` per report table and a `category` per reason/violation
type (`Total` for the section aggregate).

**LY Corporation** — its **Media Transparency Report** (メディア透明性レポート,
FY2024, published May 2025) gives, per service, a quarterly table
(『四半期ごとの投稿件数・投稿削除件数及び投稿削除割合』) with the FY2024 quarters and
the annual total. `build_japan.py` parses those five tables (archived in
`raw/lycorp-transparency-2024.pdf`):

- **Services**: Yahoo! Chiebukuro (知恵袋), Yahoo! Finance boards (ファイナンス
  掲示板), LINE OpenChat (オープンチャット), LINE VOOM, Yahoo! News comments
  (ヤフコメ).
- **`period`**: the FY2024 quarters (`2024-04..2024-06` … `2025-01..2025-03`) and
  the annual total (`2024-04..2025-03`).
- **`metric`** / **`unit`**: `posts` (投稿件数, count), `posts_removed`
  (投稿削除件数, count), `removal_rate` (投稿削除割合, percent).

**Google (YouTube)** — its **Japan Information Platform Act Transparency Report**
(26 Jul 2025 – 31 Mar 2026, published May 2026; archived in
`raw/youtube-japan-2025h2-{en,ja}.pdf`) gives Japan-specific figures, transcribed
with each breakdown cross-checked against its stated Total (the builder raises on
any mismatch). `period` is the report window `2025-07-26..2026-03-31`; the
`section`s are:

- `legal_requests` (requests received for Legal Removals, by reason),
  `legal_extended_review_notifications`, `legal_items` (identified — Removed / Not
  removed) and `legal_removals` (by reason) — the Art. 28 (i)(ii)/(iv) legal
  stream;
- `user_flags` (human flags by reason), `policy_removals` (videos removed by
  reason), `policy_detection_source` (videos removed by first-detection source),
  `suspensions` (channel terminations by reason) and `appeals`
  (appeals / reinstatements) — the Art. 28 (iv) policy stream;
- `platform` — headline figures: `monthly_active_users` (106.4M), qualified
  Japanese-language `qualified_reviewers` (293), `expert_investigation_cases` (6),
  `notifications_withheld` (0).

**Meta** — its **Information Distribution Platform Act Annual Transparency
Report** (30 Jul 2025 – 31 Mar 2026, published 31 May 2026; archived in
`raw/meta-japan-idpa-2026.pdf`) reports its three designated services —
**Facebook, Instagram and Threads** — *separately* (so `service` is one of those
three). `period` is `2025-07-30..2026-03-31`; the figures are transcribed from
the report tables (`build_meta()`), which are structural-checked only (see the
caveat below — Meta's own totals don't reconcile). The `section`s are:

- `requests_received`, `decisions_within_7d`, `decisions_after_7d`,
  `requests_no_action` — the Art. 22 rights-report channel (Tables 2.2, 3.1.1–3),
  `category` = a reporting reason (Portrait rights, Invasion of privacy, …);
- `content_actions`, `account_actions` (Tables 4.2/4.3), `user_report_actions`
  (5.3.1), `user_report_reviewed` (5.3.2, metrics `content_reported` +
  `content_not_actioned`), `proactive_actions` (5.3.3) and `account_suspensions`
  (5.4.2.1–3, metric per detection method — proactive/report/regulator/court) —
  enforcement by **violation type** (`category` = Spam, Fraud and Deception,
  Local Law Violations, …);
- `appeals` (Table 7.1) — `category='All'`, one `metric` per appeal type
  (`content_appeals`, `content_appeals_ai`, `content_appeal_reversals`, …);
- `platform` (Table 1.4) — `content_pieces` + `monthly_active_users`, `unit`
  `approx_count` (Meta reports these rounded, e.g. "4.2 billion").

Two Meta tables are **omitted**: **5.3.4** (regulator requests) has a
non-per-service "Requests" column and Meta itself flags (footnote 10) it cannot
disaggregate content- vs account-actions, with internally inconsistent tiny
counts; **5.3.5** (court orders) is all-zero ("None received").

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

- **LY Corporation + Google (YouTube) + Meta.** TikTok and X still publish only
  the qualitative Art. 21 criteria/window pages — **no statistics yet**. There is
  no common MIC template, aggregated MIC dataset, or CSV/JSON feed to harmonise
  against, and the three providers' figures are **not comparable** (LY Corp
  reports posts/removals per service and quarter; YouTube reports legal/policy
  actions by reason; Meta reports content/account enforcement by violation type
  per service — each on its own window). Additional providers slot in as they
  publish their first Art. 28 statistics.
- **Cross-section / cross-service care.** Metrics and units are never comparable
  across `section`s (LY Corp `posts` vs YouTube `flags`/`videos_removed`/… vs
  Meta `actions`/`requests`/…), and every YouTube/Meta section carries a `Total`
  category beside its breakdown, so summing over `category` double-counts. Pin
  `service`, `section` **and** `category` before aggregating.
- **Meta's totals don't reconcile — by design and by defect.** Meta's per-policy
  breakdowns are the report's own *"most prevalent categories"* — an **illustrative
  subset**, not a partition — so the `Total` category is a **superset**, not the
  sum of the listed categories. And Meta's own figures don't fully add up even
  where they should (per its logging-issue footnotes: Right-to-honor/Feelings-of-honor
  and Trademark/Copyright reasons are combined; <30 requests went uncategorised;
  `decisions_after_7d`'s Threads `Total` of 23 even sits *below* its Portrait-rights
  category of 25). `build_meta()` therefore does **structural** validation only
  (non-negative ints, well-formed per-service triples) — it deliberately does not
  assert `Total == sum` or `Total >= category`. Meta reports its Table 1.4
  platform figures **rounded** (`unit='approx_count'`).
- `removal_rate` (LY Corp) is a **percent** (posts-removed ÷ posts, per the
  report's own definition) — never SUM it. Removals may act on posts from earlier
  years, so the rate approximates the current-year ratio (the report notes this).
- YouTube's `policy_removals` and `policy_detection_source` are two cross-cuts of
  the **same** 162,390 removed videos (by reason vs by first-detection source), so
  their totals match by construction — don't add them together. Its global,
  banded Violative View Rate (VVR) figures are qualitative context and aren't
  ingested here.

## Narrative (prose) — `build_japan_narratives.py`

`build_japan.py` pulls the *numbers*; **`build_japan_narratives.py`** pulls the
**prose** — how each service describes its purpose, rules, response to violations,
detection (AI + human review), and the cross-service (共通編) sections on
countering misinformation, FY2024 new initiatives, the monitoring framework and
healthy-discourse work — so it can be full-text searched alongside the other
report narratives in `transparency-report-api` (NY ToS, CA AB 587, DSA Table-11).

The source report is **Japanese-only**, so each section is stored **bilingually**:
a curated English translation followed by the Japanese original prose, both in one
searchable `text` field. The translations are curated in the script (like
`build_japan.py`'s expected-figure constants), keeping the build deterministic and
offline; every section carries a `ja_check` phrase that must still appear on its
page, so the build **fails loudly** if the vendored PDF drifts.

Output `japan-narratives.json` is tidy-long — one row per section, columns
`company, platform, period, page, heading, text` — matching the page-based
narrative shape the API's `_build_narratives` loader expects (seeded under
`source='japan'`).

```bash
python build_japan_narratives.py   # → japan-narratives.json (19 sections)
```

## Refresh

```bash
python build_japan.py              # re-parses raw/lycorp-transparency-2024.pdf
python build_japan_narratives.py   # re-parses the prose → japan-narratives.json
```

MIC materials: hub
<https://www.soumu.go.jp/main_sosiki/joho_tsusin/d_syohi/ihoyugai.html> ·
English designation notice
<https://www.soumu.go.jp/main_sosiki/joho_tsusin/eng/pressrelease/2025/4/30_3.html>.
