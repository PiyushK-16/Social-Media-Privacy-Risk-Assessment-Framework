# Privacy by Design, Storage & Database (Sections 24, 25, 39)

## What is stored (and what is not)
| Stored | Never stored |
|---|---|
| assessment_id, overall_score, risk_level, created_at | phone number, personal e-mail, home address |
| category scores | birth date, passwords |
| finding types (+category, severity, description) | exact location, private messages |
| hash of the delete token | raw questionnaire answers, IP addresses |

The questionnaire never *asks* for the sensitive items, and the server never persists raw answers.

## Database schema (SQLite)
```
ASSESSMENTS      assessment_id PK | overall_score | risk_level | created_at | delete_token_hash
CATEGORY_SCORES  category_score_id PK | assessment_id FK | category | score
FINDINGS         finding_id PK | assessment_id FK | category | finding_type | severity | description
RECOMMENDATIONS  recommendation_id PK | finding_type (unique) | recommendation | priority
```
Foreign keys use `ON DELETE CASCADE`, so deleting an assessment removes its scores and findings. `RECOMMENDATIONS` is a static catalogue seeded from code.

## Privacy by Design principles in this app
| Principle | How the application applies it |
|---|---|
| Data minimisation | Choice-only questions; no free text; only scores/finding types stored. |
| Purpose limitation | Data is used only to produce the assessment, report and anonymous trends. |
| Least privilege | No accounts, no social-platform API access, no scraping; the app can read nothing about the user's real profiles. DB has no sensitive columns. |
| Privacy by default | Nothing is stored beyond the minimum; dashboard uses synthetic data; no cookies. |
| Transparency | Home page, questionnaire and report state what is/is not collected and the disclaimer. |
| User control | Delete endpoint with secret token; local-only metadata tool; users can simply not submit (answers stay in the browser until submit). |
| Retention limitation | `RETENTION_DAYS` (default 90) purges old assessments on startup. |
| Secure processing | Strict validation, XSS-safe rendering (textContent / Jinja autoescape), CSP & security headers, rate limiting, payload cap, no stack traces, env-based config. |
