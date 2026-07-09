---
type: ai-prompt
title: "Interview Question Generation"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/llm, recruitment/interviews]
---

## Purpose

Generate role-specific interview questions tailored to a candidate's profile and job requirements. Questions are categorized by type and difficulty to help interviewers conduct structured, comprehensive interviews that assess both technical capability and cultural fit.

This prompt supports [[sprint-12-interview-ai|Sprint 12 — AI Interview Assistance]] and is designed to reduce interview preparation time from 30+ minutes to under 5 minutes per candidate.

## Prompt Template

```text
You are an expert interview designer for a recruitment platform. Your task is to 
generate a structured set of interview questions tailored to a specific candidate 
and role.

## Job Details
- **Title**: {{job_title}}
- **Department**: {{department}}
- **Seniority Level**: {{seniority_level}}
- **Required Skills**: {{required_skills}}
- **Preferred Skills**: {{preferred_skills}}
- **Key Responsibilities**: {{responsibilities}}
- **Team Size**: {{team_size}}

## Candidate Profile
- **Current Role**: {{current_title}} at {{current_company}}
- **Years of Experience**: {{years_of_experience}}
- **Key Skills**: {{candidate_skills}}
- **Notable Achievements**: {{achievements}}
- **Skill Gaps**: {{missing_skills}}

## Scoring Context (from hybrid evaluation)
- **Overall Score**: {{overall_score}}/100
- **Keyword Match**: {{keyword_score}}/100
- **Areas of Concern**: {{concerns}}

## Instructions

Generate exactly 10 interview questions following this distribution:

### Technical Questions (4 questions)
- 1 question at EASY difficulty — validates foundational knowledge
- 2 questions at MEDIUM difficulty — tests practical application
- 1 question at HARD difficulty — assesses depth and problem-solving
- Focus on: required skills, candidate's claimed expertise, and skill gaps

### Behavioral Questions (3 questions)
- Use the STAR format (Situation, Task, Action, Result)
- Focus on: leadership, collaboration, conflict resolution, adaptability
- Tailor to the seniority level (entry-level vs. senior vs. leadership)

### Situational Questions (2 questions)
- Present realistic scenarios the candidate would face in this role
- Assess decision-making, prioritization, and problem-solving approach
- Reference actual job responsibilities

### Culture Fit Questions (1 question)
- Assess alignment with team dynamics and work style
- Focus on collaboration preferences, growth mindset, or work-life balance

## Output Format
For each question, provide:
1. **Category**: Technical | Behavioral | Situational | Culture Fit
2. **Difficulty**: Easy | Medium | Hard
3. **Question**: The interview question
4. **Purpose**: What this question assesses (1 sentence)
5. **What to listen for**: Key indicators of a strong answer (2-3 bullet points)

## Rules
- Do NOT ask about age, marital status, religion, ethnicity, disability, 
  pregnancy, or any protected characteristic
- Do NOT ask about salary history or current compensation
- Do NOT ask about gaps in employment in a way that implies judgment
- Questions must be job-relevant and legally defensible
- Avoid leading questions that suggest a "correct" answer
- Frame skill gap questions constructively (assess learning potential, not deficiency)
- Difficulty should be appropriate to the seniority level
```

## Question Category Guidelines

| Category | Purpose | Seniority Adaptation |
|---|---|---|
| Technical | Validate hands-on skills and depth | Junior: fundamentals. Senior: architecture, tradeoffs |
| Behavioral | Assess soft skills via past behavior | Junior: teamwork, learning. Senior: leadership, mentoring |
| Situational | Evaluate decision-making approach | Junior: task execution. Senior: strategic thinking |
| Culture Fit | Gauge team/org alignment | Consistent across levels |

## Difficulty Calibration

| Level | Junior (0-3 yrs) | Mid (3-6 yrs) | Senior (6+ yrs) |
|---|---|---|---|
| Easy | Concept definitions | Best practices | Architecture principles |
| Medium | Code implementation | System design components | System design end-to-end |
| Hard | Debugging scenarios | Performance optimization | Large-scale tradeoff analysis |

## Example Output

```markdown
### Question 1
- **Category**: Technical
- **Difficulty**: Medium
- **Question**: "You mentioned experience with Django REST Framework. Walk me through 
  how you would design a paginated API endpoint that supports filtering by multiple 
  candidate attributes and sorting by relevance score. What tradeoffs would you consider?"
- **Purpose**: Assesses practical Django/DRF knowledge and API design thinking.
- **What to listen for**:
  - Mentions cursor vs. offset pagination tradeoffs
  - Considers database query performance (N+1, indexing)
  - Discusses filter validation and security (SQL injection prevention)
```

## Guardrails

| Rule | Rationale |
|---|---|
| No protected-class questions | Legal compliance (EEOC, GDPR, local labor law) |
| No salary history questions | Banned in many jurisdictions; perpetuates pay inequity |
| Job-relevant only | Every question must map to a role requirement or responsibility |
| No "trick" questions | Assess genuine capability, not ability to handle gotchas |
| Constructive gap exploration | "How would you approach learning X?" not "Why don't you know X?" |
| STAR-format behavioral | Structured responses enable consistent candidate comparison |

## Model Configuration

| Parameter | Value | Rationale |
|---|---|---|
| Model | `Qwen2.5-Coder:7B (via Ollama)` | Primary local LLM for tailored, structured interview question generation |
| Fallback models | `Mistral`, `Phi-3` | Availability and latency fallback only |
| Temperature | 0.6 | Higher creativity for diverse question generation |
| Max tokens | 1024 | 10 detailed questions need space |
| Top-p | 0.95 | Broader sampling for question variety |

## Error Handling

- **Missing job details**: Generate general questions for the role title and seniority level. Note reduced specificity.
- **Missing candidate profile**: Generate role-generic questions without personalization. Flag that questions are not tailored.
- **No skill gaps**: Skip gap-focused questions; allocate to additional depth questions in strongest areas.
- **Unknown seniority**: Default to medium difficulty calibration.

## Related Documents

- [[sprint-12-interview-ai|Sprint 12 — AI Interview Assistance]]
- [[ai-pipeline|AI Pipeline]]
- [[candidate-scoring|Candidate Insight Generator]]
- [[candidate-summary|Candidate Summary Generation]]
