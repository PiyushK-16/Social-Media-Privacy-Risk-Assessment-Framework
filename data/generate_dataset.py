"""
generate_dataset.py - builds 1,000 FICTIONAL privacy-assessment records.

100% synthetic: random answers drawn from a hidden 'carelessness' level per
fictional profile. No real person, account or platform is involved.

Run:  python data/generate_dataset.py            (writes data/social_media_privacy_assessments.csv)
"""
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from services.questionnaire_data import QUESTIONS, CATEGORIES, riskiest_answer, safest_answer  # noqa: E402
from services.assessment_engine import extract_privacy_features  # noqa: E402
from services.scoring_engine import calculate_privacy_risk  # noqa: E402

DEFAULT_OUTPUT = ROOT / "data" / "social_media_privacy_assessments.csv"

# Typical chance that the RISKY answer is given by an "average" fictional user.
BASE_RISKY_RATE = {"B1": 0.25, "B3": 0.35, "C1": 0.12, "C4": 0.30, "G1": 0.35, "G2": 0.45,
                   "I3": 0.12, "D2": 0.20, "F2": 0.55, "H1": 0.60, "J1": 0.65, "J4": 0.55,
                   "G3": 0.55, "G5": 0.60, "E1": 0.35}


def _answer(q, p_risky, rng):
    """Pick one answer for a question given the probability of the risky answer."""
    r = rng.random()
    if r < p_risky:
        return riskiest_answer(q)
    u = (r - p_risky) / (1 - p_risky)           # uniform in [0,1) over the remaining mass
    if q["kind"] == "vis":
        return "FRIENDS" if u < 0.55 else "NOT_SURE" if u < 0.60 else "PRIVATE"
    return "SOMETIMES" if u < 0.20 else "NOT_SURE" if u < 0.25 else safest_answer(q)


def generate_records(n=1000, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        carelessness = rng.betavariate(1.6, 1.6)         # 0 = very careful, 1 = very careless
        answers = {}
        for q in QUESTIONS:
            base = BASE_RISKY_RATE.get(q["id"], 0.40)
            p = min(0.97, max(0.03, base + (carelessness - 0.5) * 1.5 + rng.uniform(-0.08, 0.08)))
            answers[q["id"]] = _answer(q, p, rng)
        features = extract_privacy_features(answers)
        result = calculate_privacy_risk(features)
        row = {"profile_id": f"SYN-{i:04d}"}
        row.update({q["feature"]: answers[q["id"]] for q in QUESTIONS})
        row.update({f"score_{k}": v for k, v in result["category_scores"].items()})
        row["risk_score"] = result["overall_score"]
        row["risk_level"] = result["risk_level"]
        rows.append(row)
    return rows


def write_csv(rows, path=DEFAULT_OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def main(n=1000, seed=42, path=DEFAULT_OUTPUT):
    rows = generate_records(n, seed)
    out = write_csv(rows, path)
    levels = {}
    for r in rows:
        levels[r["risk_level"]] = levels.get(r["risk_level"], 0) + 1
    print(f"Wrote {len(rows)} synthetic records to {out}")
    print("Risk level distribution:", levels)
    return out


if __name__ == "__main__":
    main()
