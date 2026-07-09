---
type: concept
name: "MCP Ecosystem"
aliases: ["Model Context Protocol", "MCP"]
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/architecture, ai/agents, product/tooling]
---

# MCP Ecosystem

## Definition

The MCP ecosystem is the project context layer that lets AI coding agents connect to approved tools, files, repositories, databases, browser sessions, and service backends through Model Context Protocol servers.

## Relevance to AI Recruitment

For the AI Recruitment SaaS, MCP is development infrastructure rather than product runtime logic. It supports project memory, implementation work, API/database inspection, browser validation, and later-stage frontend and deployment automation.

## Current State

### [PRODUCTION] Core MCP Servers

| MCP server | Purpose |
|---|---|
| [[Obsidian MCP]] | Project memory and vault navigation |
| [[Filesystem MCP]] | Project file access and code generation support |
| [[GitHub MCP]] | Repository operations |
| [[PostgreSQL MCP]] | Database inspection and SQL queries |
| [[Browser MCP]] | UI testing and browser automation |

### [EXPERIMENTAL] Later-Stage MCP Servers

| MCP server | Purpose |
|---|---|
| [[Docker MCP]] | Container management |
| [[Supabase MCP]] | Backend services and storage inspection |
| [[Stitch MCP]] | Frontend component generation |
| [[Playwright MCP]] | Frontend testing automation |

## Key Players

- [[Obsidian MCP]]
- [[Filesystem MCP]]
- [[GitHub MCP]]
- [[PostgreSQL MCP]]
- [[Browser MCP]]
- [[Docker MCP]]
- [[Supabase MCP]]
- [[Stitch MCP]]
- [[Playwright MCP]]

## Our Position

Use core MCP servers to make AI-assisted development more grounded in the actual vault, codebase, repository state, database state, and UI behavior. Treat later-stage MCP servers as optional extensions to adopt when the product needs heavier deployment, backend service, component-generation, or test automation workflows.

## Source References

- Human architecture update directive, 2026-05-29.
- [[MCP Architecture and Development Tools]]

## Open Questions

- Which MCP servers are available in the final local development environment?
- What permission boundaries should each MCP server have?
- Should database and browser MCP access be read-only by default during routine development?
