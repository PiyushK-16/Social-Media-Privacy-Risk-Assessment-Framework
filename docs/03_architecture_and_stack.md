# Architecture, Technology Stack & Folder Structure (Sections 27-29)

## System architecture
```
User
 -> Privacy Questionnaire (44 questions, choices only)
 -> Input Validation (utils/validation.py)
 -> Feature Extraction (extract_privacy_features)
 -> +-------------------------------------------+
    | Category analysers (scoring_engine):      |
    | Profile | Personal Info | Location |      |
    | Content | Connections | Tagging |         |
    | Account Security | Third-Party Apps |     |
    | Social Engineering | Digital Footprint |  |
    +-------------------------------------------+
 -> Category Scores (0-100 each)
 -> Risk Scoring Engine (calculate_privacy_risk, configurable weights)
 -> Overall Risk + Level (LOW / MODERATE / HIGH / CRITICAL)
 -> Findings Engine (generate_privacy_findings)
 -> Recommendation Engine (generate_recommendations)
 -> Privacy Dashboard + Privacy Report
 Optional: anonymised aggregates -> analytics (synthetic dataset only)
```
Design choice: one data table (`services/questionnaire_data.py`) drives questions, scoring, findings and recommendations, so adding a question is a one-line change.

## Technology options
| | Option A - Beginner (chosen) | Option B - Modern |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | React |
| Backend | Python Flask | FastAPI |
| Database | SQLite | PostgreSQL / SQLite |
| Charts | Chart.js | Recharts / Chart.js |
| Reports | Printable HTML (Save as PDF) | Server-side PDF |
| Advantages | Few moving parts, runs anywhere, easy to explain in an interview | Typed validation, auto OpenAPI docs, scalable, component reuse |
| Limitations | Manual validation, no auto docs, in-memory rate limiter | Steeper learning curve, more tooling (Node, build step) |

**Recommendation for a student: Option A.** It lets you finish, test and explain every line. Mention Option B (FastAPI + React) under "Future improvements".

## Folder structure
```
Social-Media-Privacy-Risk-Assessment/
├── backend/                  Python server
│   ├── app.py                App factory: config, security headers, rate limit, error handlers
│   ├── routes/api.py         REST endpoints (thin: validate -> call service -> respond)
│   ├── models/database.py    SQLite schema + privacy-first persistence, delete, retention
│   ├── services/             Business logic (no web code)
│   │   ├── questionnaire_data.py   44 questions, categories, answer->risk rules, recommendations
│   │   ├── assessment_engine.py    Feature extraction + pipeline orchestration
│   │   ├── scoring_engine.py       Category + overall scoring, thresholds, weights
│   │   ├── findings_engine.py      Ranked findings
│   │   ├── recommendation_engine.py Prioritised recommendations
│   │   ├── improvement_simulator.py "What if I improve my settings?"
│   │   └── analytics.py            Dashboard aggregates from the synthetic dataset
│   ├── utils/                validation, rate limiter, checklist
│   └── templates/report.html Printable report template (auto-escaped)
├── frontend/                 index / assessment / dashboard pages, css/, js/
├── data/                     generate_dataset.py + social_media_privacy_assessments.csv (1,000 synthetic rows)
├── tools/metadata_tool.py    Optional local EXIF viewer/cleaner
├── scripts/run_demo.py       Fictional demo profile + simulation
├── reports/                  Place exported reports here (git-ignored)
├── tests/                    pytest suite (functional + security/privacy)
├── screenshots/              Proof screenshots for README/LinkedIn
├── docs/                     Documentation, report, interview prep
├── README.md  requirements.txt  .env.example  .gitignore
```
