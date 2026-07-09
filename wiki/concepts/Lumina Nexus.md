---
type: concept
name: "Lumina Nexus"
aliases: ["Lumina Nexus Design System", "Lumina Nexus UI", "Lumina Nexus Theme"]
date_created: 2026-05-29
date_updated: 2026-05-30
source_count: 0
tags: [product/ux, product/design-system]
---

# Lumina Nexus

> ⚠️ **Clarification:** Lumina Nexus is a **color and design theme**, not the product name. The product is currently referred to as **RecruitAI** (placeholder) until an official product name is decided. See [[wiki/decisions/]] for any naming decisions.

## Definition

Lumina Nexus is the visual and interaction design system (color palette, typography, spacing, and component style) for the AI Recruitment SaaS platform. It defines a professional, enterprise-grade light UI with the following core tokens:

| Token | Value | Use |
|-------|-------|-----|
| Primary | `#3B82F6` | Actions, links, focus |
| Secondary | `#475569` | Supporting text, icons |
| Background | `#F8FAFC` | Page and panel backgrounds |
| Text | `#0F172A` | Body and headings |
| Border | `#E2E8F0` | Dividers, card edges |

The theme intentionally avoids: neon colors, glassmorphism, dark mode (MVP), cyberpunk aesthetics, or glow effects.

## Relevance to AI Recruitment

Recruitment software must support fast candidate review, auditable scoring, clear pipeline movement, and candidate-facing transparency. The Lumina Nexus theme gives those workflows a calm, data-focused interface that feels trustworthy and professional to HR teams and hiring managers.

## Current State

The foundation is defined in [[Lumina Nexus UI UX Foundation]]. It includes color tokens, typography, spacing, components, navigation, recruiter wireframes, candidate wireframes, dashboard layouts, pipeline board layout, candidate profile layout, comparison layout, job listing layout, and application tracking layout.

In code, the theme is implemented in `frontend/tailwind.config.ts` and `frontend/styles/globals.css`.

## Our Position

Use Lumina Nexus as the default UI design system for MVP implementation. It should remain professional, conservative, accessible, and data-focused. The product name displayed in the UI is **RecruitAI** (placeholder) — Lumina Nexus is never exposed as a brand name to end users.

## Source References

- [[Lumina Nexus UI UX Foundation]]
- [[Hybrid Ranking System]]
- [[Candidate Dashboard]]
- [[Pipeline Board]]

## Open Questions

- Should Lumina Nexus define token slots for a future dark theme, or remain light-only for MVP?
- What is the final product name that replaces the "RecruitAI" placeholder?
