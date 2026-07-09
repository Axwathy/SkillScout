---
type: feature
title: "Resume Parser"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, ai/llm, ai/nlp, recruitment/screening]
---

# Resume Parser

## Overview

The Resume Parser is a core AI-powered feature that automatically extracts structured candidate data from uploaded resume files. It supports PDF and DOCX formats and leverages LLM-based parsing to produce consistent, queryable candidate profiles. This feature is the entry point for the [[ai-pipeline|AI Pipeline]] and feeds directly into candidate scoring and [[semantic-search|Semantic Search]].

## Purpose

Recruiters spend significant time manually reading and entering candidate data. The Resume Parser eliminates this bottleneck by converting unstructured resume documents into structured JSON profiles within seconds. Parsed data powers downstream features including scoring, ranking, and semantic matching.

## User Flow

1. **Upload** — Recruiter drags a resume file into the upload dropzone or clicks to browse.
2. **Validation** — System validates file type (PDF, DOCX), size (max 10 MB), and scans for malware.
3. **Processing Indicator** — A real-time progress bar shows extraction status (uploading → extracting text → parsing → complete).
4. **Parsed Profile Display** — Structured data is rendered as a profile card with sections for contact info, experience, education, skills, and certifications.
5. **Manual Corrections** — Recruiter can toggle edit mode to correct any misidentified fields before confirming.
6. **Confirmation** — On confirmation, the parsed profile is saved, an embedding is generated, and [[candidate-scoring|Candidate Insight Generator]] is triggered.

## Backend Logic

The parsing pipeline follows a strict sequence:

| Step | Description | Technology |
|------|-------------|------------|
| 1. File Validation | Check MIME type, file size, extension | Django validators, `python-magic` |
| 2. Text Extraction | Extract raw text from document | `PyPDF2` / `pdfplumber` (PDF), `python-docx` (DOCX) |
| 3. Text Cleaning | Normalize whitespace, remove artifacts | Regex, custom cleaners |
| 4. LLM Structured Parsing | Send cleaned text to LLM with schema prompt | Qwen2.5-Coder:7B via Ollama and [[resume-analysis|Resume Analysis & Data Extraction]] |
| 5. JSON Validation | Validate LLM output against Pydantic schema | Pydantic v2 models |
| 6. Data Storage | Store parsed data as JSONB in candidate record | PostgreSQL JSONB column |
| 7. Embedding Generation | Generate vector embedding from parsed text | BAAI `bge-small-en-v1.5` |
| 8. Score Triggering | Queue candidate scoring task | Celery async task |

### Parsed Data Schema

```json
{
  "personal_info": {
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin_url": "string | null"
  },
  "summary": "string",
  "experience": [
    {
      "title": "string",
      "company": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM | Present",
      "description": "string",
      "achievements": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "graduation_date": "YYYY-MM",
      "gpa": "float | null"
    }
  ],
  "skills": ["string"],
  "certifications": ["string"],
  "languages": ["string"]
}
```

## Frontend Components

- **Upload Dropzone** — Accepts drag-and-drop and click-to-browse. Shows file preview with name and size. Validates client-side before upload.
- **Parsing Progress** — Animated stepper showing current pipeline stage. Estimated time remaining based on file size.
- **Parsed Profile Card** — Sectioned card layout displaying all parsed fields. Color-coded confidence indicators on each field.
- **Edit Mode** — Inline editing for all parsed fields. Add/remove entries in repeating sections (experience, education). Changes tracked for analytics.

## Edge Cases

| Scenario | Handling Strategy |
|----------|-------------------|
| Multi-page resumes (10+ pages) | Truncate to first 8 pages with warning; process in chunks |
| Non-standard formats (creative resumes) | Fallback to raw text extraction; flag for manual review |
| Image-only PDFs (scanned documents) | Detect via text-length heuristic; queue for OCR pipeline (future) |
| International formats (non-Latin scripts) | UTF-8 encoding support; LLM handles multilingual parsing |
| Missing sections (no education listed) | Return null fields; no error — partial profiles are valid |
| Corrupted files | Return 422 with user-friendly error message |
| Password-protected PDFs | Detect and prompt user to upload unprotected version |

## Security Considerations

All uploads pass through the [[upload-security|File Upload Security]] pipeline:

- File type validation (MIME + magic bytes, not just extension)
- Antivirus scanning via ClamAV integration
- File size limits enforced at both Nginx and application layers
- Uploaded files stored in a private Supabase Storage bucket with backend-signed URL access
- Temporary processing files are deleted after parsing completes

## Future Improvements

- **OCR Integration** — Tesseract or AWS Textract for scanned PDF support
- **LinkedIn Import** — Parse LinkedIn profile URLs directly via API
- **Bulk Parsing** — Upload ZIP archive of multiple resumes with batch processing
- **Custom Parsing Templates** — Organization-specific field extraction rules
- **Confidence Scoring** — Per-field confidence scores from LLM for review prioritization
- **Resume Format Detection** — Auto-detect chronological vs. functional vs. hybrid formats

## Related Pages

- [[ai-pipeline|AI Pipeline]] — End-to-end AI processing workflow
- [[resume-analysis|Resume Analysis & Data Extraction]] — LLM prompt template for structured extraction
- [[upload-security|File Upload Security]] — File upload security measures
- [[candidate-api|Candidate API]] — API endpoints for candidate management
- [[sprint-06-resume-parsing|Sprint 6 — AI Resume Parsing]] — Implementation sprint details
