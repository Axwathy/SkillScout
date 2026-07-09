---
type: experiment
title: "Prompt Engineering Experiments"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/ml, ai/llm, research]
---

# [EXPERIMENTAL] Prompt Engineering Experiments

This document tracks prompt engineering experiments for all AI-powered features in the recruitment platform. Each prompt is versioned, tested against standardized inputs, and evaluated on quality, consistency, and cost metrics.

> **Production rule:** Math decides. AI explains. Prompt experiments may test explanation quality, extraction quality, summaries, and recruiter insights, but they must not make the LLM responsible for candidate ranking or score generation.

See also: [[resume-analysis|Resume Analysis & Data Extraction]], [[candidate-scoring|Candidate Insight Generator]], [[interview-generation|Interview Question Generation]], [[candidate-summary|Candidate Summary Generation]]

---

## Prompts Under Development

| Prompt | Purpose | Current Version | Status |
|--------|---------|-----------------|--------|
| **Resume Parser** | Extract structured data from raw resume text | v1.0 | 🟡 Draft |
| **Candidate Insight Generator** | Explain deterministic hybrid scores and provide recruiter context | v1.0 | 🟡 Draft |
| **Interview Question Generator** | Create tailored interview questions from job + candidate data | v1.0 | 🟡 Draft |
| **Candidate Summarizer** | Generate concise candidate summary for hiring manager review | v1.0 | 🟡 Draft |

---

## Methodology

### Versioning Convention

- **Major version** (v1.0 → v2.0): Fundamental approach change (e.g., different system prompt structure, different output schema)
- **Minor version** (v1.0 → v1.1): Refinement (e.g., added examples, adjusted tone, fixed edge cases)
- **Patch version** (v1.1 → v1.1.1): Typo fixes or formatting changes with no functional impact

### Test Protocol

For each prompt version:

1. **Select test inputs**: 10 diverse sample inputs that cover typical cases and known edge cases
2. **Run generation**: Call the LLM with the prompt + each test input (temperature = 0 for reproducibility)
3. **Evaluate outputs**: Score each output on predefined quality dimensions
4. **Measure costs**: Record token usage (input + output) and latency per call
5. **Compare**: Side-by-side comparison with previous version(s)

### Quality Dimensions

| Dimension | Description | Scale |
|-----------|-------------|-------|
| **Accuracy** | Factual correctness of extracted/generated content | 1-5 |
| **Completeness** | All relevant information captured, nothing important missing | 1-5 |
| **Consistency** | Same input produces similar quality across multiple runs | 1-5 |
| **Tone** | Professional, neutral, appropriate for HR context | 1-5 |
| **Format** | Adheres to specified output schema (JSON, markdown, etc.) | Pass/Fail |
| **Helpfulness** | Output is actionable and useful for the target user (recruiter) | 1-5 |

---

## Experiment 1: Resume Parser Prompt

### Test Inputs

| ID | Resume Type | Characteristics |
|----|-------------|-----------------|
| RP-01 | Standard US format | Chronological, clear sections, 2 pages |
| RP-02 | Creative/design resume | Non-standard layout, skills-first |
| RP-03 | Academic CV | Publication list, research focus, 5+ pages |
| RP-04 | Entry-level | Limited experience, education-heavy |
| RP-05 | Senior executive | 20+ years, multiple leadership roles |
| RP-06 | International format | European CV style, photo included, personal details |
| RP-07 | Career changer | Mixed industry experience, transferable skills |
| RP-08 | Technical (engineering) | Heavy on technical skills, certifications, projects |
| RP-09 | Sparse/minimal | Very little information, gaps in employment |
| RP-10 | Non-English names | Unicode characters, international education institutions |

### Results: Resume Parser

| Version | Avg Accuracy | Avg Completeness | Avg Consistency | Format Pass Rate | Avg Tokens (in/out) | Avg Latency |
|---------|-------------|------------------|-----------------|------------------|---------------------|-------------|
| v1.0 | — | — | — | — | — | — |

### Known Issues (v1.0)

> To be documented after initial testing. Expected issues:
> - Difficulty with multi-column resume layouts
> - Skills extraction may miss implied skills
> - Date parsing inconsistencies across formats

---

## Experiment 2: Candidate Insight Generator Prompt

This prompt does not generate candidate scores. It receives deterministic scoring outputs from the hybrid scoring engine and converts them into recruiter-friendly explanations.

### Test Inputs

| ID | Scenario | Input Score Context |
|----|----------|---------------------|
| CI-01 | Perfect match — senior dev role, senior dev candidate | High semantic, skill, and experience scores |
| CI-02 | Good match — some skill gaps but strong experience | High semantic and experience, medium skill score |
| CI-03 | Partial match — right domain, wrong seniority | High semantic, low experience score |
| CI-04 | Weak match — tangentially related field | Low semantic and skill scores |
| CI-05 | No match — completely unrelated background | Very low deterministic score |
| CI-06 | Overqualified — VP applying for junior role | Strong experience but seniority mismatch context |
| CI-07 | Career changer — strong transferable skills | Medium semantic, low direct skill overlap |
| CI-08 | Skills match but no experience | High skill, low experience score |
| CI-09 | Experience match but outdated skills | Medium experience, low skill score |
| CI-10 | Equal candidates — two similar profiles for same job | Similar deterministic sub-scores |

