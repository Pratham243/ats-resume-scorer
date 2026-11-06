# ----------------------------------------------------------------------
# Hugging Face Spaces — Docker SDK deployment
# Serves BOTH FastAPI backend (port 8000, internal) and
# Streamlit frontend (port 7860, public) in a single container.
# ----------------------------------------------------------------------
FROM python:3.11-slim

# Prevent .pyc files; make logs stream in real time
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── System dependencies (spaCy, sentence-transformers, WeasyPrint PDF) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# ── HF Spaces convention: run as non-root user 'user' (uid 1000) ──
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/user/.cache/huggingface \
    STREAMLIT_HOME=/home/user/.streamlit \
    BACKEND_URL=http://localhost:8000 \
    ALLOW_GUEST_ACCESS=true

WORKDIR /home/user/app

# ── Install Python dependencies ──
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Pre-download spaCy NLP models (both small and medium) ──
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download en_core_web_md

# ── Copy application code (backend + frontend) ──
COPY --chown=user . .

# ── Make start script executable ──
RUN chmod +x start.sh

# HF Spaces public port
EXPOSE 7860

# Health check: Streamlit responds on /
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

CMD ["bash", "start.sh"]
