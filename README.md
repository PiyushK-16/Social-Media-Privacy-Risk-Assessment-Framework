# Social Media Privacy Risk Assessment Framework

> This project is designed for defensive cybersecurity and privacy education. It uses synthetic or voluntarily provided assessment responses and does not scrape, track, or profile real social-media users.

## Overview
A privacy-risk assessment platform. A user answers 44 choice-based questions about their social-media settings and habits; the framework returns a 0-100 **Privacy Risk Score** (higher = more exposure), a risk level, ten category scores, findings, prioritised recommendations, an improvement simulator, a dashboard and a printable report.

## Problem Statement
People overshare and leave weak settings without noticing how public details, location, third-party apps and weak account security combine into privacy and social-engineering risk. Few tools explain this without collecting even more personal data.

## Objectives
- Assess exposure from **self-reported** settings only.
- Explain risks in plain language and prioritise fixes.
- Demonstrate privacy-by-design (minimal storage, deletion, retention).
- Provide an aggregate dashboard using **synthetic** data.

## Cybersecurity Relevance
Risk scoring, account-takeover/phishing awareness, identity protection, least privilege for third-party apps, secure API design, GRC-style assumptions and reporting. See `docs/02_industry_relevance.md`.

## Privacy vs Security
Privacy controls how personal information is exposed and used; security protects accounts and systems. Strong security does not equal strong privacy (a user with MFA can still publish live locations). See `docs/01_concepts_and_education.md`.

## Features
44-question assessment - input validation - feature extraction - 10 category scores - configurable weights - findings engine - recommendation engine - improvement simulator - radar/bar charts - dashboard (6 charts) - printable HTML report - privacy checklist - privacy-first SQLite storage - REST API - 1,000-row synthetic dataset - local EXIF metadata tool - 45 automated tests.

## Architecture
```
User -> Questionnaire -> Validation -> Feature Extraction -> Category Analysis -> Scoring Engine
 -> Overall Score -> Risk Level -> Findings -> Recommendations -> Dashboard -> Report
```
Details: `docs/03_architecture_and_stack.md`.

## Technology Stack
Python 3 + Flask, SQLite, HTML/CSS/JavaScript, Chart.js, pytest, Pillow (metadata tool). (Option B - React + FastAPI - discussed in docs.)

## Privacy Questionnaire
44 questions in 10 categories A-J: Profile Visibility, Personal Information, Location, Posts & Content, Friends/Followers, Tagging, Authentication & Account Security, Third-Party Apps, Messaging & Social Engineering, Digital Footprint. Answers: YES/NO/SOMETIMES/NOT SURE or PUBLIC/FRIENDS/PRIVATE. The app never asks for the actual phone number, e-mail, address or birth date. Source: `backend/services/questionnaire_data.py`.

## Risk Categories
Profile Exposure, Personal Information, Location Exposure, Content Exposure, Connection Risk, Tagging Risk, Account Security, Third-Party App Risk, Social Engineering, Digital Footprint. Each 0-100 (0 = lower assessed risk, 100 = higher).

## Risk Scoring
Answer -> risk value (0, 0.4 friends, 0.5 sometimes, 0.6 not sure, 1) -> weighted average per category -> weighted overall score.

| Category | Weight | | Category | Weight |
|---|---|---|---|---|
| Profile | 10% | | Account Security | 15% |
| Personal Info | 15% | | Third-Party Apps | 5% |
| Location | 15% | | Social Engineering | 10% |
| Content | 10% | | Digital Footprint | 5% |
| Connections | 10% | | Tagging | 5% |

Levels: **0-20 LOW, 21-40 MODERATE, 41-70 HIGH, 71-100 CRITICAL** (score rounded half-up first). Weights/thresholds are **educational assumptions** that must be validated before any professional risk decision; this is not a guarantee an account will or will not be compromised. Weights are configurable via `RISK_WEIGHTS` in `.env`.

