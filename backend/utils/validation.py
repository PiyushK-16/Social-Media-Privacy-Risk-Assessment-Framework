"""
validation.py - strict input validation.

Only known question IDs and known answer options are accepted. Free text is
never accepted, which (a) blocks XSS/injection payloads and (b) stops users
from accidentally typing personal data into the system.
"""
import re
from services.questionnaire_data import QUESTIONS, QUESTION_BY_ID, options_for

ASSESSMENT_ID_RE = re.compile(r"^PRA-[0-9A-F]{16}$")


class ValidationError(Exception):
    """Raised when a request body fails validation. 'errors' is a list of safe messages."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def normalize_answer(value):
    if not isinstance(value, str):
        return None
    return value.strip().upper().replace(" ", "_")


def validate_responses(payload):
    """Return {question_id: NORMALIZED_ANSWER} or raise ValidationError."""
    if not isinstance(payload, dict):
        raise ValidationError(["'responses' must be a JSON object of question_id -> answer."])
    errors, clean = [], {}

    unknown = [k for k in payload if k not in QUESTION_BY_ID]
    if unknown:
        # Do NOT echo unknown keys back (they could contain personal data or markup).
        errors.append(f"{len(unknown)} unknown field(s) supplied. Only questionnaire IDs are accepted.")

    missing = [q["id"] for q in QUESTIONS if q["id"] not in payload]
    if missing:
        errors.append("Missing answers for: " + ", ".join(missing))

    for q in QUESTIONS:
        if q["id"] not in payload:
            continue
        ans = normalize_answer(payload[q["id"]])
        if ans not in options_for(q):
            errors.append(f"Invalid answer for {q['id']}. Allowed: {', '.join(options_for(q))}")
        else:
            clean[q["id"]] = ans
    if errors:
        raise ValidationError(errors)
    return clean


def validate_changes(changes):
    """Validate simulator input. Accepts a list of question IDs (apply safest answer)
    or a dict {question_id: answer or 'BEST'}. Returns dict {qid: answer|'BEST'}."""
    if isinstance(changes, list):
        changes = {qid: "BEST" for qid in changes}
    if not isinstance(changes, dict) or not changes:
        raise ValidationError(["'changes' must be a non-empty list of question IDs or an object."])
    clean, errors = {}, []
    for qid, ans in changes.items():
        if not isinstance(qid, str) or qid not in QUESTION_BY_ID:
            errors.append("A change refers to an unknown question ID.")
            continue
        if isinstance(ans, str) and ans.strip().upper() == "BEST":
            clean[qid] = "BEST"
            continue
        norm = normalize_answer(ans)
        if norm not in options_for(QUESTION_BY_ID[qid]):
            errors.append(f"Invalid new answer for {qid}.")
        else:
            clean[qid] = norm
    if errors:
        raise ValidationError(errors)
    return clean


def is_valid_assessment_id(value):
    return bool(isinstance(value, str) and ASSESSMENT_ID_RE.match(value))
