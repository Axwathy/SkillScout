---
type: experiment
title: "Ranking Formula Tests"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [ai/ml, research]
---

# [EXPERIMENTAL] Ranking Formula Tests

This document describes the experiment plan for tuning the hybrid ranking formula used to score and rank candidates against job postings. The formula combines semantic similarity with structured feature matching to produce a final candidate score.

> **Production rule:** Math decides. AI explains. These experiments may evaluate alternative deterministic formulas, but the LLM must not generate, override, or reorder candidate scores.

See also: [[ai-pipeline|AI Pipeline]], [[ADR-003-hybrid-ranking|ADR-003 — Hybrid Ranking System]], [[candidate-scoring|Candidate Insight Generator]]

---

## Objective

Find the optimal weight combination for the hybrid ranking formula that **maximizes correlation with human expert rankings** while maintaining interpretability and consistency across different job types.

---

## Current Production Formula

The current production formula uses three deterministic signals:

```text
final_score =
  0.45 * semantic_similarity +
  0.30 * skill_match +
  0.25 * experience_match
```

| Signal | Production Weight | Source |
|---|---:|---|
| `semantic_similarity` | 0.45 | BAAI/bge-small-en-v1.5 embeddings + pgvector cosine similarity |
| `skill_match` | 0.30 | Rule-based exact/fuzzy skill matching |
| `experience_match` | 0.25 | Rule-based years, seniority, and relevance scoring |

This is the accepted production baseline unless a future decision supersedes [[ADR-003-hybrid-ranking|ADR-003 - Hybrid Ranking System]].

## Experimental Formula Space

The formulas below are **EXPERIMENTAL (NOT CURRENT PRODUCTION FORMULA)**. They are preserved for research history and future tuning, not as implementation guidance.

The hybrid score is a weighted sum of multiple signals:

```
final_score = (w_semantic × semantic_score)
            + (w_skills × skill_match_score)
            + (w_experience × experience_score)
            + (w_education × education_score)
            + bonus_factors
```

### Variables Under Test

| Variable | Description | Range | Default |
|----------|-------------|-------|---------|
| `w_semantic` | Weight for embedding cosine similarity | 0.0 – 1.0 | 0.45 |
| `w_skills` | Weight for hard skill keyword matching | 0.0 – 1.0 | 0.30 |
| `w_experience` | Weight for years of experience relevance | 0.0 – 1.0 | 0.25 production, 0.20 experimental |
| `w_education` | Weight for education level/field match | 0.0 – 1.0 | 0.00 production, 0.10 experimental |

**Constraint**: `w_semantic + w_skills + w_experience + w_education = 1.0`

### Bonus Factors

| Factor | Description | Bonus Range |
|--------|-------------|-------------|
| `certification_bonus` | Relevant industry certifications (AWS, PMP, etc.) | 0 – 5 points |
| `education_tier_bonus` | Advanced degree in relevant field | 0 – 3 points |
| `recency_bonus` | Recent experience in the target domain (last 2 years) | 0 – 3 points |
| `leadership_bonus` | Management/leadership experience when role requires it | 0 – 3 points |

---

## Test Methodology

### Step 1: Create Golden Test Set

| Component | Details |
|-----------|---------|
| **Jobs** | 10 job postings across different roles and seniority levels |
| **Candidates** | 20 candidates per job = 200 candidate-job pairs |
| **Human rankings** | 3 hiring managers rank the 20 candidates per job from best to worst |
| **Consensus ranking** | Average rank across all 3 rankers (Borda count method) |
| **Inter-rater reliability** | Kendall's W ≥ 0.6 required before proceeding |

### Step 2: Grid Search Over Weight Combinations

Test all weight combinations at 0.1 increments where weights sum to 1.0:

```python
from itertools import product

weight_options = [round(x * 0.1, 1) for x in range(11)]  # 0.0 to 1.0
combinations = [
    (ws, wk, we, wed)
    for ws, wk, we, wed in product(weight_options, repeat=4)
    if abs(ws + wk + we + wed - 1.0) < 0.001
]
# Total combinations: 286
```

For each combination:
1. Calculate `final_score` for all 200 candidate-job pairs
2. Rank candidates per job by `final_score`
3. Compare against human consensus ranking

