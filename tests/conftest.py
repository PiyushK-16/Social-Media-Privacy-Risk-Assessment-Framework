"""conftest.py - shared fixtures + a hook that writes docs/TEST_RESULTS.md after every run.

Each test docstring uses the format:  ID | Scenario | Input | Expected result
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "data"))

from app import create_app  # noqa: E402
from services.questionnaire_data import QUESTIONS, safest_answer, riskiest_answer  # noqa: E402

RESULTS = []


@pytest.fixture
def app(tmp_path):
    return create_app({"DATABASE_PATH": str(tmp_path / "test.db"), "RATE_LIMIT_PER_MINUTE": 1000})


@pytest.fixture
def client(app):
    return app.test_client()


def make_answers(**overrides):
    """Start from the SAFEST answers; overrides use question IDs, e.g. make_answers(B1='YES')."""
    answers = {q["id"]: safest_answer(q) for q in QUESTIONS}
    answers.update(overrides)
    return answers


def risky(*ids):
    """Answers with the given question IDs set to their riskiest option."""
    by_id = {q["id"]: q for q in QUESTIONS}
    return make_answers(**{i: riskiest_answer(by_id[i]) for i in ids})


def all_public():
    return {q["id"]: riskiest_answer(q) for q in QUESTIONS}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        RESULTS.append((item.function.__doc__ or item.name, rep.outcome))


def pytest_sessionfinish(session, exitstatus):
    if not RESULTS:
        return
    lines = ["# Automated Test Results", "",
             "| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |",
             "|---|---|---|---|---|---|"]
    for doc, outcome in sorted(RESULTS, key=lambda r: r[0]):
        parts = [p.strip() for p in doc.split("|")]
        if len(parts) < 4:
            continue
        ok = outcome == "passed"
        lines.append(f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} | "
                     f"{'Matched expected result' if ok else 'Did not match expected result'} | {'PASS' if ok else 'FAIL'} |")
    passed = sum(1 for _, o in RESULTS if o == "passed")
    lines += ["", f"**{passed} / {len(RESULTS)} tests passed.**"]
    out = ROOT / "docs" / "TEST_RESULTS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
