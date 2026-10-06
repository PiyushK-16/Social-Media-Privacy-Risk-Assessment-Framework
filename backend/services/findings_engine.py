"""
findings_engine.py - turns risky answers into ranked, human-readable findings.
"""
from services.questionnaire_data import (QUESTION_BY_ID, CATEGORY_BY_KEY, SEVERITY_RANK,
                                         FINDING_THRESHOLD)


def generate_privacy_findings(features, scoring):
    """Return {'overall','level','findings':[...],'top_risks':[...],'category_scores'}.

    A finding is created for every question whose risk value is >= FINDING_THRESHOLD
    (risky answer, 'sometimes' or 'not sure'). Findings are ranked by severity,
    then by (question weight x risk x category weight).
    """
    findings = []
    for item in features["items"]:
        if item["risk"] < FINDING_THRESHOLD:
            continue
        q = QUESTION_BY_ID[item["id"]]
        cat_weight = scoring["weights"][q["category"]]
        findings.append({
            "question_id": q["id"],
            "category": q["category"],
            "category_label": CATEGORY_BY_KEY[q["category"]]["label"],
            "finding_type": q["finding_type"],
            "severity": q["severity"],
            "description": q["finding"] + (" (answer was 'not sure')" if item["answer"] == "NOT_SURE" else ""),
            "risk": item["risk"],
            "_rank": (SEVERITY_RANK[q["severity"]], q["weight"] * item["risk"] * cat_weight),
        })
    findings.sort(key=lambda f: f["_rank"], reverse=True)
    for f in findings:
        del f["_rank"]
    return {
        "overall": scoring["overall_score"],
        "level": scoring["risk_level"],
        "findings": findings,
        "top_risks": [f["description"] for f in findings[:5]],
        "category_scores": scoring["category_scores"],
    }


def format_findings_text(result):
    """Plain-text summary (handy for the CLI demo and README examples)."""
    lines = [f"OVERALL PRIVACY RISK: {result['overall_score']}/100", f"LEVEL: {result['risk_level']}", "", "TOP RISKS:"]
    for i, f in enumerate(result["findings"][:5], 1):
        lines.append(f"  {i}. {f['description']}")
    lines += ["", "CATEGORY SCORES:"]
    for key, val in result["category_scores"].items():
        lines.append(f"  {CATEGORY_BY_KEY[key]['label']}: {val}/100")
    return "\n".join(lines)
