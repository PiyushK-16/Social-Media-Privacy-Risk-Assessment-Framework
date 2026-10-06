"""
app.py - Flask application factory for the Social Media Privacy Risk Assessment Framework.

Run (from the project root):   python backend/app.py
Then open:                     http://127.0.0.1:5000
"""
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(ROOT / "data"))

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:           # python-dotenv is optional
    pass

from models import database as db  # noqa: E402
from routes.api import api, error  # noqa: E402
from services.scoring_engine import DEFAULT_WEIGHTS, validate_weights  # noqa: E402
from utils.rate_limit import RateLimiter  # noqa: E402
from utils.validation import ValidationError  # noqa: E402

CSP = ("default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


def create_app(overrides=None):
    app = Flask(__name__, static_folder=str(ROOT / "frontend"), static_url_path="", template_folder=str(BASE / "templates"))
    weights = json.loads(os.environ["RISK_WEIGHTS"]) if os.environ.get("RISK_WEIGHTS") else DEFAULT_WEIGHTS
    app.config.update(
        DATABASE_PATH=os.environ.get("DATABASE_PATH", str(ROOT / "instance" / "assessments.db")),
        DATASET_PATH=os.environ.get("DATASET_PATH", str(ROOT / "data" / "social_media_privacy_assessments.csv")),
        RATE_LIMIT_PER_MINUTE=int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60")),
        RETENTION_DAYS=int(os.environ.get("RETENTION_DAYS", "90")),
        MAX_CONTENT_LENGTH=32 * 1024,          # requests larger than 32 KB are rejected (413)
        RISK_WEIGHTS=weights,
    )
    app.config.update(overrides or {})
    validate_weights(app.config["RISK_WEIGHTS"])

    db.init_db(app.config["DATABASE_PATH"])
    db.purge_older_than(app.config["DATABASE_PATH"], app.config["RETENTION_DAYS"])
    if not Path(app.config["DATASET_PATH"]).exists():           # build the synthetic dataset on first run
        import generate_dataset
        generate_dataset.main(path=app.config["DATASET_PATH"])

    limiter = RateLimiter(app.config["RATE_LIMIT_PER_MINUTE"])
    app.extensions["limiter"] = limiter

    @app.before_request
    def rate_limit():
        if request.path.startswith("/api/") and not limiter.allow(request.remote_addr or "unknown"):
            return error("rate_limited", "Too many requests. Please slow down.", 429)

    @app.after_request
    def security_headers(resp):
        resp.headers["Content-Security-Policy"] = CSP
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(ValidationError)
    def on_validation(exc):
        return error("validation_error", "Request validation failed.", 400, exc.errors)

    @app.errorhandler(404)
    def on_404(_):
        return error("not_found", "Resource not found.", 404)

    @app.errorhandler(405)
    def on_405(_):
        return error("method_not_allowed", "Method not allowed.", 405)

    @app.errorhandler(413)
    def on_413(_):
        return error("payload_too_large", "Request body is too large.", 413)

    @app.errorhandler(500)
    def on_500(_):
        return error("server_error", "Unexpected server error.", 500)    # never leak stack traces

    app.register_blueprint(api)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    # debug=False on purpose: the Werkzeug debugger must never be exposed.
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
