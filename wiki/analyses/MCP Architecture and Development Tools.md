---
type: analysis
title: "MCP Architecture and Development Tools"
analysis_type: deep-dive
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/architecture, product/tooling, ai/agents]
---

# MCP Architecture and Development Tools

## Methodology

This page records the requested MCP and development tooling additions without rewriting unrelated architecture. I checked the existing vault structure and relevant architecture/experiment docs, then filed only the newly introduced MCP/tooling information here and linked supporting stubs.

## [PRODUCTION] MCP Architecture

MCP is the AI-native development context layer. It connects coding agents to the real project memory, files, repository state, database state, and browser state so implementation and verification can be grounded in the actual environment.

### Core MCP Servers

| MCP server | Purpose | Current role |
|---|---|---|
| [[Obsidian MCP]] | Project memory | Navigate and maintain the vault knowledge base |
| [[Filesystem MCP]] | Project files and code generation | Inspect files, understand structure, and support implementation |
| [[GitHub MCP]] | Repository operations | Inspect branches, commits, pull requests, issues, and repository metadata |
| [[PostgreSQL MCP]] | Database inspection and queries | Inspect schema/data and run development SQL checks |
| [[Browser MCP]] | UI testing and browser automation | Open, test, click through, and verify frontend behavior |

### Later-Stage MCP Servers

| MCP server | Purpose | Adoption status |
|---|---|---|
| [[Docker MCP]] | Container management | [EXPERIMENTAL] Adopt when container workflows become routine |
| [[Supabase MCP]] | Backend services and storage | [EXPERIMENTAL] Adopt when Supabase inspection/operations need direct agent support |
| [[Stitch MCP]] | Frontend component generation | [EXPERIMENTAL] Adopt when component-generation workflows are proven useful |
| [[Playwright MCP]] | Frontend testing automation | [EXPERIMENTAL] Adopt when automated end-to-end testing is active |

## Development Tools

Only newly introduced tools are listed here. Existing stable stack choices remain unchanged.

| Tool | Purpose | Status |
|---|---|---|
| [[Ollama]] | Local model runtime for the product LLM | [PRODUCTION] |
| [[Qwen2.5-Coder 7B|Qwen2.5-Coder:7B]] | Primary local LLM for summaries, explanations, resume analysis, recruiter insights, and interview generation | [PRODUCTION] |
| [[Postman]] | API testing, authentication testing, API collections, and endpoint debugging | [PRODUCTION] |
| [[MCP Ecosystem]] | Agent context layer for project memory, files, repos, database, browser, and future service tooling | [PRODUCTION] core / [EXPERIMENTAL] extensions |

## Formula Lifecycle Labels

The vault should keep experimental formulas and notes, but lifecycle labels must prevent confusion:

| Label | Meaning |
|---|---|
| `[PRODUCTION]` | Accepted architecture or current implementation direction |
| `[EXPERIMENTAL]` | Research, experiments, candidate formulas, or unproven workflows |
| `[DEPRECATED]` | Superseded or rejected approaches kept for historical context |

The current production ranking formula remains deterministic and should be treated as production behavior. Alternative weights, bonus factors, and A/B-test candidates belong under experimental sections until a later decision supersedes the current ranking decision.

## Source References

- Human architecture update directive, 2026-05-29.
- Existing vault checks: `raw/architecture/mcp-context.md`, `raw/architecture/tech-stack.md`, `raw/architecture/ai-responsibilities.md`, `raw/experiments/ranking-formula-tests.md`, `raw/experiments/prompt-experiments.md`.
- Related concept: [[MCP Ecosystem]]

## Open Questions

- Which MCP servers should be installed immediately versus documented as planned only?
- Should [[PostgreSQL MCP]] and [[Supabase MCP]] default to read-only access in development?
- Should [[Postman]] collections become a required artifact for every new API sprint?
