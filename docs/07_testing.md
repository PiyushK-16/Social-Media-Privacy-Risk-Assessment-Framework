# Testing Strategy (Sections 33-34)

Run: `python -m pytest tests -v`. Every run regenerates **docs/TEST_RESULTS.md** (Test ID, Scenario, Input, Expected, Actual, Pass/Fail).

## Functional tests (tests/test_framework.py) - T01-T33
| IDs | What they prove |
|---|---|
| T01-T02 | Fully private -> 0/LOW; fully public -> 100/CRITICAL (extreme cases) |
| T03-T20 | Each exposure/weakness (phone, email, birthday, location, check-ins, travel, workplace, education, posts, unknown connections, tag review, MFA, login alerts, password reuse, apps, link awareness, old posts, settings review) creates the right finding |
| T21-T22 | Category and overall score maths verified by hand (e.g. phone only = 3/15 = 20.0) |
| T23-T25 | Boundary values 20/21, 40/41, 70/71 classify correctly |
| T26 | Recommendations generated and ordered IMMEDIATE first |
| T27 | Improvement simulation lowers the score and reports the correct reduction |
| T28 | Database save + read-back through the API |
| T29 | Sensitive data not stored: extra `phone` field rejected, no PII columns, canary string absent from DB dump |
| T30 | Report generation contains ID, level, checklist, disclaimer |
| T31-T33 | Weight validation, questionnaire has 40+ questions, local metadata tool strips EXIF/GPS from a copy |

## Security & privacy tests (tests/test_privacy_security.py) - S01-S12
| ID | Test | Why it matters |
|---|---|---|
| S01 | Missing answers rejected | Prevents partial/garbage scoring |
| S02 | Invalid value (`<script>`) rejected and not echoed | Input validation + XSS defence |
| S03 | Non-JSON rejected | Strict content handling |
| S04 | Malicious ID in URL gives 404, no reflection | Reflected-XSS check |
| S05 | Rate limit returns 429 | Abuse/DoS mitigation |
| S06 | DELETE needs token; cascade removes rows | Authorization + data deletion |
| S07 | CSP, nosniff, frame-deny, no-store headers | Browser-side hardening |
| S08 | Config read from environment; no secrets in source | Secure configuration |
| S09 | Retention purge removes old assessments | Retention limitation |
| S10 | 100 KB body returns 413 | Payload cap |
| S11 | No `Set-Cookie` | Stateless -> no session fixation/hijack surface |
| S12 | Clean JSON errors, no stack trace; unknown change IDs rejected | Safe error handling |

"Authentication if accounts are implemented": the app deliberately has **no accounts**, so there is no password or session store to protect.

**Result of the latest run: 45 passed, 0 failed.**
