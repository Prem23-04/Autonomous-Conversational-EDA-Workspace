import os
import uuid
import logging

from flask import (
    Flask, render_template, request, jsonify, session, send_from_directory
)
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv

from utils.data_manager import DataManager
from utils.profiler import generate_profile_report
from utils.agent import EDAAgent, AgentError

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_ROOT = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "static", "reports")
CHARTS_DIR = os.path.join(BASE_DIR, "static", "charts")

os.makedirs(UPLOAD_ROOT, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eda_workspace")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", 50)) * 1024 * 1024

# LLM provider config is now handled inside utils/agent.py via .env


# In-memory per-process cache of agent instances keyed by session id, so we
# don't rebuild the (relatively expensive) LangChain agent on every message.
_agent_cache: dict[str, EDAAgent] = {}


def _get_session_id() -> str:
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


def _get_data_manager() -> DataManager:
    return DataManager(UPLOAD_ROOT, _get_session_id())


@app.route("/")
def index():
    _get_session_id()
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    try:
        dm = _get_data_manager()
        meta = dm.save_upload(file)
        # Invalidate any cached agent for this session - dataset changed.
        _agent_cache.pop(_get_session_id(), None)
        return jsonify({"success": True, "meta": meta})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except RequestEntityTooLarge:
        return jsonify({"error": "File is too large."}), 413
    except Exception as e:
        logger.exception("Upload failed")
        return jsonify({"error": f"Unexpected error during upload: {e}"}), 500

@app.route("/api/preview", methods=["GET"])
def preview_data():
    try:
        dm = _get_data_manager()
        return jsonify({"success": True, "preview": dm.preview()})
    except FileNotFoundError:
        return jsonify({"error": "No dataset uploaded yet."}), 404
    except Exception as e:
        logger.exception("Preview failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/clean", methods=["POST"])
def clean_data():
    payload = request.get_json(silent=True) or {}
    drop_duplicates = bool(payload.get("drop_duplicates", True))
    fillna_strategy = payload.get("fillna_strategy", "none")

    if fillna_strategy not in {"none", "mean", "median", "drop"}:
        return jsonify({"error": "Invalid fillna_strategy."}), 400

    try:
        dm = _get_data_manager()
        result = dm.basic_clean(drop_duplicates=drop_duplicates, fillna_strategy=fillna_strategy)
        _agent_cache.pop(_get_session_id(), None)  # dataset changed
        return jsonify({"success": True, "result": result})
    except FileNotFoundError:
        return jsonify({"error": "No dataset uploaded yet."}), 404
    except Exception as e:
        logger.exception("Cleaning failed")
        return jsonify({"error": str(e)}), 500

@app.route("/api/profile", methods=["POST"])
def profile_data():
    try:
        dm = _get_data_manager()
        df = dm.load_active_dataframe()
    except FileNotFoundError:
        return jsonify({"error": "No dataset uploaded yet."}), 404
    except Exception as e:
        logger.exception("Could not load dataframe for profiling")
        return jsonify({"error": str(e)}), 500

    minimal = df.shape[0] * df.shape[1] > 500_000  # auto-fallback for huge datasets
    try:
        filename = generate_profile_report(df, REPORTS_DIR, _get_session_id(), minimal=minimal)
        return jsonify({"success": True, "report_url": f"/reports/{filename}", "minimal": minimal})
    except Exception as e:
        logger.exception("Profiling failed")
        return jsonify({"error": f"Failed to generate profiling report: {e}"}), 500


@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    question = (payload.get("message") or "").strip()
    if not question:
        return jsonify({"error": "Message cannot be empty."}), 400

    session_id = _get_session_id()
    try:
        dm = _get_data_manager()
        df = dm.load_active_dataframe()
    except FileNotFoundError:
        return jsonify({"error": "Please upload a dataset before chatting."}), 404
    except Exception as e:
        return jsonify({"error": f"Could not load dataset: {e}"}), 500

    try:
        agent = _agent_cache.get(session_id)
        if agent is None:
            agent = EDAAgent(df)
            _agent_cache[session_id] = agent
        else:
            agent.df = df  # keep dataframe in sync in case of in-place edits

        result = agent.ask(question)
        return jsonify({"success": True, "response": result})
    except AgentError as ae:
        return jsonify({"error": str(ae)}), 422
    except Exception as e:
        logger.exception("Chat agent failed")
        return jsonify({"error": f"Unexpected agent error: {e}"}), 500
@app.route("/api/reset", methods=["POST"])
def reset_session():
    session_id = _get_session_id()
    _agent_cache.pop(session_id, None)
    session.clear()
    return jsonify({"success": True})

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Uploaded file exceeds the maximum allowed size."}), 413


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found."}), 404
    return e


@app.errorhandler(500)
def server_error(e):
    logger.exception("Internal server error")
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error."}), 500
    return e


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)