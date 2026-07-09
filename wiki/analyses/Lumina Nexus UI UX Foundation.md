---
type: analysis
title: "Lumina Nexus UI UX Foundation"
analysis_type: framework
date_created: 2026-05-29
date_updated: 2026-05-29
source_count: 0
tags: [product/ux, product/design-system, product/strategy, recruitment/screening, recruitment/analytics, ai/llm]
---

# Lumina Nexus UI UX Foundation

## Methodology

This framework translates the requested "Lumina Nexus" theme into a practical product design system for the AI Recruitment SaaS. It is grounded in the existing [[Hybrid Ranking System]], [[Qwen2.5-Coder 7B]], [[Ollama]], [[Semantic Search]], [[Pipeline Board]], [[Candidate Dashboard]], and [[AI Hiring Regulations]] pages.

Prompt corrections applied:

- "usrself" is interpreted as "yourself."
- "Professional cards" is applied to repeated objects and contained tool panels, not to every page section.
- The recruiter portal is desktop-optimized; the candidate portal is mobile-first and responsive.
- AI explanations are visually separated from deterministic scores to preserve the "Math decides. AI explains." architecture.

## Product Identity

[[Lumina Nexus]] is a conservative enterprise SaaS visual foundation for HR teams, recruiters, and hiring managers. The product should feel calm, trustworthy, fast, and evidence-driven.

Core attributes:

- Minimalist interface with high information density
- Neutral dashboard surfaces with clear hierarchy
- Strong support for tables, filters, comparison views, and status tracking
- AI presented as an assistant layer, not as the decision-maker
- No glassmorphism, neon effects, cyberpunk motifs, or decorative motion

## Design System

### Design Principles

| Principle | Product Meaning | UI Implication |
|---|---|---|
| Recruiter first | Recruiters need speed and density | Persistent filters, batch actions, compact tables, keyboard-friendly search |
| Candidate transparency | Candidates should always know status | Clear status timeline, no vague AI language, obvious next steps |
| Math decides | Rankings must remain deterministic | Scores and ranking controls are not editable by LLM output |
| AI explains | AI provides context, not authority | AI panels use explanation labels and cite underlying evidence |
| Enterprise calm | The product handles serious workflows | Conservative color, restrained motion, predictable layouts |

### Visual Language

- Page backgrounds: soft slate-tinted off-white using `#F8FAFC`
- Primary actions: blue `#3B82F6`
- Text: dark navy `#0F172A`
- Secondary controls: slate `#475569`
- Corners: rounded, but restrained; use `6px` to `10px`
- Shadows: soft and shallow; avoid floating/glass effects
- Data density: use compact but readable rows, especially in recruiter workflows

## Color Tokens

### Core Tokens

| Token | Value | Use |
|---|---:|---|
| `color.primary.50` | `#EFF6FF` | Primary light background |
| `color.primary.100` | `#DBEAFE` | Primary subtle fills |
| `color.primary.500` | `#3B82F6` | Primary buttons, links, focused states |
| `color.primary.600` | `#2563EB` | Primary hover |
| `color.primary.700` | `#1D4ED8` | Primary active |
| `color.secondary.500` | `#475569` | Secondary text and controls |
| `color.tertiary.50` | `#F8FAFC` | App background |
| `color.neutral.900` | `#0F172A` | Primary text |

### Neutral Scale

| Token | Value | Use |
|---|---:|---|
| `color.neutral.0` | `#FFFFFF` | Cards, sheets, table bodies |
| `color.neutral.50` | `#F8FAFC` | App background |
| `color.neutral.100` | `#F1F5F9` | Subtle surface |
| `color.neutral.200` | `#E2E8F0` | Borders |
| `color.neutral.300` | `#CBD5E1` | Disabled borders |
| `color.neutral.500` | `#64748B` | Muted text |
| `color.neutral.600` | `#475569` | Secondary text |
| `color.neutral.700` | `#334155` | Strong secondary text |
| `color.neutral.900` | `#0F172A` | Primary text |

### Semantic Tokens

