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
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@st.cache_resource(show_spinner="⚙️  Warming up the ATS backend (first load takes ~60s)…")
def _launch_backend():
    """
    Spawn the FastAPI backend once per Streamlit Cloud worker.

    Streamlit's cache_resource ensures this runs exactly once — subsequent
    script reruns reuse the live subprocess rather than spawning another.
    """
    backend_log = open("/tmp/ats_backend.log", "w")
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
        stderr=backend_log,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    # Wait up to 120s for backend to finish loading spaCy + sentence-transformers.
    import requests
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            r = requests.get("http://127.0.0.1:8000/", timeout=1)
            if r.status_code == 200:
                return {"status": "ready", "pid": proc.pid}
        except Exception:
            pass
        if proc.poll() is not None:
            return {"status": "crashed", "returncode": proc.returncode}
        time.sleep(1)
    return {"status": "timeout", "pid": proc.pid}


# Ensure the frontend's api_client talks to our in-container backend.
os.environ.setdefault("BACKEND_URL", "http://127.0.0.1:8000")
os.environ.setdefault("ALLOW_GUEST_ACCESS", "true")

_backend = _launch_backend()

if _backend["status"] == "crashed":
    st.error(
        f"Backend failed to start (exit code {_backend['returncode']}).\n\n"
        "Check the deploy logs for details."
    )
    st.stop()
elif _backend["status"] == "timeout":
    st.warning(
        "Backend is still warming up. Reload the page in ~30 seconds."
    )
    st.stop()

# Hand off to the existing Streamlit UI.
import runpy
runpy.run_path(
    str(ROOT_DIR / "frontend" / "streamlit_app.py"),
    run_name="__main__",
)