### Step 3: Evaluate with Ranking Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **NDCG@5** | Ranking quality for the top 5 candidates | ≥ 0.85 |
| **NDCG@10** | Ranking quality for the top 10 candidates | ≥ 0.80 |
| **Kendall's τ** | Rank correlation between model and human rankings | ≥ 0.65 |
| **Spearman's ρ** | Monotonic relationship between scores and human labels | ≥ 0.70 |
| **Top-1 Accuracy** | How often the model's #1 candidate matches the human #1 | ≥ 0.60 |
| **Top-3 Overlap** | Overlap between model's top 3 and human's top 3 | ≥ 0.70 |

### Step 4: Sensitivity Analysis

For the top 5 weight combinations:
- Perturb each weight by ±0.05 and measure metric stability
- Identify which weights have the most impact on ranking quality
- Check for overfitting to specific job types

### Step 5: A/B Test Top Formulas

| Group | Formula | Duration | Sample Size |
|-------|---------|----------|-------------|
| Control | Current default weights | 2 weeks | 50% of new jobs |
| Treatment A | Best grid search result | 2 weeks | 25% of new jobs |
| Treatment B | Second-best grid search result | 2 weeks | 25% of new jobs |

**Success metric**: Recruiter satisfaction (measured by how often the recruiter's final hire matches the model's top-3 prediction).

---

## Baseline Comparisons

| Baseline | Description | Expected NDCG@5 |
|----------|-------------|-----------------|
| **Random** | Random candidate ordering | ~0.50 |
| **Pure semantic** | `w_semantic = 1.0`, all others = 0 | ~0.70 |
| **Pure skills** | `w_skills = 1.0`, all others = 0 | ~0.65 |
| **Equal weights** | All weights = 0.25 | ~0.75 |
| **Hybrid (production default)** | 0.45/0.30/0.25 | ~0.80 |
| **Hybrid + education experiment** | 0.4/0.3/0.2/0.1 | ~0.80 |

---

## Segmented Analysis

Results should be broken down by job characteristics to identify if different job types need different weights:

| Segment | Jobs | Hypothesis |
|---------|------|-----------|
| **Technical roles** (engineering, data science) | 4 | Skills weight should be higher |
| **Non-technical roles** (marketing, sales, PM) | 3 | Semantic weight should be higher |
| **Senior roles** (director, VP) | 2 | Experience weight should be higher |
| **Entry-level roles** | 1 | Education weight should be higher |

If segmentation significantly improves results, consider **per-job-type weight profiles** rather than a single global formula.

---

## Bonus Factor Tuning

After optimizing the main weights, separately tune bonus factors:

| Test | Approach |
|------|----------|
| **Bonus magnitude** | Test bonus values from 1 to 10 points (step 1) |
| **Bonus inclusion** | Ablation study — remove each bonus factor and measure impact |
| **Certification mapping** | Map specific certifications to relevance scores per job domain |

---

## Results

> ⚠️ **Status**: Experiment not yet started. Results will be filled after execution.

### Grid Search Results (Top 10)

| Rank | w_semantic | w_skills | w_experience | w_education | NDCG@5 | Kendall's τ |
|------|------------|----------|--------------|-------------|--------|-------------|
| 1 | — | — | — | — | — | — |
| 2 | — | — | — | — | — | — |
| 3 | — | — | — | — | — | — |
| 4 | — | — | — | — | — | — |
| 5 | — | — | — | — | — | — |
| 6 | — | — | — | — | — | — |
| 7 | — | — | — | — | — | — |
| 8 | — | — | — | — | — | — |
| 9 | — | — | — | — | — | — |
| 10 | — | — | — | — | — | — |

### Segmented Results

| Segment | Best w_semantic | Best w_skills | Best w_experience | Best w_education | NDCG@5 |
|---------|----------------|--------------|-------------------|------------------|--------|
| Technical | — | — | — | — | — |
| Non-technical | — | — | — | — | — |
| Senior | — | — | — | — | — |
| Entry-level | — | — | — | — | — |

### A/B Test Results

| Group | Recruiter Satisfaction | Top-3 Match Rate | Sample Size |
|-------|----------------------|-------------------|-------------|
| Control | — | — | — |
| Treatment A | — | — | — |
| Treatment B | — | — | — |

### Recommendation

> To be written after experiments are complete. Include: final weight configuration, per-segment adjustments (if any), and implementation plan.

---

## Next Steps

1. [ ] Recruit 3 hiring managers for human ranking exercise
2. [ ] Prepare 10 job descriptions and 200 candidate profiles
3. [ ] Build grid search evaluation script
4. [ ] Run grid search and populate results
5. [ ] Conduct sensitivity analysis on top candidates
6. [ ] Design and run A/B test
7. [ ] Document final recommendation and update [[ai-pipeline|AI Pipeline]]