| Token | Value | Use |
|---|---:|---|
| `color.success.600` | `#16A34A` | Hired, positive trend, passed validation |
| `color.warning.600` | `#D97706` | Needs review, incomplete profile |
| `color.danger.600` | `#DC2626` | Rejected, destructive actions, failed checks |
| `color.info.600` | `#2563EB` | Applied, under review, neutral AI insight |
| `color.purple.600` | `#7C3AED` | AI insight accent, used sparingly |

### Status Colors

| Status | Text | Background | Border |
|---|---:|---:|---:|
| Applied | `#2563EB` | `#EFF6FF` | `#BFDBFE` |
| Under Review / Screening | `#475569` | `#F1F5F9` | `#CBD5E1` |
| Shortlisted | `#7C3AED` | `#F5F3FF` | `#DDD6FE` |
| Technical Round | `#0891B2` | `#ECFEFF` | `#A5F3FC` |
| HR Round | `#4F46E5` | `#EEF2FF` | `#C7D2FE` |
| Offer | `#D97706` | `#FFFBEB` | `#FDE68A` |
| Hired | `#16A34A` | `#F0FDF4` | `#BBF7D0` |
| Rejected | `#DC2626` | `#FEF2F2` | `#FECACA` |

### Score Colors

| Score Range | Meaning | Color |
|---|---|---:|
| 80-100 | Strong match | `#16A34A` |
| 60-79 | Reviewable match | `#D97706` |
| 0-59 | Weak match | `#DC2626` |

## Typography Scale

