---
type: backlog
title: "Future Features"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, product/strategy]
---

# Future Features

This document tracks post-MVP feature ideas organized by theme. Each feature includes a description, estimated effort, expected impact, and priority within its theme. These features are candidates for the product roadmap after MVP launch.

See also: [[mvp-features|MVP Feature List]], [[rejected-ideas|Rejected Ideas]]

---

## AI Enhancements

Advanced AI capabilities that deepen the platform's intelligence and automation.

| Feature | Description | Effort | Impact | Priority |
|---------|-------------|--------|--------|----------|
| **Auto-Sourcing from Job Boards** | Automatically search and import candidate profiles from LinkedIn, Indeed, and Glassdoor based on active job requirements. Requires API integrations or web scraping with compliance guardrails. | L | High | P1 |
| **AI Job Description Generator** | Given a job title and key requirements, generate a complete, optimized job description. Include SEO-friendly language, inclusive wording analysis, and salary benchmarking. | M | High | P1 |
| **Candidate Sentiment Analysis** | Analyze candidate communication (emails, chat messages) to gauge engagement level and interest. Flag candidates who may be losing interest or are highly engaged. | L | Medium | P2 |
| **Predictive Time-to-Fill** | ML model trained on historical hiring data to predict how long a job will take to fill. Factors: role type, seniority, location, market conditions, salary competitiveness. | L | Medium | P2 |
| **Smart Resume Summarization** | Generate concise 3-5 sentence candidate summaries highlighting the most relevant qualifications for a specific job. Useful for hiring manager review. | S | High | P1 |
| **Skill Gap Analysis** | Compare a candidate's skills against job requirements and identify specific gaps. Suggest interview questions that probe those gap areas. | M | High | P1 |

---

## Collaboration Features

Tools for team-based hiring workflows and communication.

| Feature | Description | Effort | Impact | Priority |
|---------|-------------|--------|--------|----------|
| **Real-Time Collaborative Scoring** | Multiple reviewers can score candidates simultaneously. See live updates as team members submit scores. Aggregate scores with configurable weighting per reviewer role. | L | High | P1 |
| **@Mentions in Candidate Notes** | Tag team members in candidate notes using `@username`. Mentioned users receive notifications. Creates a threaded discussion history on each candidate. | M | Medium | P1 |
| **Shared Candidate Pools** | Create pools of candidates that span multiple jobs. When a candidate isn't right for one role, they remain visible for other open positions. Avoid re-processing the same resume. | M | High | P1 |
| **Interview Scorecards** | Structured interview feedback forms with predefined criteria (technical skills, culture fit, communication). Scorecards attached to specific pipeline stages. | M | High | P1 |
| **Hiring Committee Workflows** | For senior roles, route candidates through a committee review process. Require N approvals before advancing to the next stage. | L | Medium | P2 |

---

## Integrations

Third-party connections that extend the platform's ecosystem.

| Feature | Description | Effort | Impact | Priority |
|---------|-------------|--------|--------|----------|
| **LinkedIn Import** | Import candidate profiles directly from LinkedIn using the LinkedIn Recruiter API or manual profile URL input. Parse LinkedIn data into the standard candidate schema. | L | High | P1 |
| **Slack Notifications** | Send pipeline updates, new application alerts, and scoring results to configurable Slack channels. Support `/recruit` slash commands for quick actions. | M | Medium | P1 |
| **Google Calendar Integration** | Schedule interviews directly from the platform. Create calendar events with video call links, candidate details, and interview scorecards. Two-way sync for availability. | L | High | P1 |
| **Zoom / Microsoft Teams Integration** | Generate video interview links automatically when scheduling. Record interviews (with consent) and link recordings to candidate profiles. | M | Medium | P2 |
| **ATS Import / Export** | Import existing data from other ATS platforms (Greenhouse, Lever, JazzHR) via CSV or API. Export data for portability and compliance. | L | Medium | P2 |
| **HRIS Integration** | Push hired candidates to HR systems (BambooHR, Workday, Gusto) to streamline onboarding. Sync employee data back for alumni tracking. | L | Medium | P3 |
| **Webhook System** | Generic webhook support for custom integrations. Fire events on pipeline changes, new applications, scoring completion. JSON payloads with retry logic. | M | Medium | P2 |

---

## Advanced Analytics

Data-driven insights for hiring optimization and compliance.

| Feature | Description | Effort | Impact | Priority |
|---------|-------------|--------|--------|----------|
| **Diversity Metrics** | Track demographic diversity across the hiring pipeline (with candidate consent). Visualize drop-off rates by demographic group at each stage. Alert on statistically significant disparities. | L | High | P1 |
| **Bias Auditing Dashboard** | Automated fairness analysis of AI scoring. Compare score distributions across demographic groups. Generate compliance reports for [[AI Hiring Regulations]]. | L | High | P1 |
| **A/B Testing for Job Descriptions** | Test multiple versions of a job description and measure which attracts more qualified applicants. Track application rate, candidate quality scores, and diversity metrics per variant. | M | Medium | P2 |
| **Recruiter Performance Benchmarks** | Metrics per recruiter: time-to-fill, candidate quality (scores of hired candidates), pipeline velocity, offer acceptance rate. Team leaderboards and trend analysis. | M | Medium | P2 |
| **Funnel Analytics** | Detailed conversion funnels from sourcing to hire. Identify bottleneck stages. Compare funnel performance across jobs, departments, and time periods. | M | High | P1 |
| **Cost-per-Hire Tracking** | Track costs across sourcing channels, time investment, and tool usage. Calculate ROI per hiring channel. | M | Medium | P2 |

---

## Candidate Experience

Features that improve the candidate's interaction with the hiring process.

| Feature | Description | Effort | Impact | Priority |
|---------|-------------|--------|--------|----------|
| **Candidate Portal** | Branded portal where candidates can view their application status, upload additional documents, and communicate with recruiters. Reduces "black hole" application experience. | L | High | P1 |
| **Application Status Tracking** | Candidates receive real-time updates as they move through the pipeline. Visual progress bar showing current stage and expected timeline. | M | High | P1 |
| **Automated Rejection Emails** | Personalized rejection emails with constructive feedback. Multiple templates based on rejection stage (screening vs. final round). Configurable delay to avoid immediate rejection. | S | Medium | P1 |
| **Interview Self-Scheduling** | Candidates select their preferred interview slot from available times. Integrates with recruiter calendars. Reduces scheduling back-and-forth. | M | High | P2 |
| **Feedback Surveys** | Post-process surveys sent to candidates (hired and rejected) to measure candidate experience. NPS tracking and trend analysis. | S | Medium | P2 |

---

## Roadmap Prioritization

Features will be prioritized for the post-MVP roadmap using the **RICE framework**:

| Factor    | Definition                                    | Scale     |
|-----------|-----------------------------------------------|-----------|
| **Reach** | How many users/candidates benefit per quarter | 1-10      |
| **Impact**| How much does it improve conversion/satisfaction | 0.25-3x  |
| **Confidence** | How certain are we about estimates       | 50-100%   |
| **Effort**| Person-weeks to implement                     | 1-10      |

> **RICE Score** = (Reach × Impact × Confidence) / Effort

The first post-MVP sprint will focus on the highest-RICE features across all themes, likely including: **Candidate Portal**, **Diversity Metrics**, **Slack Notifications**, and **AI Job Description Generator**.
