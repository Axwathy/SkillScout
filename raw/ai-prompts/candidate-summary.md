---
type: ai-prompt
title: "Candidate Summary Generation"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/llm, recruitment/screening]
---

## Purpose

Generate a concise, recruiter-friendly summary of a parsed candidate profile. The summary enables recruiters to quickly assess candidate fit without reading the full resume, reducing screening time by an estimated 60-70%.

## Use Case

This prompt is invoked after the [[resume-parser|Resume Parser]] has extracted structured data from a candidate's resume. It is part of the [[ai-pipeline|AI Pipeline]] and runs automatically when a new candidate profile is created or updated.

## Prompt Template

```text
You are an expert recruitment assistant. Your task is to generate a concise, 
objective summary of a candidate's profile for a recruiter.

## Candidate Profile
- **Name**: {{candidate_name}}
- **Current Title**: {{current_title}}
- **Years of Experience**: {{years_of_experience}}
- **Location**: {{location}}

### Skills
{{#each skills}}
- {{name}} (Proficiency: {{proficiency}})
{{/each}}

### Work Experience
{{#each experiences}}
- **{{role}}** at {{company}} ({{start_date}} – {{end_date}})
  {{#each achievements}}
  - {{this}}
  {{/each}}
{{/each}}

### Education
{{#each education}}
- {{degree}} in {{field}}, {{institution}} ({{year}})
{{/each}}

### Certifications
{{#each certifications}}
- {{name}} ({{issuer}}, {{year}})
{{/each}}

## Target Role (if available)
- **Title**: {{job_title}}
- **Required Skills**: {{required_skills}}
- **Preferred Skills**: {{preferred_skills}}
- **Experience Level**: {{experience_level}}

## Instructions
1. Write a 3-4 sentence summary highlighting:
   - The candidate's primary area of expertise and experience level
   - Key technical skills and domain knowledge
   - Most relevant accomplishments or qualifications
   - Fit relative to the target role (if provided)
2. Use professional, neutral language
3. Focus on verifiable facts from the profile
4. Do NOT include any hiring recommendation or decision
5. Do NOT mention age, gender, ethnicity, disability, or any protected characteristics
6. Do NOT speculate about information not present in the profile

## Output Format
Return ONLY the summary paragraph. No headers, bullet points, or additional commentary.
```

## Expected Output

### Example Input
```json
{
  "candidate_name": "Sarah Chen",
  "current_title": "Senior Backend Engineer",
  "years_of_experience": 7,
  "skills": [
    {"name": "Python", "proficiency": "expert"},
    {"name": "Django", "proficiency": "expert"},
    {"name": "PostgreSQL", "proficiency": "advanced"},
    {"name": "AWS", "proficiency": "advanced"},
    {"name": "Docker", "proficiency": "intermediate"}
  ],
  "experiences": [
    {
      "role": "Senior Backend Engineer",
      "company": "TechCorp",
      "start_date": "2021-03",
      "end_date": "present",
      "achievements": [
        "Led migration of monolithic API to microservices, reducing p95 latency by 40%",
        "Designed and implemented real-time notification system serving 500K+ users"
      ]
    }
  ]
}
```

### Example Output
> Sarah Chen is a Senior Backend Engineer with 7 years of experience specializing in Python and Django, with strong expertise in PostgreSQL and AWS infrastructure. At TechCorp, she led a monolithic-to-microservices migration that reduced p95 latency by 40% and architected a real-time notification system serving over 500K users. Her technical profile demonstrates depth in backend systems design and production-scale operations, with hands-on experience in containerization and cloud deployment.

## Guardrails

| Rule | Rationale |
|---|---|
| No hiring recommendations | Summary is informational; hiring decisions are human |
| No demographic commentary | Legal compliance; anti-discrimination |
| Factual statements only | Avoid hallucination; only reference provided data |
| No comparative language | Don't compare to other candidates or "ideal" profiles |
| No salary speculation | Compensation is not part of profile summarization |
| Professional tone | Maintain recruiter-facing quality |

## Model Configuration

| Parameter   | Value         | Rationale                                  |
| ----------- | ------------- | ------------------------------------------ |
| Model       | `Qwen2.5-Coder:7B (via Ollama)` | Primary local LLM for recruiter-facing summaries |
| Fallback models | `Mistral`, `Phi-3` | Availability and latency fallback only |
| Temperature | 0.3           | Low creativity; factual, consistent output |
| Max tokens  | 256           | Summaries should be concise                |
| Top-p       | 0.9           | Balanced nucleus sampling                  |

## Error Handling

- **Incomplete profile**: If critical fields (name, experience) are missing, generate a shorter summary noting available information. Prefix with "Limited profile data available."
- **No job context**: If target role is not provided, generate a general professional summary without fit assessment.
- **Empty skills**: Focus summary on work experience and education instead.
- **Parsing errors**: If structured data contains obvious parsing artifacts (e.g., garbled text), flag for human review rather than summarizing.

## Related Documents

- [[ai-pipeline|AI Pipeline]]
- [[resume-parser|Resume Parser]]
- [[candidate-scoring|Candidate Insight Generator]]
- [[resume-analysis|Resume Analysis & Data Extraction]]
- [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]]
