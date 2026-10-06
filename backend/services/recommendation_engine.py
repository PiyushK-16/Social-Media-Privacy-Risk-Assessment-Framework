"""
recommendation_engine.py - personalised, prioritised recommendations.
Priorities: IMMEDIATE > IMPORTANT > GOOD PRACTICE.
"""
from services.questionnaire_data import QUESTIONS, PRIORITY_RANK, SEVERITY_RANK

# One recommendation per finding type (also used to seed the RECOMMENDATIONS table).
RECOMMENDATION_CATALOG = [
    {"finding_type": q["finding_type"], "recommendation": q["recommendation"], "priority": q["priority"]}
    for q in QUESTIONS
]
_BY_TYPE = {r["finding_type"]: r for r in RECOMMENDATION_CATALOG}

GENERAL_RECOMMENDATION = {
    "finding_type": "GENERAL_REVIEW",
    "recommendation": "Your answers show few weaknesses. Keep reviewing privacy settings every 3-6 months.",
    "priority": "GOOD PRACTICE",
}


def recommendations_for_types(finding_types, severity_by_type=None):
    """Return recommendation dicts for a list of finding types, ordered by priority."""
    severity_by_type = severity_by_type or {}
    recs = [dict(_BY_TYPE[t]) for t in finding_types if t in _BY_TYPE]
    recs.sort(key=lambda r: (PRIORITY_RANK[r["priority"]], SEVERITY_RANK.get(severity_by_type.get(r["finding_type"]), 0)),
              reverse=True)
    return recs or [dict(GENERAL_RECOMMENDATION)]


def generate_recommendations(findings):
    """Personalised recommendations for the list of findings produced by the findings engine."""
    severities = {f["finding_type"]: f["severity"] for f in findings}
    return recommendations_for_types([f["finding_type"] for f in findings], severities)
