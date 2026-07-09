---
type: entity
entity_type: product
name: "Qwen2.5-Coder:7B"
aliases: ["Qwen2.5-Coder 7B", "Qwen"]
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [ai/llm, product/architecture, product/tooling]
---

# Qwen2.5-Coder:7B

## Overview

Qwen2.5-Coder:7B is the primary local LLM documented for the AI Recruitment SaaS product.

## Key Facts

| Field | Value |
|---|---|
| Category | Local LLM |
| Runtime | [[Ollama]] |
| Status | [PRODUCTION] primary LLM |

## Relevance

Qwen2.5-Coder:7B is used for recruiter-facing summaries, candidate explanations, resume analysis, recruiter insights, and interview question generation. It must not generate candidate ranking scores, reorder candidates, override deterministic scoring, or make hiring decisions.

## Source References

- Human architecture update directive, 2026-05-29.
- [[Ollama]]
- [[MCP Architecture and Development Tools]]

## Open Questions

- What prompt and context-size constraints should be standardized for production use?
