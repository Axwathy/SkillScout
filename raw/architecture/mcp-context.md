---
type: architecture
title: "MCP & AI-Native Workflow"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, ai/agents]
---

# [PRODUCTION] MCP / AI-Native Workflow

This project utilizes a modern AI-native engineering workflow.

- **Obsidian:** Project memory (the `raw/` and `wiki/` structure)
- **Claude:** Architecture reasoning and high-level design
- **Codex/Cursor:** Implementation and code generation
- **MCP (Model Context Protocol):** Context retrieval to connect the agent to the actual environment, files, and state.

## Primary Product LLM

The product's primary local LLM is **Qwen2.5-Coder:7B via Ollama**.

Fallback models:
- Mistral
- Phi-3

Qwen is used for structured resume analysis, recruiter-facing summaries, candidate insight generation, and interview question generation. It is not used for embeddings, deterministic scoring, ranking, final hiring decisions, or production-critical ordering logic.

## Architecture Rule

Math decides. AI explains.

- `BAAI/bge-small-en-v1.5` generates embeddings for vector search and candidate-job similarity.
- The hybrid scoring engine computes rankings using semantic similarity, skill match, and experience match.
- Qwen2.5-Coder:7B explains computed scores and generates recruiter context.
- The LLM cannot override scores, reorder candidates, alter the hybrid score, or make hiring decisions.

## Related Documents

- [[ai-responsibilities|AI Responsibilities]]
- [[ai-pipeline|AI Pipeline]]
- [[semantic-matching|Semantic Matching]]
