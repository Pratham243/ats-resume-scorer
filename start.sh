#!/bin/bash
# ----------------------------------------------------------------------
# HF Spaces startup: run FastAPI backend (bg) + Streamlit frontend (fg)
# ----------------------------------------------------------------------
set -e

echo ">>> [1/2] Starting FastAPI backend on 0.0.0.0:8000..."
uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info &
BACKEND_PID=$!

# Give backend time to load spaCy + sentence-transformers (~30-60s first run)
echo ">>> Waiting for backend to warm up..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/ > /dev/null 2>&1; then
        echo ">>> Backend is up."
        break
    fi
    sleep 2
done

echo ">>> [2/2] Starting Streamlit frontend on 0.0.0.0:7860..."
exec streamlit run frontend/streamlit_app.py \
    --server.port=7860 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
