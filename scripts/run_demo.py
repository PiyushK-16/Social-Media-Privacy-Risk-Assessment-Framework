"""run_demo.py - assess the FICTIONAL demonstration profile, then simulate improvements.
Run: python scripts/run_demo.py   (also writes docs/DEMO_RESULTS.md)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from services.questionnaire_data import QUESTIONS, CATEGORY_BY_KEY, safest_answer, riskiest_answer  # noqa: E402
from services.assessment_engine import run_assessment  # noqa: E402
from services.findings_engine import format_findings_text  # noqa: E402
from services.improvement_simulator import simulate_improvement  # noqa: E402

BY_ID = {q["id"]: q for q in QUESTIONS}
# Fictional profile from the project brief. Questions not mentioned there use a middle-of-the-road
# answer ("SOMETIMES" / "FRIENDS") so the demo reflects an average, not a perfect, user.
RISKY_IDS = ["A1", "B1", "B3", "C1", "C2", "C3", "C5", "C4", "E1", "F2", "G1", "G4", "H1", "J1"]
SAFE_IDS = ["B2"]                                   # e-mail is private
DEFAULT_ANSWER = lambda q: "FRIENDS" if q["kind"] == "vis" else "SOMETIMES"

demo = {q["id"]: DEFAULT_ANSWER(q) for q in QUESTIONS}
demo.update({i: riskiest_answer(BY_ID[i]) for i in RISKY_IDS})
demo.update({i: safest_answer(BY_ID[i]) for i in SAFE_IDS})

FIXES = {"Phone -> Private": ["B1"], "Birthday -> Private": ["B3"], "Location -> Private": ["C1", "C2", "C3", "C5"],
         "Travel plans -> Private": ["C4"], "Unknown requests -> Reject/Verify": ["E1"], "Tag review -> Enabled": ["F2"],
         "MFA -> Enabled": ["G1"], "Login alerts -> Enabled": ["G4"], "Third-party apps -> Reviewed": ["H1"]}

result = run_assessment(demo)
fix_ids = [i for ids in FIXES.values() for i in ids]
sim = simulate_improvement(demo, fix_ids)

out = ["# Demo Profile Results (fictional)", "", "```", format_findings_text(result), "```", "", "## Recommendations"]
for r in result["recommendations"][:8]:
    out.append(f"- [{r['priority']}] {r['recommendation']}")
out += ["", "## Improvement simulation", ""] + [f"- {k}" for k in FIXES]
out += ["", f"CURRENT: {sim['current']['overall_score']}/100 ({sim['current']['risk_level']})",
        f"SIMULATED: {sim['simulated']['overall_score']}/100 ({sim['simulated']['risk_level']})",
        f"RISK REDUCTION: {sim['risk_reduction']} points", "", f"_{sim['disclaimer']}_"]
text = "\n".join(out)
print(text)
(ROOT / "docs" / "DEMO_RESULTS.md").write_text(text + "\n", encoding="utf-8")
