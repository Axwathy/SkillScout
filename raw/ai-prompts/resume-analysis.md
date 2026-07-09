---
type: ai-prompt
title: "Resume Analysis & Data Extraction"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/llm, recruitment/parsing]
---

## Purpose

Extract structured data from raw resume text into a standardized JSON format. This is the first stage of the [[ai-pipeline|AI Pipeline]] — all downstream processes (scoring, summarization, matching) depend on accurate resume parsing.

This prompt powers [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]] and feeds data to the [[resume-parser|Resume Parser]] service.

## Prompt Template

````text
You are an expert resume parser for a recruitment platform. Your task is to extract 
structured data from raw resume text and return it as valid JSON.

## Raw Resume Text
```
{{raw_resume_text}}
```

## Instructions
Parse the resume text and extract the following fields. If a field is not present 
in the resume, use null. Do NOT fabricate or infer information that is not explicitly 
stated or clearly implied.

### Extraction Rules
1. **Names**: Extract the full name as presented. Do not reorder or abbreviate.
2. **Contact info**: Extract email and phone exactly as written. If multiple, use the first.
3. **Skills**: Extract both explicitly listed skills AND skills mentioned in job descriptions.
   Assign proficiency based on context:
   - "expert" / "advanced": 5+ years usage, leadership role, or explicitly stated
   - "intermediate": 2-5 years usage or moderate context
   - "beginner": mentioned but limited context
4. **Experience**: Extract each position with dates. Parse dates flexibly 
   (e.g., "Jan 2020", "2020-01", "January 2020" → "2020-01").
   Use "present" for current roles.
5. **Achievements**: Extract quantified accomplishments where possible. Keep original phrasing.
6. **Education**: Extract degree, field of study, institution, and graduation year.
7. **Certifications**: Extract name, issuing organization, and year if available.

### Date Parsing
- Convert all dates to "YYYY-MM" format where possible
- If only year is given, use "YYYY-01"
- Current/ongoing positions: use "present" as end_date
- If dates are ambiguous, note in the _parsing_notes field

## Output Format
Return ONLY valid JSON matching the schema below. No markdown, no commentary, 
no explanation outside the JSON.
````

## Output JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["personal_info", "skills", "experience", "education"],
  "properties": {
    "personal_info": {
      "type": "object",
      "properties": {
        "full_name": { "type": ["string", "null"] },
        "email": { "type": ["string", "null"] },
        "phone": { "type": ["string", "null"] },
        "location": { "type": ["string", "null"] },
        "linkedin_url": { "type": ["string", "null"] },
        "github_url": { "type": ["string", "null"] },
        "portfolio_url": { "type": ["string", "null"] }
      }
    },
    "summary": {
      "type": ["string", "null"],
      "description": "Professional summary or objective if present"
    },
    "skills": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "proficiency"],
        "properties": {
          "name": { "type": "string" },
          "proficiency": { 
            "type": "string", 
            "enum": ["expert", "advanced", "intermediate", "beginner"] 
          },
          "category": {
            "type": "string",
            "enum": ["programming_language", "framework", "database", "cloud", 
                     "devops", "tool", "soft_skill", "domain", "other"]
          },
          "years_used": { "type": ["number", "null"] }
        }
      }
    },
    "experience": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["company", "role", "start_date"],
        "properties": {
          "company": { "type": "string" },
          "role": { "type": "string" },
          "start_date": { "type": "string", "pattern": "^\\d{4}-\\d{2}$" },
          "end_date": { "type": ["string", "null"] },
          "location": { "type": ["string", "null"] },
          "description": { "type": ["string", "null"] },
          "achievements": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "education": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "institution": { "type": "string" },
          "degree": { "type": ["string", "null"] },
          "field_of_study": { "type": ["string", "null"] },
          "graduation_year": { "type": ["integer", "null"] },
          "gpa": { "type": ["string", "null"] }
        }
      }
    },
    "certifications": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "issuer": { "type": ["string", "null"] },
          "year": { "type": ["integer", "null"] },
          "credential_id": { "type": ["string", "null"] }
        }
      }
    },
    "languages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "language": { "type": "string" },
          "proficiency": { "type": "string" }
        }
      }
    },
    "_metadata": {
      "type": "object",
      "properties": {
        "parsing_confidence": {
          "type": "string",
          "enum": ["high", "medium", "low"],
          "description": "Overall confidence in parsing accuracy"
        },
        "parsing_notes": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Notes about ambiguities, assumptions, or issues"
        },
        "total_years_experience": {
          "type": ["number", "null"],
          "description": "Calculated total years of professional experience"
        }
      }
    }
  }
}
```

## Error Handling

| Scenario | Handling Strategy |
|---|---|
| Garbled/OCR text | Set `parsing_confidence: "low"`, add note, extract what's possible |
| No contact info | Set fields to `null`, add parsing note |
| Ambiguous dates | Use best guess with "YYYY-01", document in `parsing_notes` |
| Non-English resume | Attempt extraction, set `parsing_confidence: "low"`, flag for human review |
| Very short resume | Extract available data, set `parsing_confidence: "low"` |
| Multiple roles at same company | Create separate experience entries, note relationship |
| Freelance/contract work | Extract as individual experience entries with "Freelance" or "Contract" prefix |

## Model Configuration

| Parameter | Value | Rationale |
|---|---|---|
| Model | `Qwen2.5-Coder:7B (via Ollama)` | Primary local LLM for structured extraction and schema-following |
| Fallback models | `Mistral`, `Phi-3` | Availability and latency fallback only |
| Temperature | 0.1 | Near-deterministic for consistent parsing |
| Max tokens | 2048 | Complex resumes generate large JSON |
| Top-p | 0.8 | Tight sampling for extraction accuracy |
| Response format | `json_object` | Enforce valid JSON output |

## Validation Pipeline

After LLM extraction, the parsed output is validated programmatically:

```python
def validate_parsed_resume(data: dict) -> tuple[bool, list[str]]:
    """Validate parsed resume data against schema and business rules."""
    errors = []

    # Schema validation
    try:
        jsonschema.validate(data, RESUME_SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error: {e.message}")

    # Business rule validation
    if not data.get('personal_info', {}).get('full_name'):
        errors.append("Missing candidate name")

    if not data.get('skills'):
        errors.append("No skills extracted — may need manual review")

    # Date consistency check
    for exp in data.get('experience', []):
        if exp.get('end_date') and exp['end_date'] != 'present':
            if exp['start_date'] > exp['end_date']:
                errors.append(f"Date inversion: {exp['role']} at {exp['company']}")

    return (len(errors) == 0, errors)
```

## Related Documents

- [[ai-pipeline|AI Pipeline]]
- [[resume-parser|Resume Parser]]
- [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]]
- [[candidate-summary|Candidate Summary Generation]]
- [[upload-security|File Upload Security]]
