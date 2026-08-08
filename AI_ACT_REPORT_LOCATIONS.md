# EU AI Act Article 53 training-content report locations

Filled public summaries found for general-purpose AI models under Article
53(1)(d) of Regulation (EU) 2024/1689. The normalized extraction and methodology
live in [`ai-training-transparency/`](ai-training-transparency/).

The Commission does not maintain a registry of filled summaries. Providers must
publish them with the model and on their own official site or distribution
channel, so this catalog records the upstream location and local archive.

## Newly verified in August 2026

| Provider | Models covered | Official source | Local archive | Status |
|---|---|---|---|---|
| Polish Ministry of Digital Affairs (PLLuM) | PLLuM 2512 base family (3 variants) | [Official model repository](https://huggingface.co/CYFRAGOVPL/PLLuM-4B-base-2512/blob/main/PLLuM_2512_base_Public_Summary_of_Training_Content.pdf) | [`pllum-2512-base`](ai-training-transparency/raw/pllum-2512-base-eu-training-summary.pdf) | verified |
| Polish Ministry of Digital Affairs (PLLuM) | PLLuM 2512 instruct family (4 variants) | [Official model repository](https://huggingface.co/CYFRAGOVPL/Llama-PLLuM-70B-instruct-2512/blob/main/PLLuM_2512_instruct_Public_Summary_of_Training_Content.pdf) | [`pllum-2512-instruct`](ai-training-transparency/raw/pllum-2512-instruct-eu-training-summary.pdf) | verified |
| Polish Ministry of Digital Affairs (PLLuM) | PLLuM 2512 chat family (4 variants) | [Official model repository](https://huggingface.co/CYFRAGOVPL/Llama-PLLuM-70B-instruct-2512/blob/main/PLLuM_2512_chat_Public_Summary_of_Training_Content.pdf) | [`pllum-2512-chat`](ai-training-transparency/raw/pllum-2512-chat-eu-training-summary.pdf) | verified |
| EuroLLM Team | EuroLLM 9B/22B base and instruct family (6 variants) | [Official model repository](https://huggingface.co/utter-project/EuroLLM-22B-Instruct-2512/blob/main/EuroLLM_Public_Summary.pdf) | [`eurollm`](ai-training-transparency/raw/eurollm-eu-training-summary.pdf) | verified |

## Current extracted coverage

The dataset now contains 15 summary entries across 11 providers: Bria, EuroLLM,
Google, Hugging Face, Meta, Microsoft, OpenAI, Poland's Ministry of Digital
Affairs (PLLuM), SpeakLeash, Swiss AI, and xAI. A summary entry may cover several
model versions; the three PLLuM entries cover 11 variants and EuroLLM covers six.

## Claimed but not retrievable

| Provider | Model | Official evidence | Browser audit | Status |
|---|---|---|---|---|
| Domyn S.p.A. | Domyn Small v1.0 | [Official model card](https://huggingface.co/domyn/Domyn-Small-v1.0#eu-ai-act-compliance) · [official technical report](https://secure.domyn.com/Website/Research/Papers/domyn_small_arxiv_submission.pdf) | Audited in Chrome on 8 Aug 2026. Both sources say the Article 53(1)(d) summary is a “companion artefact,” but neither links it. The rendered repository file tree contains the model card, weights, configuration, tokenizer and serving plugins, but no training-content summary. | claimed; not retrievable; not ingested |

The Domyn technical report is useful supporting evidence, but it is not a
substitute for a filled Commission public-summary template. It discloses an
approximately 9-trillion-token foundation corpus, a 503-billion-token continued
pre-training phase and high-level source/category proportions. It then refers to
a separate companion artefact instead of providing or locating that artefact.
The missing link is therefore a publication/discoverability gap, not proof that
Domyn never prepared the summary.

## Authoritative requirements

- [European Commission template and explanatory notice](https://digital-strategy.ec.europa.eu/en/library/explanatory-notice-and-template-public-summary-training-content-general-purpose-ai-models)
- [European Commission template FAQ](https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content)

The template applies to models placed on the Union market from 2 August 2025;
pre-existing models have a transitional deadline of 2 August 2027. The AI Office
can enforce the obligations from 2 August 2026.

## Enforcement details

- The European Commission has exclusive power to supervise and enforce the
  GPAI rules in Chapter V and implements that work through the AI Office
  ([Article 88](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-88)).
- The Article 53 duties applied from 2 August 2025. Commission enforcement
  powers became operational on 2 August 2026. Only models placed on the market
  before 2 August 2025 retain the transition to 2 August 2027.
- An open-source release can still be a placing on the Union market. The
  open-source exception in Article 53(2) covers only the technical and
  downstream documentation duties in Article 53(1)(a) and (b), and does not
  remove the copyright-policy or public training-summary duties in (c) and (d).
- The AI Office may begin with a technical compliance dialogue. The Commission
  can then request documents and information under Article 91, evaluate a model
  through APIs or other technical means including source code under
  [Article 92](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-92),
  and require compliance measures under
  [Article 93](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-93).
  Available Article 93 measures include restricting market availability,
  withdrawal or recall of a model.
- Under [Article 101](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-101),
  an intentional or negligent violation can draw a fine of up to 3% of the
  provider's preceding-year worldwide turnover or EUR 15 million, whichever is
  higher. The same ceiling covers failure to supply requested information,
  comply with an Article 93 measure or provide model access for evaluation.
  The provider must receive the Commission's preliminary findings and an
  opportunity to be heard before a fine is adopted.

Domyn Small was released in May 2026 and self-identifies as a GPAI model, so it
is in the post-2-August-2025 cohort rather than the legacy-model transition.
Nothing in the public materials reviewed establishes that it exceeds the
10^25-FLOP presumption for systemic risk or has been designated as systemic-risk.
That does not affect its Article 53(1)(d) public-summary obligation.