Font family: Inter, with system fallback `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.

| Token | Size | Line Height | Weight | Use |
|---|---:|---:|---:|---|
| `text.display` | 32px | 40px | 700 | Rare app-level titles |
| `text.h1` | 28px | 36px | 700 | Page title |
| `text.h2` | 22px | 30px | 650 | Major section title |
| `text.h3` | 18px | 26px | 650 | Panel title |
| `text.body` | 14px | 22px | 400 | Default UI copy |
| `text.body-strong` | 14px | 22px | 600 | Table labels, card titles |
| `text.small` | 13px | 20px | 400 | Secondary metadata |
| `text.caption` | 12px | 18px | 500 | Badges, helper text |
| `text.metric` | 30px | 36px | 700 | Dashboard metrics |

Typography rules:

- Use tabular numbers for metrics and scores.
- Keep letter spacing at `0`.
- Avoid paragraph-heavy dashboard views.
- Prefer sentence case for labels and buttons.

## Spacing System

Use a 4px base grid.

| Token | Value | Use |
|---|---:|---|
| `space.1` | 4px | Tight icon/text gap |
| `space.2` | 8px | Button icon gap, compact fields |
| `space.3` | 12px | Compact padding |
| `space.4` | 16px | Standard padding |
| `space.5` | 20px | Panel spacing |
| `space.6` | 24px | Page section spacing |
| `space.8` | 32px | Page group spacing |
| `space.10` | 40px | Large vertical separation |
| `space.12` | 48px | Major layout spacing |

Layout constants:

- Recruiter sidebar width: `264px`
- Recruiter topbar height: `64px`
- Candidate mobile bottom nav height: `64px`
- Page max width for recruiter forms: `960px`
- Page max width for candidate content: `1120px`
- Table row height: `48px` compact, `56px` standard
- Kanban column width: `320px`

## Component Library

### Foundations

| Component | Description | Notes |
|---|---|---|
| App shell | Sidebar, topbar, content region | Recruiter portal only |
| Candidate shell | Header, mobile bottom nav, content region | Candidate portal |
| Page header | Title, subtitle, primary action, secondary actions | No oversized hero treatment |
| Breadcrumbs | Context navigation | Use in deep recruiter pages |
| Empty state | Title, brief text, primary action | No decorative illustrations required |
| Skeleton | Loading placeholder | Match final layout dimensions |

### Inputs and Controls

| Component | Variants | Requirements |
|---|---|---|
| Button | Primary, secondary, ghost, danger, icon-only | 40px default height, 32px compact |
| Text input | Default, search, error, disabled | Clear focus ring in primary blue |
| Textarea | Default, error | Used for job descriptions and notes |
| Select | Single, multi-select | Searchable for long lists |
| Checkbox | Default, indeterminate | Bulk selection in tables |
| Toggle | On/off | Permissions and notification settings |
| Slider | Score range | Used in candidate filters |
| Date picker | Single, range | Analytics and job filters |
| Command search | Global search and semantic search | `Ctrl+K` / `Cmd+K` compatible |

### Data Components

| Component | Use |
|---|---|
| Metric card | KPI title, value, trend, comparison period |
| Data table | Candidates, jobs, recruiters, permissions |
| Sortable table header | Ranking and analytics views |
| Filter bar | Jobs, candidates, analytics |
| Badge | Status, score, role, source |
| Progress bar | Profile completion, funnel progress |
| Score breakdown | Deterministic sub-score display |
| Chart container | Funnel, line, bar, histogram |
| Timeline | Candidate status and activity history |

### Recruitment Components

| Component | Use |
|---|---|
| Job card | Compact job summary in job list |
| Job editor | Create/edit job form with sections |
| Candidate row | Dense row for candidates table |
| Candidate card | Kanban card and compact profile summary |
| Resume viewer | PDF/document viewer with parsed sections |
| AI insight panel | LLM-generated summaries and recommendations |
| Pipeline column | Kanban stage column |
| Comparison matrix | Side-by-side candidate comparison |
| Skill matrix | Skill match across candidates |
| Application tracker | Candidate-facing status timeline |

### AI Components

AI components must visibly separate evidence from generated text.

| Component | Use | Constraint |
|---|---|---|
| AI summary card | Candidate summary | Must not include ranking controls |
| AI insight callout | Recruiter insight | Label as generated explanation |
| Interview question set | Suggested interview questions | Recruiter can edit before use |
| Score explanation | Explains sub-scores | Cannot change score values |
| Evidence list | Skills, resume excerpts, job requirements | Must remain source-backed |

## Navigation Architecture

### Recruiter Portal

Primary desktop sidebar:

1. Dashboard
2. Jobs
3. Candidates
4. Pipeline
5. Compare
6. Analytics
7. Settings

Topbar:

- Organization switcher
- Global search
- Notifications
- Help
- User menu

Recommended route structure:

| Route | Page |
|---|---|
| `/dashboard` | Hiring overview |
| `/jobs` | Jobs list |
| `/jobs/new` | Create job |
| `/jobs/[id]` | Job detail |
| `/jobs/[id]/edit` | Edit job |
| `/candidates` | Candidate list and semantic search |
| `/candidates/[id]` | Candidate profile |
| `/pipeline` | Cross-job pipeline selector |
| `/pipeline/[jobId]` | Job-specific pipeline board |
| `/compare` | Candidate comparison launcher |
| `/compare?candidateIds=` | Candidate comparison |
| `/analytics` | Hiring analytics |
| `/settings` | Organization settings |
| `/settings/recruiters` | Recruiter management |
| `/settings/permissions` | Permissions |

### Candidate Portal

Primary mobile-first navigation:

1. Home
2. Jobs
3. Applications
4. Profile
5. Notifications

Recommended route structure:

| Route | Page |
|---|---|
| `/candidate/signup` | Candidate signup |
| `/candidate/login` | Candidate login |
| `/candidate/dashboard` | Candidate dashboard |
| `/candidate/jobs` | Job listings |
| `/candidate/jobs/[id]` | Job details |
| `/candidate/applications` | Application tracking |
| `/candidate/profile` | Profile, resume, skills, experience |
| `/candidate/notifications` | Notifications |

## Recruiter Portal Wireframes

### Recruiter Dashboard

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Sidebar        │ Topbar: Org switcher | Search | Notifications | User      │
│                ├───────────────────────────────────────────────────────────┤
│ Dashboard      │ Hiring Overview                         [Create job]      │
│ Jobs           │                                                           │
│ Candidates     │ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────┐ │
│ Pipeline       │ │ Open jobs  │ │ Candidates │ │ Time hire  │ │ Offers  │ │
│ Compare        │ └────────────┘ └────────────┘ └────────────┘ └─────────┘ │
│ Analytics      │                                                           │
│ Settings       │ ┌──────────────────────────────┐ ┌──────────────────────┐ │
│                │ │ Hiring funnel                │ │ AI insights          │ │
│                │ │ Applied > Screening > Offer  │ │ Bottlenecks, alerts  │ │
│                │ └──────────────────────────────┘ └──────────────────────┘ │
│                │ ┌───────────────────────────────────────────────────────┐ │
│                │ │ Active jobs table                                      │ │
│                │ └───────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### Jobs

```
Page header: Jobs                                      [Create job]
Filter bar: Search | Status | Department | Recruiter | Date

