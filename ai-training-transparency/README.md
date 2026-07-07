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
| Microsoft | phi-4 / Phi-4-multimodal / Phi-4-mini | 1 billion to 10 trillion tokens | 2 |

### Sources & method

There is **no single registry** of the *filled* summaries — each provider
self-publishes in its own format — so the builder reads two source shapes:

- **Markdown "data summary cards"** (Microsoft's convention on Hugging Face,
  `microsoft/<model>/data_summary_card.md`) — template fields as
  `**1.3.1.A Text training data size:** …` lines, parsed by their stable numeric
  codes (generic — new providers using the same markdown template parse for free).
- **PDF** (Google, on its transparency-report bucket) — the size bands are
  **checkbox** selections not in the PDF text layer, so Google's values are
  **curated** from the rendered form and cross-checked with fail-loud anchors
  against the PDF text (model name, market date, knowledge cut-off).

**Coverage is a starting, expandable set** (Google + Microsoft; 4 model entries).
More providers slot in as their summaries are archived under `raw/`.

## Refresh

```bash
python build_ai_training.py     # re-reads raw/ → ai-training-transparency.json
```

Template + explanatory notice:
<https://digital-strategy.ec.europa.eu/en/library/explanatory-notice-and-template-public-summary-training-content-general-purpose-ai-models>.
