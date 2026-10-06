"""
improvement_simulator.py - "What happens if I improve my settings?"

Stateless: nothing is stored. It re-runs the scoring pipeline on a modified COPY
of the answers. Results are a framework simulation, NOT a guarantee of safety.
"""
from services.questionnaire_data import QUESTION_BY_ID, safest_answer
from services.assessment_engine import run_assessment

SIM_DISCLAIMER = ("Framework simulation only: it shows how this educational score would change if the "
                  "selected settings changed. It is not a guarantee of real-world safety.")


def simulate_improvement(responses, changes, weights=None):
    """changes: {question_id: new_answer or 'BEST'} (already validated)."""
    if isinstance(changes, (list, tuple, set)):      # convenience: list of IDs = apply safest answer
        changes = {qid: "BEST" for qid in changes}
    before = run_assessment(responses, weights)
    improved, applied = dict(responses), []
    for qid, new in changes.items():
        q = QUESTION_BY_ID[qid]
        new_answer = safest_answer(q) if new == "BEST" else new
        applied.append({"question_id": qid, "finding_type": q["finding_type"],
                        "from": responses[qid], "to": new_answer, "recommendation": q["recommendation"]})
        improved[qid] = new_answer
    after = run_assessment(improved, weights)
    return {
        "current": {"overall_score": before["overall_score"], "risk_level": before["risk_level"],
                    "category_scores": before["category_scores"]},
        "simulated": {"overall_score": after["overall_score"], "risk_level": after["risk_level"],
                      "category_scores": after["category_scores"]},
        "risk_reduction": before["overall_score"] - after["overall_score"],
        "applied_changes": applied,
        "disclaimer": SIM_DISCLAIMER,
    }
