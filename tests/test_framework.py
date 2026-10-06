"""Functional tests T01-T30 (scoring, findings, recommendations, simulator, storage, report)."""
import sqlite3

from conftest import make_answers, risky, all_public
from services.assessment_engine import run_assessment, extract_privacy_features
from services.scoring_engine import classify_risk, calculate_category_scores, calculate_privacy_risk
from services.questionnaire_data import QUESTIONS
from services.improvement_simulator import simulate_improvement


def types(result):
    return {f["finding_type"] for f in result["findings"]}


def test_t01_fully_private(): 
    """T01 | Fully private profile | all safest answers | score 0, LOW, no findings"""
    r = run_assessment(make_answers())
    assert r["overall_score"] == 0 and r["risk_level"] == "LOW" and r["findings"] == []


def test_t02_fully_public():
    """T02 | Fully public synthetic profile | all riskiest answers | score 100, CRITICAL, 44 findings"""
    r = run_assessment(all_public())
    assert r["overall_score"] == 100 and r["risk_level"] == "CRITICAL" and len(r["findings"]) == len(QUESTIONS)


def test_t03_public_phone():
    """T03 | Public phone | B1=YES | PUBLIC_PHONE finding and personal_info score > 0"""
    r = run_assessment(risky("B1"))
    assert "PUBLIC_PHONE" in types(r) and r["category_scores"]["personal_info"] > 0


def test_t04_public_email():
    """T04 | Public email | B2=YES | PUBLIC_EMAIL finding"""
    assert "PUBLIC_EMAIL" in types(run_assessment(risky("B2")))


def test_t05_public_birthday():
    """T05 | Public birthday | B3=YES | PUBLIC_BIRTHDAY finding (HIGH)"""
    f = [x for x in run_assessment(risky("B3"))["findings"] if x["finding_type"] == "PUBLIC_BIRTHDAY"]
    assert f and f[0]["severity"] == "HIGH"


def test_t06_public_location():
    """T06 | Public location (geotags + inferable home/work) | C2=YES,C5=YES | location findings, score > 0"""
    r = run_assessment(risky("C2", "C5"))
    assert {"GEOTAGGED_POSTS", "INFERABLE_HOME_WORK_LOCATION"} <= types(r) and r["category_scores"]["location"] > 0


def test_t07_realtime_checkins():
    """T07 | Real-time check-ins | C1=YES,C3=YES | REALTIME_LOCATION + LIVE_CHECKINS"""
    assert {"REALTIME_LOCATION", "LIVE_CHECKINS"} <= types(run_assessment(risky("C1", "C3")))


def test_t08_travel_plans():
    """T08 | Travel plans public | C4=YES | PUBLIC_TRAVEL_PLANS finding"""
    assert "PUBLIC_TRAVEL_PLANS" in types(run_assessment(risky("C4")))


def test_t09_workplace_exposure():
    """T09 | Workplace exposure | B5=YES | PUBLIC_WORKPLACE finding"""
    assert "PUBLIC_WORKPLACE" in types(run_assessment(risky("B5")))


def test_t10_education_exposure():
    """T10 | Education exposure | B6=YES | PUBLIC_EDUCATION finding"""
    assert "PUBLIC_EDUCATION" in types(run_assessment(risky("B6")))


def test_t11_public_posts():
    """T11 | Public posts | D1=PUBLIC | PUBLIC_POSTS finding"""
    assert "PUBLIC_POSTS" in types(run_assessment(risky("D1")))


def test_t12_unknown_connections():
    """T12 | Unknown connections accepted | E1=YES | UNKNOWN_CONNECTIONS_ACCEPTED, connections score > 0"""
    r = run_assessment(risky("E1"))
    assert "UNKNOWN_CONNECTIONS_ACCEPTED" in types(r) and r["category_scores"]["connections"] > 0


def test_t13_tag_review_disabled():
    """T13 | Tag review disabled | F2=NO | TAG_REVIEW_DISABLED finding"""
    assert "TAG_REVIEW_DISABLED" in types(run_assessment(risky("F2")))


