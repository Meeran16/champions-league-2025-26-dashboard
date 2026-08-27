# AI Football Analyst Architecture

## Objective

The AI Football Analyst is designed as a **grounded analytical interface**, not as a free-form chatbot.

The language model is not responsible for calculating tournament statistics. Instead, user questions are mapped to approved analytical functions that retrieve or calculate results from the validated dashboard datasets.

## Architecture

```text
User question
      |
      v
Entity resolution
(team / player / position)
      |
      v
Deterministic intent router
      |
      v
Approved analytics function
      |
      v
EvidenceResult
(answer + facts + table + scope + caveats)
      |
      +------------------------+
      | current branch         |
      v                        |
Evidence Engine UI             |
                               |
      +------------------------+
      | next stage             |
      v                        |
LLM explanation layer <--------+
      |
      v
Professional answer
+ visible supporting evidence
```

## Why this design

A direct "question -> LLM -> SQL" architecture would be easy to demonstrate but harder to trust and defend.

This project instead uses:

- a fixed set of approved analytical functions;
- explicit team/player entity resolution;
- bounded evidence payloads;
- source-scope labels;
- safe unsupported responses;
- no arbitrary SQL execution;
- no runtime web scraping.

This keeps numerical truth inside the analytics layer and reserves the future LLM for interpretation and natural-language explanation.

## Current supported analytics

### Tournament

- tournament summary
- league-phase standings
- scoring rate by stage
- top-scoring teams
- final result

### Team

- team profile
- team comparison
- league-phase form
- match history
- best home records
- best away records
- high-possession / below-median-results exploration
- lower-possession / above-median-results exploration

### Player

- top LPI candidates by position
- individual LPI profile
- same-position player comparison

## Evidence contract

Every successful query returns an `EvidenceResult` containing:

```text
question
intent
title
answer
facts[]
table[]
scope
caveats[]
followups[]
chart
```

The future language model will receive a bounded serialization of this object.

## Safety / trust rules

1. Unsupported questions do not trigger arbitrary SQL.
2. The system does not fabricate missing knockout possession or shooting data.
3. Full-competition metrics and league-phase-only detailed metrics are labelled separately.
4. Penalty-shootout scores remain separate from football scores.
5. LPI is always described as a project-defined analytical index, not an official UEFA award.
6. Cross-position LPI comparison is rejected because different position groups use different weights.
7. The future LLM will be instructed to use only the supplied evidence payload for numerical claims.

## Future stages

1. Add an LLM provider abstraction.
2. Generate concise natural-language explanations from `EvidenceResult`.
3. Add answer citations/evidence badges inside the Streamlit page.
4. Add contextual chart selection.
5. Add conversational follow-up state while keeping each turn grounded.
6. Add evaluation cases for hallucination resistance and numerical consistency.
