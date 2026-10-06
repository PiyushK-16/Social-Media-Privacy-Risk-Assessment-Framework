"""api.py - REST API blueprint. All endpoints return JSON except report/checklist downloads."""
from flask import Blueprint, Response, current_app, jsonify, render_template, request

from models import database as db
from services.analytics import get_dashboard_stats
from services.assessment_engine import run_assessment, DISCLAIMER
from services.improvement_simulator import simulate_improvement
from services.questionnaire_data import CATEGORIES, CATEGORY_BY_KEY, public_questionnaire
from services.recommendation_engine import recommendations_for_types
from utils.checklist import CHECKLIST, checklist_text
from utils.validation import (ValidationError, is_valid_assessment_id, validate_changes, validate_responses)

api = Blueprint("api", __name__, url_prefix="/api")


def error(code, message, status, details=None):
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return jsonify(body), status


def _json_body():
    """Return parsed JSON dict or raise ValidationError."""
    if not request.is_json:
        raise ValidationError(["Content-Type must be application/json."])
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError(["Request body must be a JSON object."])
    return data


def _check_id(assessment_id):
    return is_valid_assessment_id(assessment_id)


@api.get("/questionnaire")
def questionnaire():
    """Return the 44 questions (no scoring logic is exposed)."""
    return jsonify({**public_questionnaire(), "disclaimer": DISCLAIMER})


@api.post("/assessment")
def create_assessment():
    """Validate answers -> run the engine -> store ONLY minimal results."""
    body = _json_body()
    extra = set(body) - {"responses"}
    if extra:
        raise ValidationError([f"{len(extra)} unexpected field(s). Only 'responses' is accepted."])
    responses = validate_responses(body.get("responses"))
    result = run_assessment(responses, current_app.config["RISK_WEIGHTS"])
    assessment_id, token, created_at = db.save_assessment(current_app.config["DATABASE_PATH"], result)
    return jsonify({"assessment_id": assessment_id, "delete_token": token, "created_at": created_at, **result}), 201


@api.get("/assessment/<assessment_id>")
def get_assessment(assessment_id):
    if not _check_id(assessment_id):
        return error("not_found", "Assessment not found.", 404)
    data = db.get_assessment(current_app.config["DATABASE_PATH"], assessment_id)
    if not data:
        return error("not_found", "Assessment not found.", 404)
    data["disclaimer"] = DISCLAIMER
    return jsonify(data)


@api.get("/assessment/<assessment_id>/recommendations")
def get_recs(assessment_id):
    if not _check_id(assessment_id):
        return error("not_found", "Assessment not found.", 404)
    recs = db.get_recommendations(current_app.config["DATABASE_PATH"], assessment_id)
    if recs is None:
        return error("not_found", "Assessment not found.", 404)
    if not recs:
        recs = recommendations_for_types([])
    return jsonify({"assessment_id": assessment_id, "recommendations": recs})


@api.get("/assessment/<assessment_id>/report")
def report(assessment_id):
    """Printable HTML report built ONLY from stored minimal data. Use 'Print > Save as PDF'."""
    if not _check_id(assessment_id):
        return error("not_found", "Assessment not found.", 404)
    path = current_app.config["DATABASE_PATH"]
    data = db.get_assessment(path, assessment_id)
    if not data:
        return error("not_found", "Assessment not found.", 404)
    recs = db.get_recommendations(path, assessment_id) or recommendations_for_types([])
    cats = [{"label": CATEGORY_BY_KEY[k]["label"], "score": v} for k, v in data["category_scores"].items()]
    html = render_template("report.html", a=data, categories=cats, recs=recs, checklist=CHECKLIST,
                           priority_actions=[r for r in recs if r["priority"] == "IMMEDIATE"],
                           disclaimer=DISCLAIMER)
    resp = Response(html, mimetype="text/html")
    if request.args.get("download") == "1":
        resp.headers["Content-Disposition"] = f'attachment; filename="privacy-report-{assessment_id}.html"'
    return resp


@api.post("/assessment/simulate-improvement")
def simulate():
    body = _json_body()
    extra = set(body) - {"responses", "changes"}
    if extra:
        raise ValidationError([f"{len(extra)} unexpected field(s)."])
    responses = validate_responses(body.get("responses"))
    changes = validate_changes(body.get("changes"))
    return jsonify(simulate_improvement(responses, changes, current_app.config["RISK_WEIGHTS"]))


@api.get("/dashboard/stats")
def dashboard_stats():
    stats = get_dashboard_stats(current_app.config["DATASET_PATH"])
    return jsonify({**stats, "live": db.live_stats(current_app.config["DATABASE_PATH"])})


@api.get("/privacy-checklist")
def privacy_checklist():
    if request.args.get("format") == "txt":
        return Response(checklist_text(), mimetype="text/plain",
                        headers={"Content-Disposition": 'attachment; filename="privacy-checklist.txt"'})
    return jsonify({"title": "Social Media Privacy Checklist", "items": CHECKLIST})


@api.delete("/assessment/<assessment_id>")
def delete(assessment_id):
    """Delete an assessment. Requires the secret token returned when it was created."""
    if not _check_id(assessment_id):
        return error("not_found", "Assessment not found.", 404)
    outcome = db.delete_assessment(current_app.config["DATABASE_PATH"], assessment_id,
                                   request.headers.get("X-Delete-Token", ""))
    if outcome == "not_found":
        return error("not_found", "Assessment not found.", 404)
    if outcome == "forbidden":
        return error("forbidden", "Missing or invalid delete token.", 403)
    return jsonify({"deleted": True})
