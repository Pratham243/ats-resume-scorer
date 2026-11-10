"""
Streamlit Cloud entry point for the ATS Resume Scorer.

Single-container deployment pattern:
    1. Launch FastAPI backend as a subprocess bound to 127.0.0.1:8000
       (private to this container — not exposed to the public internet).
    2. Point BACKEND_URL at it so the Streamlit frontend's api_client
       transparently keeps working.
    3. Hand off execution to the existing Streamlit UI in
       frontend/streamlit_app.py — no changes to UI code required.

The microservice architecture is preserved: backend and frontend remain
decoupled processes communicating over HTTP. Only the network topology
changes (loopback instead of a routable domain) to fit Streamlit Cloud's
single-process-per-app model.
"""
import os
import sys
import time
import subprocess
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_LOG_PATH = "/tmp/ats_backend.log"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _tail_backend_log(lines: int = 80) -> str:
    """Return the last `lines` of the backend subprocess log (for UI error display)."""
    try:
        with open(BACKEND_LOG_PATH, "r") as f:
            content = f.read()
        return "\n".join(content.splitlines()[-lines:])
    except Exception as e:
        return f"(could not read backend log: {e})"


@st.cache_resource(show_spinner="⚙️  Warming up the ATS backend (first load takes ~60s)…")
def _launch_backend():
    """
    Spawn the FastAPI backend once per Streamlit Cloud worker.

    Streamlit's cache_resource ensures this runs exactly once — subsequent
    script reruns reuse the live subprocess rather than spawning another.

    Output is written to BOTH a file AND Streamlit's stdout so errors surface
    in the Streamlit Cloud deploy logs (via `tee`-style duplication done in Python).
    """
    # Open log file for subprocess output; also print to this process's stdout
    # so Streamlit Cloud captures backend startup messages in its deploy logs.
    backend_log = open(BACKEND_LOG_PATH, "w", buffering=1)  # line-buffered
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "info",
        ],
        cwd=str(ROOT_DIR),
        stdout=backend_log,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    # Wait up to 180s for backend to finish loading spaCy + sentence-transformers.
    # First run downloads the sentence-transformers model (~90 MB) from HF Hub,
    # which can take 30–60s; add a buffer on top for cold starts.
    import requests
    deadline = time.time() + 180
    while time.time() < deadline:
        try:
            r = requests.get("http://127.0.0.1:8000/", timeout=1)
            if r.status_code == 200:
                return {"status": "ready", "pid": proc.pid}
        except Exception:
            pass
        if proc.poll() is not None:
            # Subprocess exited before serving — capture its log tail for UI.
            return {
                "status": "crashed",
                "returncode": proc.returncode,
                "log_tail": _tail_backend_log(80),
            }
        time.sleep(1)
    return {
        "status": "timeout",
        "pid": proc.pid,
        "log_tail": _tail_backend_log(80),
    }


# Ensure the frontend's api_client talks to our in-container backend.
os.environ.setdefault("BACKEND_URL", "http://127.0.0.1:8000")
os.environ.setdefault("ALLOW_GUEST_ACCESS", "true")

_backend = _launch_backend()

if _backend["status"] == "crashed":
    st.error(
        f"❌ FastAPI backend subprocess exited with code {_backend['returncode']} "
        "before it could serve requests."
    )
    with st.expander("Backend log (last 80 lines)", expanded=True):
        st.code(_backend.get("log_tail", "(no log)"), language="text")
    st.info(
        "Common causes: missing env var, OOM kill, or an import/startup error "
        "in backend/main.py. Fix the root cause and push a new commit."
    )
    st.stop()
elif _backend["status"] == "timeout":
    st.warning("⚠️ Backend did not become ready within 180 seconds.")
    with st.expander("Backend log (last 80 lines)", expanded=True):
        st.code(_backend.get("log_tail", "(no log)"), language="text")
    st.info("Reload the page in ~30 seconds — if it keeps timing out, investigate the log above.")
    st.stop()

# Hand off to the existing Streamlit UI.
import runpy
runpy.run_path(
    str(ROOT_DIR / "frontend" / "streamlit_app.py"),
    run_name="__main__",
)
