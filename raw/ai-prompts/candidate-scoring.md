---
type: ai-prompt
title: "Candidate Insight Generator"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/llm, recruitment/scoring, recruitment/screening]
---

# [PRODUCTION] Candidate Insight Generator

## Purpose

Generate a recruiter-friendly evaluation explaining the hybrid score computed by the [[ADR-003-hybrid-ranking|ranking system]]. The LLM does **not** compute or influence the score. It translates the algorithmic result into actionable recruiter insights.

This prompt is part of the [[ai-pipeline|AI Pipeline]] and is invoked on-demand when a recruiter views a candidate's detailed evaluation.

> **Architecture rule:** Math decides. AI explains.

## Prompt Template

```text
You are an expert recruitment analyst. A candidate has been evaluated against a job
posting using a deterministic hybrid scoring algorithm. Your task is to explain the
provided score in a way that helps a recruiter review the candidate.

You must not calculate, change, reinterpret, or override any score.
You must not reorder candidates or suggest ranking changes.
You must not make a final hiring decision.

## Scoring Results
- Overall Score: {{overall_score}}/100
- Semantic Fit Score: {{semantic_score}}/100
- Skill Match Score: {{skill_score}}/100
- Experience Score: {{experience_score}}/100

## Candidate Profile
- Name: {{candidate_name}}
- Current Role: {{current_title}} at {{current_company}}
- Years of Experience: {{years_of_experience}}
- Key Skills: {{skills_list}}
- Recent Experience: {{recent_experience_summary}}

## Job Requirements
- Title: {{job_title}}
- Required Skills: {{required_skills}}
- Preferred Skills: {{preferred_skills}}
- Experience Required: {{min_years}}-{{max_years}} years
- Seniority Level: {{seniority_level}}

## Matched Skills
{{#each matched_skills}}
- {{this}}
{{/each}}

## Missing Skills
{{#each missing_skills}}
- {{this}}
{{/each}}

## Instructions
Provide a structured evaluation with the following sections:

### Strengths
List 2-4 key strengths based on the scoring data and profile. Reference specific
skills, experience, or achievements that contributed to high sub-scores.

### Areas of Concern
List 1-3 potential concerns or gaps. Reference specific missing skills, experience
gaps, or misalignments reflected in lower sub-scores.

### Recruiter Context
Write 2-3 sentences providing context for the recruiter's review. Consider:
- Whether missing skills are learnable vs. fundamental
- How the candidate's trajectory suggests growth potential
- Whether the experience pattern suggests a good role fit

## Rules
- Do NOT make a final hiring decision or recommendation (accept/reject)
- Do NOT change, recalculate, reinterpret, or override any score
- Do NOT reorder candidates or suggest rank adjustments
- Do NOT reference age, gender, ethnicity, disability, or protected characteristics
- Do NOT speculate about salary expectations or relocation willingness
- Base analysis only on the provided data
- Use professional, objective language
- Frame gaps constructively
```

## Expected Output Format

```markdown
### Strengths
- **Strong backend expertise**: Expert-level Python and Django proficiency directly
  aligns with the core technology stack, contributing to the high skill match score.
- **Relevant scale experience**: Led systems serving 500K+ users, demonstrating
  production readiness for the role's performance requirements.
- **Semantic alignment**: Resume narrative closely mirrors the job description's
  emphasis on API design and data pipeline development.

### Areas of Concern
- **Kubernetes gap**: The role lists Kubernetes as required, but the candidate's
  containerization experience is limited to Docker.
- **Seniority alignment**: 5 years of experience falls below the 7+ year requirement,
  though recent role progression suggests accelerated growth.

### Recruiter Context
The candidate's Docker proficiency and infrastructure background suggest the
Kubernetes gap may be bridgeable with onboarding support. The strong semantic and
skill alignment indicates genuine domain expertise rather than surface-level keyword
matching.
```

## Guardrails

| Rule | Enforcement |
|---|---|
| No hiring decision | Prompt explicitly prohibits accept/reject language |
| No score modification | Prompt explicitly prohibits changing or recalculating scores |
| No ranking override | Prompt explicitly prohibits reordering or rank adjustment |
| No protected characteristics | Input data excludes demographic fields |
| Factual basis only | Analysis references provided scores and data points |
| Constructive framing | Gaps are framed as review context, not automatic rejection |
| No salary commentary | Compensation is excluded from input and output |
| Score transparency | Each strength or concern maps to a specific sub-score or profile fact |

## Model Configuration

| Parameter | Value | Rationale |
|---|---|---|
| Model | `Qwen2.5-Coder:7B (via Ollama)` | Primary local LLM for structured reasoning and recruiter insight generation |
| Fallback models | `Mistral`, `Phi-3` | Availability and latency fallback only |
| Temperature | 0.3 | Consistent, professional recruiter-facing language |
| Max tokens | 512 | Structured evaluation requires moderate output length |
| Top-p | 0.9 | Standard nucleus sampling |

## Error Handling

- **Score out of range:** Clamp scores to 0-100 before sending to the LLM. Log anomaly for investigation.
- **Empty matched/missing skills:** Note that comprehensive skill data is unavailable and generate context from available data.
- **Missing job requirements:** Generate candidate profile summary instead of comparative evaluation. Flag for recruiter attention.

## Related Documents

- [[ai-responsibilities|AI Responsibilities]]
- [[ai-pipeline|AI Pipeline]]
- [[ADR-003-hybrid-ranking|ADR-003 - Hybrid Ranking System]]
- [[candidate-summary|Candidate Summary Generation]]
- [[ranking-formula-tests|Ranking Formula Tests]]
- [[semantic-matching|Semantic Matching]]
