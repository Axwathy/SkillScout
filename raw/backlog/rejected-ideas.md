---
type: backlog
title: "Rejected Ideas"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/feature, product/strategy, ethics]
---

# Rejected Ideas

This document records feature ideas that were explicitly rejected for the AI Recruitment SaaS platform. Each entry includes the reasoning behind the rejection to serve as institutional memory and prevent these ideas from being re-proposed without addressing the original concerns.

See also: [[AI Hiring Regulations]], [[future-features|Future Features]]

---

## AI Emotion Detection

**Status**: ❌ Permanently Rejected

**Proposal**: Analyze candidate video interviews to detect emotions (confidence, nervousness, enthusiasm) using facial expression analysis and vocal tone processing.

**Rejection Reasons**:

- **Pseudoscience**: The scientific consensus does not support reliable emotion detection from facial expressions. Lisa Feldman Barrett's research demonstrates that facial movements do not map consistently to internal emotional states across individuals and cultures.
- **Legal risk**: The **EU AI Act** (Article 5) explicitly prohibits emotion recognition systems in employment contexts. Similar restrictions are emerging in US state legislation (Illinois BIPA, NYC Local Law 144).
- **Demographic bias**: Emotion detection models show significant accuracy disparities across racial groups, genders, and neurodivergent individuals. Candidates with autism spectrum conditions or cultural differences in emotional expression would be systematically disadvantaged.
- **Reputational risk**: [[HireVue]]'s use of facial analysis in hiring assessments led to widespread backlash, an FTC complaint, and eventual removal of the feature. We should learn from their experience, not repeat it.

**Verdict**: No amount of technical improvement can overcome the fundamental scientific and ethical problems with this approach.

---

## AI Lie Detection

**Status**: ❌ Permanently Rejected

**Proposal**: Use AI to analyze verbal and non-verbal cues during interviews to detect deception or dishonesty.

**Rejection Reasons**:

- **Unreliable**: No credible peer-reviewed evidence supports AI-based lie detection. Even traditional polygraph tests achieve only 60-70% accuracy — barely above chance.
- **False positives**: Nervous candidates (especially those from marginalized backgrounds, non-native speakers, or those with social anxiety) would be disproportionately flagged as "deceptive."
- **Harmful**: False accusations of dishonesty cause real harm to candidates and expose the company to defamation liability.
- **Legal exposure**: Using unvalidated lie detection in employment decisions would likely violate anti-discrimination laws and could constitute unfair labor practices.

**Verdict**: The technology does not exist in any reliable form. Building features around it would be irresponsible.

---

## Blockchain Hiring

**Status**: ❌ Rejected (Revisit if Scale Demands)

**Proposal**: Store candidate credentials and hiring records on a blockchain for tamper-proof verification and decentralized identity.

**Rejection Reasons**:

- **Unnecessary complexity**: Credential verification at our scale (hundreds to thousands of candidates) does not require decentralized consensus. A signed database record achieves the same integrity guarantees with far less complexity.
- **Infrastructure overhead**: Running or integrating with blockchain nodes adds operational burden, latency, and cost with no corresponding user benefit.
- **GDPR conflict**: The immutability of blockchain fundamentally conflicts with GDPR's "right to be forgotten" (Article 17). Candidate data must be deletable upon request.
- **No user demand**: No recruiter or hiring manager has ever expressed a need for blockchain-based credential storage. The problem it solves doesn't exist for our users.

**Verdict**: A solution in search of a problem. Revisit only if the industry standardizes on blockchain-based credentials (unlikely in our time horizon).

---

## Social Media Personality Scoring

**Status**: ❌ Permanently Rejected

**Proposal**: Analyze candidates' public social media profiles (Twitter/X, Facebook, Instagram) to generate personality assessments and cultural fit scores.

**Rejection Reasons**:

- **Privacy concerns**: Scraping social media profiles without explicit consent violates candidate privacy expectations and potentially violates platform terms of service.
- **Bias amplification**: Social media profiles are proxies for age, ethnicity, socioeconomic status, religion, political views, and other protected characteristics. Any scoring based on this data would introduce protected-class discrimination.
- **GDPR / CCPA violations**: Processing personal data from social media for employment decisions requires explicit consent and a legitimate basis — which is nearly impossible to establish when candidates don't know their profiles are being analyzed.
- **Legal precedent**: Multiple jurisdictions (Maryland, Illinois, New York) have enacted laws restricting or prohibiting employer access to candidate social media accounts.
- **Data quality**: Social media personas are curated representations, not accurate reflections of workplace behavior. Any personality assessment derived from them would be unreliable.

