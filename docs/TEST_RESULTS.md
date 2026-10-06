# Automated Test Results

| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|
| S01 | Input validation: missing answers | only 3 answers sent | 400 listing missing IDs | Matched expected result | PASS |
| S02 | Input validation: invalid value | B1='<script>alert(1)</script>' | 400 and payload not echoed back | Matched expected result | PASS |
| S03 | Input validation: wrong content type | form-encoded body | 400 | Matched expected result | PASS |
| S04 | XSS protection | malicious assessment ID in URL | 404 and no reflection of the payload | Matched expected result | PASS |
| S05 | API rate limiting | 7 requests with limit 5/min | first 5 allowed, then 429 | Matched expected result | PASS |
| S06 | Authorization & data deletion | DELETE without/with token | 403 without, 200 with, then 404 | Matched expected result | PASS |
| S07 | Secure headers | GET /api/privacy-checklist | CSP, nosniff, frame deny, no-store present | Matched expected result | PASS |
| S08 | Environment variables | RATE_LIMIT_PER_MINUTE=7 and RETENTION_DAYS=5 in env | app reads them; no secrets in source | Matched expected result | PASS |
| S09 | Retention limitation | assessment older than 90 days | purge removes it, newer one stays | Matched expected result | PASS |
| S10 | Payload size limit | 100 KB JSON body | 413 | Matched expected result | PASS |
| S11 | Secure session handling | normal assessment flow | no Set-Cookie header (stateless app) | Matched expected result | PASS |
| S12 | Error handling | unknown route and unknown JSON field | clean JSON errors, no stack trace | Matched expected result | PASS |
| T01 | Fully private profile | all safest answers | score 0, LOW, no findings | Matched expected result | PASS |
| T02 | Fully public synthetic profile | all riskiest answers | score 100, CRITICAL, 44 findings | Matched expected result | PASS |
| T03 | Public phone | B1=YES | PUBLIC_PHONE finding and personal_info score > 0 | Matched expected result | PASS |
| T04 | Public email | B2=YES | PUBLIC_EMAIL finding | Matched expected result | PASS |
| T05 | Public birthday | B3=YES | PUBLIC_BIRTHDAY finding (HIGH) | Matched expected result | PASS |
| T06 | Public location (geotags + inferable home/work) | C2=YES,C5=YES | location findings, score > 0 | Matched expected result | PASS |
| T07 | Real-time check-ins | C1=YES,C3=YES | REALTIME_LOCATION + LIVE_CHECKINS | Matched expected result | PASS |
| T08 | Travel plans public | C4=YES | PUBLIC_TRAVEL_PLANS finding | Matched expected result | PASS |
| T09 | Workplace exposure | B5=YES | PUBLIC_WORKPLACE finding | Matched expected result | PASS |
| T10 | Education exposure | B6=YES | PUBLIC_EDUCATION finding | Matched expected result | PASS |
| T11 | Public posts | D1=PUBLIC | PUBLIC_POSTS finding | Matched expected result | PASS |
| T12 | Unknown connections accepted | E1=YES | UNKNOWN_CONNECTIONS_ACCEPTED, connections score > 0 | Matched expected result | PASS |
| T13 | Tag review disabled | F2=NO | TAG_REVIEW_DISABLED finding | Matched expected result | PASS |
| T14 | MFA disabled | G1=NO | MFA_DISABLED (HIGH) and account_security score > 0 | Matched expected result | PASS |
| T15 | Login alerts disabled | G4=NO | LOGIN_ALERTS_DISABLED finding | Matched expected result | PASS |
| T16 | Password reuse reported | G2=YES | PASSWORD_REUSE finding | Matched expected result | PASS |
| T17 | Third-party apps not reviewed | H1=NO | THIRD_PARTY_APPS_NOT_REVIEWED finding | Matched expected result | PASS |
| T18 | Suspicious-link awareness low | I1=NO | LOW_LINK_AWARENESS finding | Matched expected result | PASS |
| T19 | Old posts not reviewed | J1=NO | OLD_POSTS_NOT_REVIEWED finding | Matched expected result | PASS |
| T20 | Privacy settings not reviewed | J4=NO | SETTINGS_NOT_REVIEWED finding | Matched expected result | PASS |
| T21 | Category score maths | B1 risky only (weight 3 of 15) | personal_info = 20.0 | Matched expected result | PASS |
| T22 | Overall score maths | all personal_info risky only (weight 15%) | overall 15, LOW | Matched expected result | PASS |
| T23 | Score boundary 20 | 20 and 21 | 20 -> LOW, 21 -> MODERATE | Matched expected result | PASS |
| T24 | Score boundary 40 | 40 and 41 | 40 -> MODERATE, 41 -> HIGH | Matched expected result | PASS |
| T25 | Score boundary 70 | 70 and 71 | 70 -> HIGH, 71 -> CRITICAL | Matched expected result | PASS |
| T26 | Recommendation generation | MFA off + public phone + live location | IMMEDIATE recs listed first | Matched expected result | PASS |
| T27 | Improvement simulation | fix MFA, phone, live location | after < before, reduction = difference | Matched expected result | PASS |
| T28 | Database save | POST assessment then GET it | 201, stored score matches, findings stored | Matched expected result | PASS |
| T29 | Sensitive data not stored | extra 'phone' field rejected; DB has no PII columns | 400, no sensitive column names | Matched expected result | PASS |
| T30 | Report generation | GET report for stored assessment | 200 HTML with ID, level, disclaimer, checklist | Matched expected result | PASS |
| T31 | Custom weights must sum to 1 | weights summing to 1.2 | ValueError; valid custom weights change the score | Matched expected result | PASS |
| T32 | Questionnaire has 40+ questions across 10 categories | read questionnaire | 44 questions, 10 categories | Matched expected result | PASS |
| T33 | Local metadata tool | JPEG with EXIF+GPS then --strip | metadata read locally, clean copy has none, original untouched | Matched expected result | PASS |

**45 / 45 tests passed.**