def test_t14_mfa_disabled():
    """T14 | MFA disabled | G1=NO | MFA_DISABLED (HIGH) and account_security score > 0"""
    r = run_assessment(risky("G1"))
    assert "MFA_DISABLED" in types(r) and r["category_scores"]["account_security"] > 0


def test_t15_login_alerts_disabled():
    """T15 | Login alerts disabled | G4=NO | LOGIN_ALERTS_DISABLED finding"""
    assert "LOGIN_ALERTS_DISABLED" in types(run_assessment(risky("G4")))


def test_t16_password_reuse():
    """T16 | Password reuse reported | G2=YES | PASSWORD_REUSE finding"""
    assert "PASSWORD_REUSE" in types(run_assessment(risky("G2")))


def test_t17_third_party_not_reviewed():
    """T17 | Third-party apps not reviewed | H1=NO | THIRD_PARTY_APPS_NOT_REVIEWED finding"""
    assert "THIRD_PARTY_APPS_NOT_REVIEWED" in types(run_assessment(risky("H1")))


def test_t18_low_link_awareness():
    """T18 | Suspicious-link awareness low | I1=NO | LOW_LINK_AWARENESS finding"""
    assert "LOW_LINK_AWARENESS" in types(run_assessment(risky("I1")))


def test_t19_old_posts_not_reviewed():
    """T19 | Old posts not reviewed | J1=NO | OLD_POSTS_NOT_REVIEWED finding"""
    assert "OLD_POSTS_NOT_REVIEWED" in types(run_assessment(risky("J1")))


def test_t20_settings_not_reviewed():
    """T20 | Privacy settings not reviewed | J4=NO | SETTINGS_NOT_REVIEWED finding"""
    assert "SETTINGS_NOT_REVIEWED" in types(run_assessment(risky("J4")))


def test_t21_category_score_calculation():
    """T21 | Category score maths | B1 risky only (weight 3 of 15) | personal_info = 20.0"""
    scores = calculate_category_scores(extract_privacy_features(risky("B1")))
    assert scores["personal_info"] == 20.0 and scores["profile"] == 0.0


def test_t22_overall_score_calculation():
    """T22 | Overall score maths | all personal_info risky only (weight 15%) | overall 15, LOW"""
    r = run_assessment(risky("B1", "B2", "B3", "B4", "B5", "B6", "B7"))
    assert r["category_scores"]["personal_info"] == 100.0 and r["overall_score"] == 15 and r["risk_level"] == "LOW"


def test_t23_boundary_20():
    """T23 | Score boundary 20 | 20 and 21 | 20 -> LOW, 21 -> MODERATE"""
    assert classify_risk(20) == "LOW" and classify_risk(21) == "MODERATE"


def test_t24_boundary_40():
    """T24 | Score boundary 40 | 40 and 41 | 40 -> MODERATE, 41 -> HIGH"""
    assert classify_risk(40) == "MODERATE" and classify_risk(41) == "HIGH"


def test_t25_boundary_70():
    """T25 | Score boundary 70 | 70 and 71 | 70 -> HIGH, 71 -> CRITICAL"""
    assert classify_risk(70) == "HIGH" and classify_risk(71) == "CRITICAL"


def test_t26_recommendation_generation():
    """T26 | Recommendation generation | MFA off + public phone + live location | IMMEDIATE recs listed first"""
    r = run_assessment(risky("G1", "B1", "C1", "E1"))
    recs = r["recommendations"]
    assert len(recs) == 4 and [x["priority"] for x in recs][:3] == ["IMMEDIATE"] * 3 and recs[-1]["priority"] == "IMPORTANT"


