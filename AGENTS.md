# AI Recruitment SaaS — LLM Wiki Schema

> This file governs how the LLM maintains this knowledge base. Every interaction follows these rules.

---

## Identity

This is an **LLM-maintained wiki** for building an AI-powered recruitment SaaS product. The wiki tracks competitive intelligence, market research, product strategy, technology landscape, regulatory environment, customer insights, and product decisions — everything needed to go from idea to product with a compounding knowledge base.

**The human** curates sources, directs analysis, asks questions, and makes strategic decisions.  
**The LLM** does all writing, summarizing, cross-referencing, filing, and maintenance.

---

## Directory Structure

```
/
├── AGENTS.md                  # This file — the schema (LLM + human co-evolve)
├── raw/                       # Source documents & product documentation (human-managed)
│   ├── architecture/          # System design docs (backend, frontend, AI pipeline, etc.)
│   ├── sprints/               # Sprint plans, checklists, retrospectives
│   ├── decisions/             # Architecture Decision Records (ADRs)
│   ├── ai-prompts/            # LLM prompt templates for product AI features
│   ├── database/              # Schema definitions, relationships, pgvector notes
│   ├── features/              # Feature specifications and requirements
│   ├── apis/                  # API endpoint documentation
│   ├── deployment/            # Docker, CI/CD, hosting configuration docs
│   ├── security/              # Security strategies (JWT, CSRF, rate-limiting)
│   ├── analytics/             # Analytics specs, metrics definitions
│   ├── experiments/           # AI/ML experiments (embeddings, ranking, prompts)
│   ├── backlog/               # Feature backlog, rejected ideas, technical debt
│   └── research/              # Market research, competitor analysis, risk assessments
├── wiki/                      # LLM-generated knowledge base (LLM-managed)
│   ├── index.md               # Content catalog — master directory of all pages
│   ├── log.md                 # Chronological activity log
│   ├── overview.md            # High-level synthesis — the "front page"
│   ├── sources/               # One summary page per ingested source
│   ├── entities/              # Companies, products, people, organizations
│   ├── concepts/              # Technologies, methodologies, strategies, patterns
│   ├── analyses/              # Comparisons, deep-dives, filed query results
│   └── decisions/             # Product decisions, strategic choices, trade-offs
└── .obsidian/                 # Obsidian configuration
```

### Layer Rules

| Layer | Owner | Mutability |
|-------|-------|-----------|
| `raw/` | Human | Immutable — LLM reads, never modifies |
| `wiki/` | LLM | LLM creates, updates, and maintains all files |
| `AGENTS.md` | Both | Co-evolved — human and LLM refine together |

---

## Page Types & Frontmatter

Every wiki page starts with YAML frontmatter. The LLM must always include it.

### Source Summary (`wiki/sources/`)

```yaml
---
type: source
title: "<descriptive title>"
source_file: "raw/<path to original>"
source_url: "<URL if web-sourced>"
author: "<author or org>"
date_published: YYYY-MM-DD
date_ingested: YYYY-MM-DD
tags: [<relevant tags>]
confidence: high | medium | low
---
```

Content structure:
1. **TL;DR** — 2-3 sentence summary
2. **Key Takeaways** — Bulleted list of the most important points
3. **Detailed Notes** — Organized by topic/section
4. **Connections** — Links to related wiki pages using `[[wikilinks]]`
5. **Open Questions** — What this source raises but doesn't answer

### Entity Page (`wiki/entities/`)

```yaml
---
type: entity
entity_type: company | product | person | organization
name: "<entity name>"
aliases: ["<alt names>"]
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
source_count: <number of sources referencing this entity>
tags: [<relevant tags>]
---
```

Content structure:
1. **Overview** — What this entity is, why it matters
2. **Key Facts** — Structured data (founding date, HQ, funding, etc.)
3. **Relevance** — How this relates to our AI recruitment SaaS
4. **Source References** — Which sources mention this entity
5. **Open Questions** — What we don't know yet

### Concept Page (`wiki/concepts/`)

```yaml
---
type: concept
name: "<concept name>"
aliases: ["<alt names>"]
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
source_count: <number>
tags: [<relevant tags>]
---
```

Content structure:
1. **Definition** — Clear explanation of the concept
2. **Relevance to AI Recruitment** — Why this matters for our product
3. **Current State** — What the landscape looks like today
4. **Key Players** — Who's using or advancing this
5. **Our Position** — Where we stand or should stand
6. **Source References**
7. **Open Questions**

### Analysis Page (`wiki/analyses/`)

```yaml
---
type: analysis
title: "<descriptive title>"
analysis_type: comparison | deep-dive | market-map | swot | framework
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
source_count: <number>
tags: [<relevant tags>]
---
```

Free-form but must include a **Methodology** section and **Source References**.

### Decision Page (`wiki/decisions/`)

```yaml
---
type: decision
title: "<decision title>"
status: proposed | decided | revisiting | superseded
date_created: YYYY-MM-DD
date_decided: YYYY-MM-DD
superseded_by: "[[link]]"
tags: [<relevant tags>]
---
```

Content structure:
1. **Context** — Why this decision was needed
2. **Options Considered** — Each option with pros/cons
3. **Decision** — What was chosen and why
4. **Implications** — What follows from this decision
5. **Review Triggers** — Conditions that should prompt revisiting

---

## Wikilink Conventions

