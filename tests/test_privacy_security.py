"""Security & privacy tests S01-S12 (validation, XSS, rate limit, headers, deletion, retention...)."""
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import make_answers, risky
from app import create_app
from models import database as db


def test_s01_missing_answers_rejected(client):
    """S01 | Input validation: missing answers | only 3 answers sent | 400 listing missing IDs"""
    r = client.post("/api/assessment", json={"responses": {"A1": "PUBLIC", "B1": "YES", "G1": "NO"}})
    assert r.status_code == 400 and "Missing answers" in " ".join(r.json["error"]["details"])


def test_s02_invalid_answer_rejected(client):
    """S02 | Input validation: invalid value | B1='<script>alert(1)</script>' | 400 and payload not echoed back"""
    payload = make_answers(B1="<script>alert(1)</script>")
    r = client.post("/api/assessment", json={"responses": payload})
    assert r.status_code == 400 and "<script>" not in r.get_data(as_text=True)


def test_s03_non_json_rejected(client):
    """S03 | Input validation: wrong content type | form-encoded body | 400"""
    assert client.post("/api/assessment", data="x=1").status_code == 400


def test_s04_xss_in_report_and_ids(client):
    """S04 | XSS protection | malicious assessment ID in URL | 404 and no reflection of the payload"""
    r = client.get("/api/assessment/<script>alert(1)</script>/report")
    assert r.status_code == 404 and "<script>alert" not in r.get_data(as_text=True)


def test_s05_rate_limiting(tmp_path):
    """S05 | API rate limiting | 7 requests with limit 5/min | first 5 allowed, then 429"""
    c = create_app({"DATABASE_PATH": str(tmp_path / "r.db"), "RATE_LIMIT_PER_MINUTE": 5}).test_client()
    codes = [c.get("/api/privacy-checklist").status_code for _ in range(7)]
    assert codes[:5] == [200] * 5 and codes[5] == 429


def test_s06_delete_requires_token(client):
    """S06 | Authorization & data deletion | DELETE without/with token | 403 without, 200 with, then 404"""
    r = client.post("/api/assessment", json={"responses": risky("G1")}).json
    url = f"/api/assessment/{r['assessment_id']}"
    assert client.delete(url).status_code == 403
    assert client.delete(url, headers={"X-Delete-Token": "wrong"}).status_code == 403
    assert client.delete(url, headers={"X-Delete-Token": r["delete_token"]}).status_code == 200
    assert client.get(url).status_code == 404
    conn = sqlite3.connect(client.application.config["DATABASE_PATH"])
    assert conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == 0     # cascade delete


def test_s07_security_headers(client):
    """S07 | Secure headers | GET /api/privacy-checklist | CSP, nosniff, frame deny, no-store present"""
    h = client.get("/api/privacy-checklist").headers
    assert "default-src 'self'" in h["Content-Security-Policy"] and h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY" and h["Cache-Control"] == "no-store"


def test_s08_environment_configuration(monkeypatch, tmp_path):
    """S08 | Environment variables | RATE_LIMIT_PER_MINUTE=7 and RETENTION_DAYS=5 in env | app reads them; no secrets in source"""
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "7"); monkeypatch.setenv("RETENTION_DAYS", "5")
    app = create_app({"DATABASE_PATH": str(tmp_path / "e.db")})
    assert app.config["RATE_LIMIT_PER_MINUTE"] == 7 and app.config["RETENTION_DAYS"] == 5
    src = (Path(__file__).resolve().parent.parent / "backend" / "app.py").read_text()
    assert "SECRET_KEY" not in src and "password=" not in src.lower()


def test_s09_retention_purge(app):
    """S09 | Retention limitation | assessment older than 90 days | purge removes it, newer one stays"""
    path = app.config["DATABASE_PATH"]
    old_id, _, _ = db.save_assessment(path, {"overall_score": 10, "risk_level": "LOW", "category_scores": {"profile": 1.0}, "findings": []})
    new_id, _, _ = db.save_assessment(path, {"overall_score": 10, "risk_level": "LOW", "category_scores": {"profile": 1.0}, "findings": []})
    with db.connect(path) as conn:
        past = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(timespec="seconds")
        conn.execute("UPDATE assessments SET created_at=? WHERE assessment_id=?", (past, old_id))
    assert db.purge_older_than(path, 90) == 1
    assert db.get_assessment(path, old_id) is None and db.get_assessment(path, new_id) is not None


def test_s10_oversized_payload(client):
    """S10 | Payload size limit | 100 KB JSON body | 413"""
    assert client.post("/api/assessment", json={"responses": {"A1": "x" * 100000}}).status_code == 413


def test_s11_stateless_no_session_cookies(client):
    """S11 | Secure session handling | normal assessment flow | no Set-Cookie header (stateless app)"""
    r = client.post("/api/assessment", json={"responses": make_answers()})
    assert "Set-Cookie" not in r.headers


def test_s12_no_stack_trace_leak_and_unknown_fields(client):
    """S12 | Error handling | unknown route and unknown JSON field | clean JSON errors, no stack trace"""
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404 and "Traceback" not in r.get_data(as_text=True)
    r2 = client.post("/api/assessment/simulate-improvement", json={"responses": make_answers(), "changes": ["ZZ9"]})
    assert r2.status_code == 400 and r2.is_json