def test_t27_improvement_simulation():
    """T27 | Improvement simulation | fix MFA, phone, live location | after < before, reduction = difference"""
    answers = risky("G1", "B1", "C1", "F2", "E1")
    s = simulate_improvement(answers, ["G1", "B1", "C1"])
    assert s["simulated"]["overall_score"] < s["current"]["overall_score"]
    assert s["risk_reduction"] == s["current"]["overall_score"] - s["simulated"]["overall_score"]


def test_t28_database_save(client):
    """T28 | Database save | POST assessment then GET it | 201, stored score matches, findings stored"""
    r = client.post("/api/assessment", json={"responses": risky("G1", "B1")})
    assert r.status_code == 201
    got = client.get(f"/api/assessment/{r.json['assessment_id']}").json
    assert got["overall_score"] == r.json["overall_score"] and len(got["findings"]) == 2
    assert client.get(f"/api/assessment/{r.json['assessment_id']}/recommendations").status_code == 200


def test_t29_sensitive_data_not_stored(client, app):
    """T29 | Sensitive data not stored | extra 'phone' field rejected; DB has no PII columns | 400, no sensitive column names"""
    bad = client.post("/api/assessment", json={"responses": make_answers(), "phone": "555-0100-CANARY"})
    assert bad.status_code == 400
    client.post("/api/assessment", json={"responses": risky("B1")})
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    cols = {row[1].lower() for t in ("assessments", "category_scores", "findings", "recommendations")
            for row in conn.execute(f"PRAGMA table_info({t})")}
    banned = {"phone", "email", "address", "birth_date", "birthday", "password", "location", "message", "answers", "responses", "ip"}
    assert not (cols & banned)
    dump = "\n".join(conn.iterdump())
    assert "CANARY" not in dump and "555-0100" not in dump


def test_t30_report_generation(client):
    """T30 | Report generation | GET report for stored assessment | 200 HTML with ID, level, disclaimer, checklist"""
    r = client.post("/api/assessment", json={"responses": risky("G1")})
    html = client.get(f"/api/assessment/{r.json['assessment_id']}/report").get_data(as_text=True)
    assert r.json["assessment_id"] in html and r.json["risk_level"] in html
    assert "not a guarantee" in html and "Enable MFA" in html


def test_t31_weights_validation():
    """T31 | Custom weights must sum to 1 | weights summing to 1.2 | ValueError; valid custom weights change the score"""
    import pytest
    from services.scoring_engine import DEFAULT_WEIGHTS
    bad = dict(DEFAULT_WEIGHTS, profile=0.30)
    with pytest.raises(ValueError):
        calculate_privacy_risk(extract_privacy_features(make_answers()), bad)
    heavy = {k: 0.0 for k in DEFAULT_WEIGHTS}; heavy["account_security"] = 1.0
    assert run_assessment(risky("G1", "G2", "G3", "G4", "G5", "G6"), heavy)["overall_score"] == 100


def test_t32_questionnaire_size():
    """T32 | Questionnaire has 40+ questions across 10 categories | read questionnaire | 44 questions, 10 categories"""
    assert len(QUESTIONS) >= 40 and len({q["category"] for q in QUESTIONS}) == 10


def test_t33_metadata_tool_strips_exif(tmp_path):
    """T33 | Local metadata tool | JPEG with EXIF+GPS then --strip | metadata read locally, clean copy has none, original untouched"""
    import sys
    from pathlib import Path
    from PIL import Image
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import metadata_tool
    img = Image.new("RGB", (20, 20), (10, 20, 30)); ex = img.getexif(); ex[271] = "DemoPhoneCo"
    gps = ex.get_ifd(0x8825); gps[1] = "N"; gps[2] = (1.0, 2.0, 3.0)
    src = tmp_path / "p.jpg"; img.save(src, exif=ex)
    before = metadata_tool.read_metadata(src)
    assert before["exif"].get("Make") == "DemoPhoneCo" and before["gps"]
    clean = metadata_tool.strip_metadata(src)
    after = metadata_tool.read_metadata(clean)
    assert not after["exif"] and not after["gps"] and metadata_tool.read_metadata(src)["gps"]