Table columns:
Job title | Status | Department | Candidates | Avg score | Pipeline | Updated | Actions

Row actions:
View | Edit | Publish/Unpublish | Archive
```

### Candidates

```
Page header: Candidates
Primary controls: Keyword search | Semantic search | Job | Stage | Score range | Source

Main area:
Candidate table with dense rows:
Name | Applied role | Stage | Score | Skills | Source | Last activity | Actions

Side panel:
Saved filters | Recent semantic queries | Bulk actions
```

## Candidate Portal Wireframes

### Authentication

```
┌──────────────────────────────┐
│ Lumina Nexus                 │
│ Create your candidate profile│
│ Email                        │
│ Password                     │
│ [Create account]             │
│ Already have an account?     │
└──────────────────────────────┘
```

Rules:

- Keep forms short.
- Use clear error states.
- Do not show marketing-heavy content in the auth flow.

### Candidate Dashboard

```
Header: Lumina Nexus | Notifications | Profile

┌─────────────────────────────────────────┐
│ Profile completion: 72%                 │
│ [Complete profile]                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Applications                            │
│ Product Designer    Under Review        │
│ Backend Engineer    Technical Round     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Next actions                            │
│ Upload resume | Add skills | Confirm availability │
└─────────────────────────────────────────┘
```

## Dashboard Layouts

### Recruiter Dashboard Layout

Priority order:

1. KPI row: open jobs, active candidates, shortlisted, average time-to-hire
2. Funnel chart: applied to hired conversion
3. AI insights: bottlenecks, unusual score distribution, aging candidates
4. Active jobs table
5. Recent candidate activity

Layout:

- Desktop: `12-column grid`
- KPI cards: four cards across
- Main chart: 8 columns
- AI insights: 4 columns
- Tables: full width

### Candidate Dashboard Layout

Priority order:

1. Current application status
2. Profile completion
3. Active applications
4. Notifications and next steps
5. Recommended jobs

Layout:

- Mobile: single column
- Tablet/desktop: two columns, status and profile in left, applications in right

## Pipeline Board Layout

Stages:

1. Applied
2. Screening
3. Technical
4. HR
5. Offer
6. Hired
7. Rejected

Board structure:

```
Header: Pipeline | Job selector | Search | Filters | Bulk actions

┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ Applied    │ │ Screening  │ │ Technical  │ │ HR         │
│ 34         │ │ 18         │ │ 9          │ │ 5          │
│ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │ │ ┌────────┐ │
│ │Card    │ │ │ │Card    │ │ │ │Card    │ │ │ │Card    │ │
│ └────────┘ │ │ └────────┘ │ │ └────────┘ │ │ └────────┘ │
└────────────┘ └────────────┘ └────────────┘ └────────────┘
```

Candidate card content:

- Name
- Current title
- Overall score
- Top two matching skills
- Days in stage
- Quick actions: view, note, schedule, reject

Interaction rules:

- Drag and drop only changes pipeline stage after server confirmation.
- Rejected transitions require a reason.
- Hired transitions require confirmation.
- Ranking within a stage is score-sorted by default and cannot be reordered by LLM output.

## Candidate Profile Layout

Desktop layout:

```
Header:
Candidate name | Current title | Stage | Score | Actions

Left column:
- Score breakdown
- Contact
- Applied job
- Action buttons

Center column:
- Resume viewer
- Parsed resume sections
- Skills and experience

