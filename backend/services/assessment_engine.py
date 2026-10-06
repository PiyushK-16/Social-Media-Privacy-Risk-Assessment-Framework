"""
assessment_engine.py - the pipeline orchestrator.

Questionnaire answers -> feature extraction -> category scores -> overall score
-> findings -> recommendations.   Nothing here touches the database.
"""
from services.questionnaire_data import (QUESTIONS, risk_for_answer, is_protective)
from services.scoring_engine import calculate_privacy_risk
from services.findings_engine import generate_privacy_findings
from services.recommendation_engine import generate_recommendations

DISCLAIMER = ("This is an educational privacy-risk framework based on self-reported answers. "
              "It is not a guarantee that an account will or will not be compromised. Weights and "
              "thresholds are educational assumptions that should be validated before any "
              "professional risk decision.")


def extract_privacy_features(responses):
    """Convert validated answers into numeric risk features (0 = safe ... 1 = riskiest).

    Returns a structured dictionary:
      items          - one entry per question (feature name, category, risk 0-1, weight)
      risk_by_feature- {feature_name: risk}
      controls       - how many protective controls (MFA, alerts, ...) are fully enabled
    """
    items, risk_by_feature, control_flags = [], {}, {}
    for q in QUESTIONS:
        answer = responses[q["id"]]
        risk = risk_for_answer(q, answer)
        items.append({"id": q["id"], "category": q["category"], "feature": q["feature"],
                      "answer": answer, "risk": risk, "weight": q["weight"]})
        risk_by_feature[q["feature"]] = risk
        if is_protective(q):
            control_flags[q["feature"]] = (risk == 0.0)
    return {"items": items, "risk_by_feature": risk_by_feature,
            "controls": {"enabled": sum(control_flags.values()), "total": len(control_flags),
                         "by_feature": control_flags}}


def run_assessment(responses, weights=None, thresholds=None):
    """Run the full pipeline for ONE validated response set and return a result dict."""
    features = extract_privacy_features(responses)
    scoring = calculate_privacy_risk(features, weights, thresholds)
    findings = generate_privacy_findings(features, scoring)
    recommendations = generate_recommendations(findings["findings"])
    return {
        "overall_score": scoring["overall_score"],
        "risk_level": scoring["risk_level"],
        "category_scores": scoring["category_scores"],
        "findings": findings["findings"],
        "top_risks": findings["top_risks"],
        "recommendations": recommendations,
        "controls": {"enabled": features["controls"]["enabled"], "total": features["controls"]["total"]},
        "disclaimer": DISCLAIMER,
    }