## Privacy Findings
`generate_privacy_findings()` creates a finding for each risky/uncertain answer, ranked by severity then weighted impact.

## Recommendation Engine
`generate_recommendations()` maps findings to actions grouped as IMMEDIATE, IMPORTANT, GOOD PRACTICE.

## Improvement Simulator
Re-scores a copy of the answers with chosen fixes applied (stateless). Framework simulation only. Demo: 70/100 HIGH -> 32/100 MODERATE (38-point reduction) - see `docs/DEMO_RESULTS.md`.

## Digital Footprint
Self-reported review habits for old posts, unused accounts, public comments and settings reviews (active vs passive footprint explained in docs).

## Social Engineering Awareness
Scores risky behaviours and explains defensively how public context can make scams convincing. No attack scripts.

## Account Security
MFA, password reuse, password manager, login alerts, session review, recovery info.

## Privacy Dashboard
`/dashboard.html`: summary cards plus six charts (category risk, risk distribution, top weaknesses, account controls, digital-footprint distribution, improvement comparison) over synthetic data.

## Privacy Report
`/api/assessment/{id}/report` - ID, date, score, level, categories, findings, priority actions, recommendations, checklist, disclaimer. Print to PDF from the browser. Contains no sensitive data.

## Privacy by Design
Data minimisation, purpose limitation, least privilege, privacy by default, transparency, user control (delete token), retention limit (90 days), secure processing. See `docs/04_privacy_by_design_and_data.md`.

## Installation
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python data/generate_dataset.py
```

## Usage
```bash
python backend/app.py        # open http://127.0.0.1:5000
python scripts/run_demo.py   # fictional demo profile
python tools/metadata_tool.py photo.jpg --strip
```

## API Documentation
`docs/05_api.md` (endpoints: questionnaire, assessment, recommendations, report, simulate-improvement, dashboard stats, privacy-checklist, delete).

## Testing
`python -m pytest tests -v` -> 45 tests (33 functional + 12 security/privacy). Results table: `docs/TEST_RESULTS.md`. Strategy: `docs/07_testing.md`.

## Security & Privacy Testing
Verified: no PII columns or canary data in the database, strict validation, XSS-safe handling, rate limiting (429), security headers, token-protected deletion with cascade, retention purge, no cookies, no stack traces, env-based config.

## Results
- 1,000 synthetic profiles: average score 49.8; LOW 180, MODERATE 263, HIGH 283, CRITICAL 274.
- Most common weaknesses in the synthetic data: old posts not reviewed (71%), third-party apps not reviewed (70%), sessions not reviewed (69%).
- Average score if IMMEDIATE fixes were applied: 42.5; after IMMEDIATE + IMPORTANT fixes: 7.4 (framework simulation).
- Tests: 45 / 45 passed.

## Limitations
Self-reported answers can be wrong; weights and thresholds are assumptions not calibrated on real incident data; synthetic data reflects my generator's assumptions, not real populations; platform-specific settings differ; in-memory rate limiter and no user accounts are suited to a learning project, not production.

## Future Improvements
Platform-specific checklists, configurable organisational policies, awareness quizzes, privacy-maturity scoring, teen/family safety modules, enterprise training and GRC reporting, anonymous organisational trends, model calibration, localisation, accessibility, report comparison over time, client-side-only mode. (No invasive monitoring or scraping.)

## Screenshots
Add images to `screenshots/` using `docs/09_screenshot_checklist.md`.

## Learning Outcomes
Risk modelling, secure Flask API design, input validation, privacy-by-design, threat modelling, test automation, data visualisation, technical documentation and Git workflow.

## Ethical Disclaimer
Defensive education only. No scraping, tracking, profiling, account enumeration or access to private accounts. Use only on your own settings or fictional data.

## Author
`Piyush K. Ahirwar`· [GitHub](https://github.com/PiyushK-16) · [LinkedIn](https://www.linkedin.com/in/piyush-k-ahirwar-658633261)
