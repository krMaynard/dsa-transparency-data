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

## Authoritative requirements

- [European Commission template and explanatory notice](https://digital-strategy.ec.europa.eu/en/library/explanatory-notice-and-template-public-summary-training-content-general-purpose-ai-models)
- [European Commission template FAQ](https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content)

The template applies to models placed on the Union market from 2 August 2025;
pre-existing models have a transitional deadline of 2 August 2027. The AI Office
can enforce the obligations from 2 August 2026.
