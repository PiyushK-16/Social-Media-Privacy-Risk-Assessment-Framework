"""
analytics.py - aggregate dashboard statistics from the SYNTHETIC dataset.
Nothing here uses real people's data.
"""
import csv
import os
from pathlib import Path
from services.questionnaire_data import (QUESTIONS, CATEGORIES, QUESTION_BY_ID, is_protective,
                                         FINDING_THRESHOLD, risk_for_answer)
from services.assessment_engine import run_assessment, DISCLAIMER
from services.improvement_simulator import simulate_improvement
from services.recommendation_engine import RECOMMENDATION_CATALOG

_cache = {}


def load_dataset(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _row_to_responses(row):
    return {q["id"]: row[q["feature"]] for q in QUESTIONS}


def get_dashboard_stats(path):
    path = str(path)
    mtime = os.path.getmtime(path)
    if _cache.get("key") == (path, mtime):
        return _cache["value"]

    rows = load_dataset(path)
    n = len(rows)
    levels = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
    cat_totals = {c["key"]: 0.0 for c in CATEGORIES}
    weakness_counts = {q["finding_type"]: 0 for q in QUESTIONS}
    control_on = {q["feature"]: 0 for q in QUESTIONS if is_protective(q) and q["category"] == "account_security"}
    controls_pct_sum, fp_buckets = 0.0, {"0-20": 0, "21-40": 0, "41-70": 0, "71-100": 0}
    score_sum = imm_sum = imp_sum = 0

    for row in rows:
        responses = _row_to_responses(row)
        res = run_assessment(responses)
        levels[res["risk_level"]] += 1
        score_sum += res["overall_score"]
        for k, v in res["category_scores"].items():
            cat_totals[k] += v
        for f in res["findings"]:
            weakness_counts[f["finding_type"]] += 1
        for q in QUESTIONS:
            if q["feature"] in control_on and risk_for_answer(q, responses[q["id"]]) == 0.0:
                control_on[q["feature"]] += 1
        controls_pct_sum += 100.0 * res["controls"]["enabled"] / res["controls"]["total"]
        fp = res["category_scores"]["digital_footprint"]
        fp_buckets["0-20" if fp <= 20 else "21-40" if fp <= 40 else "41-70" if fp <= 70 else "71-100"] += 1
        # Improvement comparison: fix only IMMEDIATE items, then IMMEDIATE + IMPORTANT items
        for sums, prios in (("imm", {"IMMEDIATE"}), ("imp", {"IMMEDIATE", "IMPORTANT"})):
            ids = [f["question_id"] for f in res["findings"] if QUESTION_BY_ID[f["question_id"]]["priority"] in prios]
            after = simulate_improvement(responses, ids)["simulated"]["overall_score"] if ids else res["overall_score"]
            if sums == "imm":
                imm_sum += after
            else:
                imp_sum += after

    labels = {c["key"]: c["label"] for c in CATEGORIES}
    avg_cats = {k: round(v / n, 1) for k, v in cat_totals.items()}
    top = sorted(weakness_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    ftype_desc = {q["finding_type"]: q["finding"] for q in QUESTIONS}
    stats = {
        "data_source": "synthetic (fictional) assessments - not real people",
        "dataset_size": n,
        "average_score": round(score_sum / n, 1),
        "level_distribution": levels,
        "average_category_scores": [{"key": k, "label": labels[k], "score": s} for k, s in avg_cats.items()],
        "high_risk_categories": [labels[k] for k, s in avg_cats.items() if s > 50],
        "top_weaknesses": [{"finding_type": t, "description": ftype_desc[t], "percent": round(100 * c / n, 1)} for t, c in top],
        "account_controls": [{"feature": f, "percent_enabled": round(100 * c / n, 1)} for f, c in control_on.items()],
        "average_controls_enabled_percent": round(controls_pct_sum / n, 1),
        "digital_footprint_distribution": fp_buckets,
        "improvement_comparison": {"current": round(score_sum / n, 1), "after_immediate_fixes": round(imm_sum / n, 1),
                                   "after_immediate_and_important_fixes": round(imp_sum / n, 1)},
        "recommendation_count": len(RECOMMENDATION_CATALOG),
        "disclaimer": DISCLAIMER,
    }
    _cache["key"], _cache["value"] = (path, mtime), stats
    return stats
