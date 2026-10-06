"""
scoring_engine.py - category scores, overall score, risk level.

SCORE DIRECTION: 0 = lower assessed risk, 100 = higher assessed risk.

EDUCATIONAL ASSUMPTION: the weights and thresholds below are teaching values.
They must be validated/calibrated before being used for any professional
risk decision.
"""
import math
from services.questionnaire_data import CATEGORIES

DEFAULT_WEIGHTS = {c["key"]: c["weight"] for c in CATEGORIES}

# (upper bound inclusive, level). Scores are rounded half-up to an integer first.
DEFAULT_THRESHOLDS = [(20, "LOW"), (40, "MODERATE"), (70, "HIGH"), (100, "CRITICAL")]


def round_half_up(x):
    return int(math.floor(x + 0.5))


def validate_weights(weights):
    """Weights must cover every category, be non-negative and sum to 1.0."""
    keys = {c["key"] for c in CATEGORIES}
    if set(weights) != keys:
        raise ValueError("weights must define exactly these categories: " + ", ".join(sorted(keys)))
    if any((not isinstance(v, (int, float))) or v < 0 for v in weights.values()):
        raise ValueError("weights must be non-negative numbers")
    if abs(sum(weights.values()) - 1.0) > 0.001:
        raise ValueError("weights must sum to 1.0")
    return dict(weights)


def classify_risk(score, thresholds=None):
    """Map a 0-100 score to LOW / MODERATE / HIGH / CRITICAL."""
    thresholds = thresholds or DEFAULT_THRESHOLDS
    s = min(100, max(0, round_half_up(score)))
    for upper, level in thresholds:
        if s <= upper:
            return level
    return thresholds[-1][1]


def calculate_category_scores(features):
    """Weighted average of question risk (0-1) inside each category, scaled to 0-100."""
    scores = {}
    for cat in CATEGORIES:
        items = [i for i in features["items"] if i["category"] == cat["key"]]
        total_w = sum(i["weight"] for i in items)
        raw = sum(i["weight"] * i["risk"] for i in items) / total_w if total_w else 0.0
        scores[cat["key"]] = round(raw * 100, 1)
    return scores


def calculate_privacy_risk(features, weights=None, thresholds=None):
    """Combine category scores into the overall Privacy Risk Score using configurable weights."""
    weights = validate_weights(weights or DEFAULT_WEIGHTS)
    category_scores = calculate_category_scores(features)
    exact = sum(weights[k] * v for k, v in category_scores.items())
    overall = min(100, max(0, round_half_up(exact)))
    return {
        "overall_score": overall,
        "overall_exact": round(exact, 2),
        "risk_level": classify_risk(overall, thresholds),
        "category_scores": category_scores,
        "weights": weights,
    }
