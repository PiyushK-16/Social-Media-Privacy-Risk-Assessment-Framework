# REST API (Section 26)

Base URL `http://127.0.0.1:5000`. All bodies are JSON. Errors use `{"error": {"code", "message", "details?"}}`.

**Authentication / authorization.** There are no user accounts (data minimisation). Assessment IDs are random and unguessable (`PRA-` + 16 hex). Reading uses the ID as a capability; **deleting requires the secret `X-Delete-Token`** returned once at creation (only its SHA-256 hash is stored, compared in constant time).

| Method & path | Request | Success response | Validation / errors | Privacy notes |
|---|---|---|---|---|
| `GET /api/questionnaire` | - | 44 questions, categories, disclaimer | - | No scoring logic exposed |
| `POST /api/assessment` | `{"responses": {"A1":"PUBLIC", ... all 44 IDs}}` | `201` id, delete_token, scores, level, findings, recommendations | `400` missing/invalid/unknown fields (unknown keys are not echoed), `415/400` non-JSON, `413` >32 KB, `429` rate limit | Raw answers are not stored |
| `GET /api/assessment/{id}` | - | stored scores, level, findings, created_at | `404` bad/unknown id | Minimal data only |
| `GET /api/assessment/{id}/recommendations` | - | recommendations ordered IMMEDIATE > IMPORTANT > GOOD PRACTICE | `404` | Derived from finding types |
| `GET /api/assessment/{id}/report[?download=1]` | - | printable HTML report | `404` | Built only from stored minimal data |
| `POST /api/assessment/simulate-improvement` | `{"responses": {...}, "changes": ["B1","G1"]}` or `{"B1":"PRIVATE"}` | current vs simulated score, reduction, applied changes | `400` unknown ids/answers | Stateless - nothing stored |
| `GET /api/dashboard/stats` | - | aggregates from synthetic dataset + live counts | - | Synthetic data only |
| `GET /api/privacy-checklist[?format=txt]` | - | checklist JSON or text download | - | - |
| `DELETE /api/assessment/{id}` | header `X-Delete-Token` | `{"deleted": true}` | `403` bad token, `404` | Cascades to scores/findings |

Example:
```bash
curl -s -X POST http://127.0.0.1:5000/api/assessment -H "Content-Type: application/json" \
     -d @sample_responses.json
```