- Use `[[Page Name]]` for all cross-references (Obsidian-native)
- Use `[[Page Name|display text]]` when the page name is awkward in prose
- Every entity, concept, and source mentioned in a page should be linked
- Prefer linking to existing pages over creating new ones unless the topic warrants its own page
- When a link target doesn't exist yet, create it (even as a stub) during the same operation

---

## Tags

Use hierarchical tags in frontmatter. Core tag taxonomy:

```
recruitment/          # Core domain
  recruitment/sourcing
  recruitment/screening
  recruitment/matching
  recruitment/assessment
  recruitment/onboarding
  recruitment/analytics

ai/                   # Technology
  ai/nlp
  ai/llm
  ai/ml
  ai/computer-vision
  ai/recommendation
  ai/agents

market/               # Business
  market/competitor
  market/trend
  market/regulation
  market/pricing
  market/segment
  market/funding

product/              # Product
  product/feature
  product/ux
  product/integration
  product/architecture
  product/strategy

research/             # Research
  research/academic
  research/industry-report
  research/case-study
```

Tags can be extended as needed. New tags should follow the `category/subcategory` pattern.

---

## Operations

### 1. Ingest

**Trigger:** Human drops a source into `raw/` and says "ingest" (or similar).

**Workflow:**

1. **Read** the source document completely
2. **Discuss** key takeaways with the human (unless batch mode)
3. **Create** a source summary page in `wiki/sources/`
4. **Create or update** entity pages for every notable entity mentioned
5. **Create or update** concept pages for every notable concept
6. **Update** `wiki/overview.md` if the source materially changes the big picture
7. **Update** `wiki/index.md` with entries for all new/modified pages
8. **Append** to `wiki/log.md` with a structured entry
9. **Report** a summary of all changes made

**Quality checks during ingest:**
- Flag contradictions with existing wiki content
- Note where this source strengthens or challenges existing claims
- Identify gaps: "This source mentions X but we have no page for it yet"

### 2. Query

**Trigger:** Human asks a question.

**Workflow:**

1. **Read** `wiki/index.md` to find relevant pages
2. **Read** the relevant wiki pages (not raw sources, unless needed for verification)
3. **Synthesize** an answer with `[[wikilink]]` citations to wiki pages
4. **Offer to file**: If the answer is substantive, ask "Should I file this as an analysis page?"
5. If filed: create the page in `wiki/analyses/`, update index and log

### 3. Lint

**Trigger:** Human says "lint" or "health check" (or periodically suggested by LLM).

**Checks to perform:**
- [ ] Orphan pages (no inbound links)
- [ ] Dead links (wikilinks pointing to non-existent pages)
- [ ] Stale pages (not updated despite newer contradicting sources)
- [ ] Missing pages (concepts/entities mentioned but lacking pages)
- [ ] Frontmatter completeness
- [ ] Tag consistency
- [ ] Index completeness (all pages listed?)
- [ ] Contradictions between pages

**Output:** A lint report with specific issues and suggested fixes. Ask human before applying fixes.

### 4. Maintain

**Trigger:** Any time the LLM touches the wiki.

**Always:**
- Keep `wiki/index.md` current
- Keep `wiki/log.md` current
- Ensure all new entities/concepts get pages (at minimum stubs)
- Maintain wikilinks between related pages
- Update `date_updated` in frontmatter of modified pages
- Update `source_count` when new sources reference an entity/concept

---

## Index Format (`wiki/index.md`)

```markdown
# Wiki Index

> Last updated: YYYY-MM-DD | Total pages: N | Total sources: N

## Sources
| Page | Source | Date Ingested | Tags |
|------|--------|--------------|------|
| [[Source Title]] | author/org | YYYY-MM-DD | tags |

## Entities
| Page | Type | Source Count | Tags |
|------|------|-------------|------|
| [[Entity Name]] | company/product/person | N | tags |

## Concepts
| Page | Source Count | Tags |
|------|-------------|------|
| [[Concept Name]] | N | tags |

## Analyses
| Page | Type | Date | Tags |
|------|------|------|------|
| [[Analysis Title]] | comparison/deep-dive | YYYY-MM-DD | tags |

## Decisions
| Page | Status | Date | Tags |
|------|--------|------|------|
| [[Decision Title]] | decided/proposed | YYYY-MM-DD | tags |
```

---

## Log Format (`wiki/log.md`)

```markdown
## [YYYY-MM-DD HH:MM] <operation> | <title>

<brief description of what was done>

**Pages touched:** [[Page1]], [[Page2]], ...
```

Operations: `ingest`, `query`, `lint`, `update`, `decision`, `structure`, `init`

---

## Interaction Protocol

Every conversation follows this pattern:

1. **Determine operation type** (ingest / query / lint / maintain / other)
2. **Execute the operation** per the workflows above
3. **Update index and log**
4. **Summarize changes** to the human

If the human's request doesn't map to a defined operation, the LLM should still:
- Answer the question
- Consider whether the answer should be filed in the wiki
- Suggest related explorations

---

## Evolution

This schema is a living document. When the human or LLM identifies a pattern that should be codified:
1. Propose the change
2. Get human approval
3. Update this file
4. Log the schema change

Current version: **2.0 — Product-oriented raw structure**  
Domain: **AI Recruitment SaaS**  
Created: **2025-05-22**  
Updated: **2026-05-22**