**Verdict**: Fundamentally incompatible with ethical hiring and privacy law.

---

## Gamified Resume Review

**Status**: ❌ Rejected

**Proposal**: Turn resume review into a gamified experience with points, badges, and leaderboards for recruiters who review the most resumes or make the fastest decisions.

**Rejection Reasons**:

- **Trivializes the process**: Hiring decisions affect people's livelihoods. Gamification incentivizes speed over quality and reduces candidates to game objects.
- **Perverse incentives**: Leaderboards and points encourage racing through reviews rather than careful evaluation. This directly undermines the quality of hiring decisions.
- **Professionalism**: Our brand positioning emphasizes thoughtful, AI-augmented hiring. Gamification signals the opposite — that we don't take the process seriously.
- **Candidate perception**: If candidates learned their resumes were being "gamified," it would severely damage trust and employer brand.

**Verdict**: Gamification has its place, but hiring decisions is not one of them.

---

## AI Video Facial Analysis

**Status**: ❌ Permanently Rejected

**Proposal**: Analyze candidate video interviews using computer vision to assess traits like "professionalism," "engagement," and "leadership potential" from facial features, eye contact, and body language.

**Rejection Reasons**:

- **Proven demographic bias**: Multiple independent studies (Rhue 2018, Buolamwini & Gebru 2018) demonstrate that facial analysis systems exhibit significant racial and gender bias. Accuracy rates for dark-skinned women can be 35% lower than for light-skinned men.
- **[[HireVue]] precedent**: HireVue used facial analysis in hiring assessments for years before removing the feature in 2021 due to scientific criticism, public backlash, and an EPIC complaint to the FTC. They acknowledged the technology was not sufficiently validated.
- **Legal liability**: NYC Local Law 144 requires bias audits for automated employment decision tools. Facial analysis would almost certainly fail these audits. The EU AI Act classifies such systems as "high risk" or "prohibited" depending on implementation.
- **No scientific validity**: There is no peer-reviewed evidence that facial features predict job performance. Physiognomy — judging character from appearance — is a discredited pseudoscience.
- **Accessibility**: Candidates with visible disabilities, facial differences, or who use assistive devices would be systematically disadvantaged.

**Verdict**: This technology is harmful, biased, and legally toxic. It should never be implemented.

---

## Automated Background Checks Without Consent

**Status**: ❌ Permanently Rejected

**Proposal**: Automatically run background checks on candidates when they enter the pipeline, before obtaining explicit consent.

**Rejection Reasons**:

- **Illegal**: The Fair Credit Reporting Act (FCRA) requires written consent before conducting background checks. Violating this carries statutory damages of $100-$1,000 per candidate plus punitive damages.
- **Ethical**: Candidates have the right to know what information is being gathered about them and to provide context for anything that appears negative.
- **Ban-the-box movement**: Many jurisdictions prohibit background checks until after a conditional offer is made. Automating early checks would violate these laws.

**Verdict**: Background checks must always be opt-in, transparent, and conducted at the appropriate stage of the hiring process.

---

## Voice-Based Personality Assessment

**Status**: ❌ Rejected

**Proposal**: Analyze voice patterns (pitch, speed, cadence, pauses) during phone screens to generate personality trait scores.

**Rejection Reasons**:

- **Scientific validity**: While some research suggests correlations between vocal features and personality traits, the effect sizes are small and not reliable enough for high-stakes employment decisions.
- **Accent bias**: Voice analysis systems are biased against non-native speakers, regional accents, and speech impediments. This creates disparate impact against candidates from diverse linguistic backgrounds.
- **Consent issues**: Recording and analyzing voice data requires explicit consent under wiretapping laws (many US states are two-party consent states).

**Verdict**: Interesting research area but not appropriate for employment decisions at current accuracy levels.

---

## Summary Matrix

| Idea | Primary Risk | Legal Exposure | Reputational Risk | Revisit? |
|------|-------------|----------------|-------------------|----------|
| AI Emotion Detection | Pseudoscience | High (EU AI Act) | Severe | Never |
| AI Lie Detection | Unreliable | High | Severe | Never |
| Blockchain Hiring | Complexity | Low (GDPR) | Low | Maybe |
| Social Media Scoring | Privacy/Bias | High (GDPR/CCPA) | Severe | Never |
| Gamified Resume Review | Professionalism | Low | Medium | Never |
| AI Video Facial Analysis | Bias | High (multiple laws) | Severe | Never |
| Background Checks w/o Consent | Illegal | Very High (FCRA) | High | Never |
| Voice Personality Assessment | Bias | Medium | Medium | Maybe |