### Evaluation Criteria (Insight-Specific)

| Criterion | Description |
|-----------|-------------|
| **Score faithfulness** | Does the explanation preserve the provided deterministic score and sub-scores? |
| **Explanation quality** | Is the explanation specific, citing actual resume content and job requirements? |
| **Bias check** | Does the score change when name/demographics are altered? |
| **Consistency** | Same input produces similar explanation quality across runs? |
| **No ranking override** | Does the output avoid reordering, score modification, or hiring decisions? |

### Results: Candidate Insight Generator

| Version | Score Faithfulness Pass | Explanation Quality (1-5) | Bias Check Pass | No Ranking Override Pass | Avg Tokens |
|---------|-------------------------|---------------------------|-----------------|--------------------------|------------|
| v1.0 | — | — | — | — | — |

---

## Experiment 3: Interview Question Generator

### Test Inputs

| ID | Job Type | Focus Area |
|----|----------|-----------|
| IQ-01 | Software engineer | Technical (coding, system design) |
| IQ-02 | Product manager | Behavioral + strategic thinking |
| IQ-03 | Data scientist | Technical + statistical reasoning |
| IQ-04 | Marketing manager | Creative + analytical |
| IQ-05 | Sales representative | Behavioral + situational |
| IQ-06 | UX designer | Portfolio-based + process |
| IQ-07 | Engineering manager | Leadership + technical depth |
| IQ-08 | Entry-level analyst | Learning potential + basic skills |
| IQ-09 | Remote position | Communication + self-management |
| IQ-10 | Diversity-focused | Inclusive, bias-free questioning |

### Evaluation Criteria (Question-Specific)

| Criterion | Description |
|-----------|-------------|
| **Relevance** | Questions target the right competencies for the role |
| **Specificity** | Questions reference the candidate's actual background |
| **Variety** | Mix of behavioral, technical, and situational questions |
| **Legality** | No questions about protected characteristics |
| **Difficulty calibration** | Questions match the seniority level |

### Results: Interview Questions

| Version | Avg Relevance | Avg Specificity | Variety Score | Legal Compliance | Avg Questions Generated |
|---------|--------------|-----------------|---------------|------------------|------------------------|
| v1.0 | — | — | — | — | — |

---

## Experiment 4: Candidate Summarizer

### Test Inputs

Same candidate profiles used in CI-01 through CI-10 (from Candidate Insight Generator tests).

### Evaluation Criteria (Summarizer-Specific)

| Criterion | Description |
|-----------|-------------|
| **Conciseness** | Summary is 3-5 sentences (not too long, not too short) |
| **Key highlights** | Captures the most relevant qualifications |
| **Actionability** | Hiring manager can make a screening decision from the summary |
| **Neutrality** | No biased language or unsubstantiated claims |

### Results: Candidate Summarizer

| Version | Avg Conciseness | Avg Key Highlights | Avg Actionability | Neutrality Pass | Avg Tokens |
|---------|----------------|--------------------|--------------------|-----------------|------------|
| v1.0 | — | — | — | — | — |

---

## Cost Tracking

| Prompt | Model | Avg Input Tokens | Avg Output Tokens | Cost per Call | Monthly Estimate (1K calls) |
|--------|-------|-----------------|-------------------|---------------|----------------------------|
| Resume Parser | Qwen2.5-Coder:7B (via Ollama) | — | — | — | — |
| Candidate Insight Generator | Qwen2.5-Coder:7B (via Ollama) | — | — | — | — |
| Interview Questions | Qwen2.5-Coder:7B (via Ollama) | — | — | — | — |
| Candidate Summary | Qwen2.5-Coder:7B (via Ollama) | — | — | — | — |

### Cost Optimization Strategies

1. **Model fallback**: Use Qwen2.5-Coder:7B as the primary LLM, with Mistral and Phi-3 as fallbacks for availability or latency issues
2. **Prompt compression**: Reduce system prompt length without losing quality
3. **Caching**: Cache results for identical inputs (resume + job pair)
4. **Batch processing**: Use batch API for non-real-time insight generation; deterministic scoring remains in the scoring service

---

## Next Steps

1. [ ] Finalize v1.0 prompts for all four tasks
2. [ ] Assemble test input sets with diverse, representative samples
3. [ ] Run baseline evaluations for all v1.0 prompts
4. [ ] Identify top 3 improvement areas per prompt
5. [ ] Iterate to v1.1 and re-evaluate
6. [ ] Document final prompt versions and integrate into [[ai-pipeline|AI Pipeline]]
