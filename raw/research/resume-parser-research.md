---
type: research
title: "Resume Parser Research"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [research/industry-report, ai/nlp, product/feature]
---

# Resume Parser Research

## Overview
Extracting structured data from raw, unstructured resumes is a notoriously difficult problem due to the infinite variety of formatting, file types, and human phrasing.

## Approaches Comparison

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| **Rule-Based (Regex)** | Uses regular expressions to find patterns (emails, dates). | Fast, cheap, deterministic. | Extremely brittle, terrible at extracting context or complex skills. |
| **Traditional ML (NER)** | Custom trained Named Entity Recognition models (e.g., SpaCy). | Fast at inference, decent accuracy on standard formats. | High training cost, requires massive labeled dataset, struggles with novel layouts. |
| **LLM-Based (Qwen2.5-Coder:7B via Ollama)** | Passes extracted raw text to the primary local LLM with a strict JSON schema prompt. | Strong structured output, handles unusual formatting, understands context. | Higher latency than rules, potential for hallucinations without validation. |
| **Hybrid** | Regex for hard data (email/phone) + LLM for complex sections (experience/skills). | Balances cost, speed, and accuracy. | More complex system architecture. |

## Existing Commercial Solutions
- **Sovren (Textkernel):** Enterprise standard. Very accurate, but expensive and legacy API.
- **Affinda:** Modern API, good accuracy, uses deep learning.
- **AWS Comprehend / Azure Document Intelligence:** General purpose, requires custom tuning for resumes.
- **Pyresparser (Open Source):** SpaCy based. Good for basic use cases but fails on complex modern resumes.

## Our Recommended Approach: LLM-Based with Structured Output
Use Qwen2.5-Coder:7B via Ollama with strict JSON schema enforcement. Mistral and Phi-3 are fallback models only; they are not the primary production LLM.

**The Pipeline:**
1. Text Extraction: Use `PyPDF2` / `pdfplumber` for PDFs, `python-docx` for Word docs.
2. Fallback OCR: Tesseract if the PDF is an image scan.
3. LLM Parsing: Send the raw string to the LLM with the [[resume-analysis|Resume Analysis & Data Extraction]].
4. Validation: Enforce schema using Pydantic on the backend.

## Known Challenges
- **Non-Standard Formats:** Multi-column layouts often break simple text extractors (text reads left-to-right across columns incorrectly).
  - *Solution:* Use layout-aware PDF parsers (like `pdfplumber` or cloud document AI).
- **International Resumes:** Different date formats, inclusion of photos/marital status (common in parts of Europe/Asia).
  - *Solution:* Explicit prompt instructions to ignore demographic data.
- **Length:** 5+ page academic CVs might exceed context windows or token limits.
  - *Solution:* Truncation strategies or chunked processing.

See also: [[ai-pipeline|AI Pipeline]], [[resume-parser|Resume Parser]], [[resume-analysis|Resume Analysis & Data Extraction]]
