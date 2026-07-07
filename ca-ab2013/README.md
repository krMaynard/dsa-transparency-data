# California AB 2013 — AI training-data transparency summary

**AB 2013** (the *Generative Artificial Intelligence: Training Data Transparency
Act*, in force **1 Jan 2026**) requires a developer of a generative-AI system or
service made available to Californians to post a **high-level summary of the
datasets used to train it** on its website. Google publishes one consolidated
**"AI Training Data Transparency Summary"** covering its generative-AI products
(Gemini Apps, Search, YouTube, Ads, Android, Pixel, …).

This is a **narrative** disclosure (prose, not numbers), so — like the NY ToS,
CA AB 587, DSA Table-11 and Japan corpora — it rides in the API's full-text
`report_narratives` search index (surfaced at `/narratives`), not a structured
table.

## What's built

`build_ca_ab2013_narratives.py` reads the archived PDF under `raw/` and splits
the single-page summary into four searchable sections (Overview, Data sources,
Training-data size, Data cleaning and preprocessing), each verified with a
fail-loud text anchor. Output `ca-ab2013-narratives.json` in the shared
page-based narrative shape (`company, platform, period, page, heading, text`).

```bash
python build_ca_ab2013_narratives.py   # raw/ PDF → ca-ab2013-narratives.json
```

Source: Google's summary, archived from its transparency-report bucket
(`storage.googleapis.com/transparencyreport/report-downloads/`, slug `jj`).
