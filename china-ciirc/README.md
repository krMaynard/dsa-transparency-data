# China CIIRC (12377) — online-report handling statistics

The Central Cyberspace Administration of China (**CAC**) **Illegal and Harmful
Information Reporting Center** (中央网信办违法和不良信息举报中心 — the national
**12377** hotline) publishes a monthly bulletin, **"全国网络举报受理情况"**, on how
many public reports of illegal / harmful online information (色情/赌博/侵权/谣言…
— obscenity, gambling, infringement, rumors) were handled that month, split by
the receiving body:

- **`central_center`** — 中央网信办举报中心, the central reporting center;
- **`local_departments`** — 各地网信举报工作部门, the provincial / local
  cyberspace-office departments;
- **`platforms`** — 全国主要网站平台, the major national websites & platforms (a
  **`commercial_platforms`** subset, 主要商业网站平台, is broken out some months);
- **`national_total`** — their sum.

Coarse (a few figures per month) but a genuine **multi-year series** — the one
major jurisdiction otherwise absent from this corpus. **79 months, Oct 2019 →
May 2026.** China discloses aggregate handling *volumes*, not the per-platform or
per-category breakdowns that Western reports carry.

## What's built

`build_ciirc.py --download` scrapes the notices listing (`/tzgg/listN.html`) and
each monthly post from `www.12377.cn`, archiving the raw HTML under `raw/`;
`build()` then parses the archived pages **offline** (deterministic). Figures are
published in 万 (ten-thousands) and stored as absolute counts.

Output `china-ciirc.json`, tidy-long
(`publisher, period, section, category, metric, unit, value`).

```bash
python build_ciirc.py --download   # re-scrape www.12377.cn → raw/, then build
python build_ciirc.py              # rebuild offline from raw/
```

### Parsing notes

The bulletin wording drifts across the 2019→ series (label variants; the newest
layout drops the opening national-total sentence; some months space every glyph,
`1872.2 万件`). The parser squashes whitespace, keys off the stable 中央网信办 /
各地网信 anchors, and **cross-checks** that `central + local + platforms`
reconciles with the stated national total within rounding slack — or it raises.
The `全国主要网站平台` prefix disambiguates the platforms breakdown line from the
headline-total sentence (which also contains "主要网站平台受理举报").

Source: `www.12377.cn/tzgg/` (通知公告 / notices). Values in `count` (万 × 10 000).