Right column:
- AI summary
- Strengths
- Weaknesses
- Interview recommendations
- Pipeline timeline
```

AI guardrails:

- The score block always shows `semantic_similarity`, `skill_match`, and `experience_match`.
- AI summary appears below or beside the deterministic score, never replacing it.
- Weaknesses should be framed as "risks or gaps to verify," not final judgments.
- Interview recommendations must be editable and recruiter-approved.

## Candidate Comparison Layout

```
Header: Compare candidates | Job context selector | Export

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Criteria     │ Candidate A  │ Candidate B  │ Candidate C  │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Overall      │ 86           │ 78           │ 72           │
│ Semantic     │ 91           │ 80           │ 77           │
│ Skills       │ 82           │ 76           │ 70           │
│ Experience   │ 81           │ 75           │ 66           │
│ Must-haves   │ 5/6          │ 4/6          │ 4/6          │
│ Top skills   │ Python, AWS  │ Python, SQL  │ React, Node  │
│ AI notes     │ Summary      │ Summary      │ Summary      │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

Comparison rules:

- Compare two to four candidates at once.
- The deterministic score order remains fixed unless the recruiter changes the sort criterion.
- Skill comparison should show must-have, preferred, missing, and inferred skills.
- AI notes are explanations only and must not be used as hidden ranking factors.

## Job Listing Layout

### Recruiter Jobs List

```
Header: Jobs | [Create job]
Filter row: Search | Status | Department | Published | Archived
Table:
Title | Status | Applicants | Avg score | Hiring manager | Created | Actions
```

Job status actions:

- Draft: edit, publish, archive
- Published: edit, unpublish, archive
- Archived: restore, view

### Candidate Job Listings

```
Header: Browse jobs
Search: Role, skill, keyword
Filters: Department | Location | Remote | Experience | Employment type

Job card:
Title
Department | Location | Type
Short description
Requirement chips
[View details]
```

### Job Details

```
Title | Department | Location | Type
[Apply]

Sections:
- Overview
- Responsibilities
- Requirements
- Preferred qualifications
- Hiring process
- Candidate transparency note
```

Candidate-facing requirements:

- Use clear language and avoid inflated qualifications.
- Show the hiring process stages.
- Show application status after applying.

## Application Tracking Layout

Candidate statuses:

1. Applied
2. Under Review
3. Shortlisted
4. Technical Round
5. HR Round
6. Offer
7. Rejected
8. Hired

Mobile-first timeline:

```
Application: Backend Engineer
Current status: Technical Round

Applied        Complete
Under Review   Complete
Shortlisted    Complete
Technical      Current
HR Round       Upcoming
Offer          Upcoming
```

Transparency rules:

- Always show the current status.
- Always show the last status update date.
- If rejected, show a respectful final state and any human-approved feedback policy.
- Do not expose internal score values to candidates unless explicitly approved as a product policy.

## Accessibility

Minimum requirements:

- WCAG AA contrast for text and controls
- Keyboard access for tables, filters, modals, and Kanban actions
- Visible focus ring using `#3B82F6`
- No color-only status indicators
- Chart data available in tabular form
- AI-generated text labeled clearly
- Destructive actions require confirmation

## Performance UX

Recruiter portal:

- Load dashboard shell immediately with skeletons.
- Keep filters in URL query params.
- Use virtualized tables for 500+ candidates.
- Debounce semantic search at 300ms.
- Preserve scroll and filter state when returning from profile pages.

Candidate portal:

- Mobile pages should be fast on mid-range devices.
- Application status should render before secondary recommendations.
- Resume upload should show progress and clear error recovery.

## Source References

- [[Hybrid Ranking System]]
- [[Qwen2.5-Coder 7B]]
- [[Ollama]]
- [[Semantic Search]]
- [[Pipeline Board]]
- [[Candidate Dashboard]]
- [[AI Hiring Regulations]]

## Open Questions

- Should candidates ever see their AI-derived match score, or only qualitative status?
- Should recruiter dashboards support custom layouts in MVP, or remain fixed until analytics matures?
- Which candidate-facing feedback policy is legally safest across target markets?
- Should design tokens be implemented directly in Tailwind config or generated from a token JSON file?
