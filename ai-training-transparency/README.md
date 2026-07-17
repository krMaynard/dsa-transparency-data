# EU AI Act — AI training-data transparency summaries

**Article 53(1)(d)** of the EU AI Act (Reg. (EU) 2024/1689) requires providers of
**general-purpose AI models** to publish a *public summary of the content used to
train the model*, on the AI Office's standardised template (in force **2 Aug
2025**; 26 providers signed the GP-AI Code of Practice — OpenAI, Anthropic,
Microsoft, Mistral, Google, … — Meta the notable holdout). Each summary discloses,
per modality, a **banded training-data size**, the data-acquisition cut-off, and
yes/no flags per data-source category.

## What's built

`build_ai_training.py` → `ai-training-transparency.json`, a **cross-provider,
comparable** tidy-long dataset
(`provider, model, released, section, field, value, size_rank`) from the
summaries archived in `raw/`. Two `section`s:

- **`modality`** — `field` = Text / Image / Audio / Video / Other; `value` = the
  disclosed size band; **`size_rank`** = 1 / 2 / 3 for the three bands (0 = "Not
  applicable"), so the coarse sizes are **numerically comparable across
  providers**.
- **`general`** — `data_cutoff`, `ongoing_collection`.
- **`data_source`** — `publicly_available`, `commercially_licensed`,
  `third_party_private`, `personal_data`, `synthetic` (`value` = Yes / No / Not
  applicable / …).

Example comparison (Text training-data size):

| Provider | Model | Text size | rank |
|---|---|---|:--:|
| Google | Gemini 3 Pro family | More than 10 trillion tokens | 3 |
| Meta | Muse Spark | More than 10 trillion tokens | 3 |
| xAI | Grok 4.5 | More than 10 trillion tokens | 3 |
| Bria | Bria 3.2 | 1 billion to 10 trillion tokens (reported as: up to 19.2 billion tokens) | 2 |
| Microsoft | phi-4 / Phi-4-multimodal / Phi-4-mini | 1 billion to 10 trillion tokens | 2 |

### Sources & method

There is **no single registry** of the *filled* summaries — each provider
self-publishes in its own format — so the builder reads three source shapes:

- **Markdown "data summary cards"** (Microsoft's convention on Hugging Face,
  `microsoft/<model>/data_summary_card.md`) — template fields as
  `**1.3.1.A Text training data size:** …` lines, parsed by their stable numeric
  codes (generic — new providers using the same markdown template parse for free).
- **PDF** (Google + Meta + OpenAI + xAI + Swiss AI + SpeakLeash, on their
  transparency buckets / Hugging Face) — the size bands are **checkbox**
  selections (Google's don't render in the text layer; Meta lays them out as form
  cells; OpenAI's, xAI's and Swiss AI's ☒/☐ render; Bielik uses a literal `X`
  marker), so those values are **curated** from the rendered form and
  cross-checked with fail-loud anchors against the PDF text (model name, market
  date, cut-off). Meta groups Image &
  Video as one "Perception" modality (recorded on both rows) and breaks out
  `crawled` / `user_data`; OpenAI files on the full template (its `user_data` is
  Yes via other products — ChatGPT/Codex — though model-interaction data was
  not used). **xAI** (Grok 4.5, placed on the Union market 14 Jul 2026) answers
  Yes to *every* data-source category (2.1–2.6) and is the first filer here that
  is **not** a Code-of-Practice signatory (3.1 = No) — it describes honouring
  opt-out signals directly instead. The two open/EU models are text-only:
  **Apertus** (Swiss AI —
  ETH Zürich / EPFL / CSCS, ~15T tokens, public data only, no own crawler) and
  **Bielik** (SpeakLeash, a Polish LLM continued from Mistral 7B, own
  "Speakleash" crawler + synthetic + licensed data).
- **Hugging Face Space** — **SmolLM3** (Hugging Face) publishes its summary in a
  Gradio Space (an interactive `hf.space` app), not a PDF. We archive the
  Space's `app.py` (which embeds the filled template as HTML) under `raw/` and
  curate + anchor-check against it, same as the PDF providers. Text-only,
  ~11T tokens, public + synthetic data only (no crawling / licensing / user /
  private data).
- **HTML page** — **Bria 3.2** publishes its summary as a page on its own site
  (`bria.ai/eu-policy`), so we archive the page under `raw/` and anchor-check
  against it. An image-generation model trained **exclusively on commercially
  licensed data** — the only filer so far with *both* `publicly_available` = No
  and `crawled` = No. It also **didn't tick the size bands**: it wrote exact
  figures ("Up to 19.2 billion tokens", "479 million images") into the size
  cells, so we record the band those figures fall in (keeping `size_rank`
  comparable) and preserve the disclosed figure verbatim in the value. Its
  Audio/Video/Other rows are **omitted** rather than "Not applicable" — its table
  simply has no rows for them, so the summary doesn't actually say.

**Coverage is a starting, expandable set** (Google + Meta + Microsoft + OpenAI +
xAI + Swiss AI + SpeakLeash + Hugging Face + Bria; 11 model entries). More
providers slot in as their summaries are archived under `raw/`. Notably, several
Code-of-Practice signatories (Anthropic — incl. Fable 5 —, Mistral, Cohere,
Aleph Alpha, Stability) have **not** published the standardised template — they
disclose training content only as free-form prose (model cards) or rely on the
2 Aug 2027 transitional deadline for pre-existing models. The inverse also holds:
xAI filed the template **without** signing the Code of Practice, so the two
commitments track each other loosely at best.

## Refresh

```bash
python build_ai_training.py     # re-reads raw/ → ai-training-transparency.json
```

Template + explanatory notice:
<https://digital-strategy.ec.europa.eu/en/library/explanatory-notice-and-template-public-summary-training-content-general-purpose-ai-models>.
