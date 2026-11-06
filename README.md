---
title: ATS Resume Scorer
emoji: 🎯
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: true
license: mit
short_description: AI-powered resume scoring — FastAPI + spaCy + Llama 3
---

# 🎯 AI Resume ATS Scorer & Optimizer

> **Enterprise-grade, Multi-Agent Applicant Tracking System (ATS) and career alignment engine built with FastAPI, Streamlit, spaCy, Sentence-Transformers, Groq (Llama 3), Ollama (GDPR Local LLM), and Supabase.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203-F55036?style=flat)](https://groq.com)
[![Ollama](https://img.shields.io/badge/Ollama-GDPR%20Local%20LLM-black?style=flat&logo=ollama)](https://ollama.com)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com)

**Target Repository:** [https://github.com/Pratham243/ats-resume-scorer](https://github.com/Pratham243/ats-resume-scorer)  
**Author & Sole Contributor:** Prathamesh Shimpi ([@Pratham243](https://github.com/Pratham243))

---

## 🚀 Key Highlights & Capabilities

* **Decoupled Modern Architecture:** Decouples the **Streamlit** reactive user interface from an asynchronous, high-throughput **FastAPI** backend microservice.
* **Autonomous Multi-Agent Pipeline:**
  * **Extractor Agent:** High-precision resume & job description parser enforcing strict Pydantic schemas without hallucinations.
  * **Critic Agent:** Analytical hiring evaluator measuring keyword overlap, entity density, experience timeline integrity, and identifying underperforming bullet points.
  * **Drafter Agent:** Technical career coach synthesizing high-converting bullet rewrites using Google's **STAR methodology** (Situation, Task, Action, Result) with quantified business metrics.
* **Hybrid Semantic & Exact Matching NLP:** Integrates **spaCy (`en_core_web_md`)** Named Entity Recognition with dense 384-dimensional **Sentence-Transformers (`all-MiniLM-L6-v2`)** vector cosine similarity to understand conceptual engineering equivalence.
* **GDPR Local LLM Toggle:** Single environment variable (`USE_LOCAL_LLM=true`) routes all AI inferences to an on-premise/local **Ollama** daemon for zero-data-leakage compliance.
* **DevOps & Cloud Native:** Complete multi-container orchestration with **Docker & Docker Compose**, pre-caching ML models for instantaneous container startups.
* **Persistent History & Authentication:** Secure JWT-based user session handling and historical analysis tracking backed by **Supabase Postgres**.
* **Automated PDF Export:** Multi-page executive ATS audit reports rendered dynamically via **WeasyPrint** and **Jinja2**.

---

## 🏛️ System Architecture

```
                                  USER INTERFACE (Streamlit :8501)
                                                 │
                                  REST API / Multipart File Upload
                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FASTAPI BACKEND (:8000)                                  │
│                                                                                        │
│   [ File Parser ] ──► Extracted Raw Text (PyMuPDF / pdfplumber / docx)                 │
│                              │                                                         │
│                              ▼                                                         │
│                     [ EXTRACTOR AGENT ]                                                │
│         (Structured Skills, Work History, Education, Certifications)                   │
│                              │                                                         │
│         ┌────────────────────┴─────────────────────┐                                   │
│         ▼                                          ▼                                   │
│  spaCy NER (en_core_web_md)               Sentence-Transformers                        │
│  Entity & Keyword Extraction              (all-MiniLM-L6-v2 Embeddings)                │
│         │                                          │                                   │
│         └────────────────────┬─────────────────────┘                                   │
│                              ▼                                                         │
│                      [ CRITIC AGENT ]                                                  │
│              - ATS Rubric Weighted Scoring (0–100)                                     │
│              - Keyword Match & Skills Gap Analysis                                     │
│              - Weak / Metric-Sparse Bullet Detection                                   │
│                              │                                                         │
│                              ▼                                                         │
│                      [ DRAFTER AGENT ]                                                 │
│              - Google XYZ / STAR Framework Rewrites                                    │
│              - Quantified Business Metric Ingestion                                    │
│                              │                                                         │
│           ┌──────────────────┴──────────────────┐                                      │
│           ▼                                     ▼                                      │
│    Cloud Inference                      GDPR Local Inference                           │
│   (Groq API / Llama 3)                 (Ollama Daemon / Llama 3)                       │
│  [USE_LOCAL_LLM=false]                    [USE_LOCAL_LLM=true]                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
            │                                                      │
            ▼                                                      ▼
  [ Supabase Database ]                                   [ WeasyPrint Engine ]
  (History & Auth Tracking)                               (Executive PDF Audit)
```

---

## ⚖️ ATS Scoring Rubric Breakdown

| Category | What is Evaluated | Weight |
|---|---|---|
| **Keywords** | Fuzzy and semantic overlap between candidate skills and JD requirements | **25%** |
| **Content Depth** | Quantified metrics (%, $, latency, throughput, scale) and achievement verbs | **25%** |
| **Formatting** | Clean section hierarchies, standard ATS headers, parseable text structure | **20%** |
| **Skill Validation** | Cross-verification that declared skills are proven inside projects/experience | **15%** |
| **ATS Compatibility** | Layout compliance, absence of nested tables/columns, contact info privacy | **15%** |

---

## 📂 Target Directory Structure

```
ats-resume-scorer/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Supabase JWT verification & guest fallback
│   │   └── routes.py                # REST endpoints (/analyze-resume, /history, /generate-pdf)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                # Pydantic environment configurations & model settings
│   ├── database/
│   │   ├── __init__.py
│   │   └── supabase_db.py           # Async Supabase REST client for history tracking
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic schemas (Agent models, STAR rewrites, ATS rubrics)
│   ├── services/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py        # Unified Groq vs. Ollama router with JSON healing
│   │   │   ├── extractor_agent.py   # High-precision schema extraction
│   │   │   ├── critic_agent.py      # Rubric scoring & weak bullet identification
│   │   │   └── drafter_agent.py     # STAR method bullet point optimizer
│   │   ├── ats_scorer.py            # NLP scoring logic & skill verification
│   │   ├── feedback_engine.py       # Actionable feedback and issue diagnostic rules
│   │   ├── jd_matcher.py            # Cosine similarity and keyword gap matching
│   │   ├── pdf_export.py            # WeasyPrint PDF compiler
│   │   ├── recommendation_engine.py # Priority recommendations generator
│   │   ├── report_generator.py      # HTML Jinja2 report pipeline
│   │   ├── resume_analyzer.py       # Multi-Agent pipeline orchestrator
│   │   └── resume_parser.py         # Multi-format document parser (PDF, DOCX)
│   ├── templates/                   # Jinja2 HTML templates for PDF reports
│   │   ├── action_items.html
│   │   ├── jd_comparison.html
│   │   ├── quick_actions.html
│   │   └── summary.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py            # File helpers and validation routines
│   │   └── matching.py              # Normalized skill string tokenizers
│   ├── Dockerfile                   # Production backend container definition
│   └── main.py                      # FastAPI application entrypoint & lifespan model loader
├── frontend/
│   ├── .streamlit/
│   │   ├── config.toml              # Streamlit branding & server configs
│   │   └── secrets.toml.example     # Secrets template
│   ├── assets/
│   │   └── styles.css               # Clean SaaS UI styling
│   ├── components/
│   │   ├── __init__.py
│   │   ├── _helpers.py              # Status badges and color helpers
│   │   ├── action_items.py          # Action items checklist
│   │   ├── dashboard.py             # Main results orchestrator
│   │   ├── detailed_feedback.py     # Categorized severity issue cards
│   │   ├── jd_comparison.py         # Keyword overlap and gap display
│   │   ├── recommendations.py       # High/Medium priority cards
│   │   ├── score_display.py         # Gauge score and progress bars
│   │   ├── skill_validation.py      # Validated vs unvalidated skills tags
│   │   ├── star_rewrites.py         # AI Drafter Agent STAR rewrites component
│   │   └── strengths_issues.py      # Summary strengths and critical issues
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py            # Client interface communicating with FastAPI
│   │   └── supabase_client.py       # Client-side Supabase auth integration
│   ├── views/
│   │   ├── __init__.py
│   │   ├── history.py               # Historical audits dashboard
│   │   ├── landing.py               # Landing page and feature overview
│   │   ├── resources.py             # ATS guidelines and tips
│   │   └── scorer.py                # Main interactive resume audit view
│   ├── Dockerfile                   # Production frontend container definition
│   └── streamlit_app.py             # Streamlit application entrypoint
├── jupyter notebooks/               # Research, BERT embeddings experiments, and EDA
│   ├── 01_EDA_and_DATA_prep.ipynb
│   ├── 02_BERT_EMBEDDINGS.ipynb
│   └── 03_BERT_FINETUNEipynb.ipynb
├── .env.example                     # Environment variables specification
├── .gitignore                       # Production gitignore
├── docker-compose.yml               # Multi-service container orchestrator
└── requirements.txt                 # Pinned project dependencies
```

---

## ⚡ Quickstart: Running with Docker (Recommended)

Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.

### 1. Clone the repository
```bash
git clone https://github.com/Pratham243/ats-resume-scorer.git
cd ats-resume-scorer
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` with your API keys:
* Add your `GROQ_API_KEY` from [console.groq.com](https://console.groq.com)
* Add your Supabase keys (if using auth/database), or leave blank for automatic local guest mode.

### 3. Launch Services with Docker Compose
```bash
docker compose up --build
```

* **Frontend UI:** [http://localhost:8501](http://localhost:8501)
* **Backend API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Backend Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🔒 GDPR Compliance: Running with Local Ollama

To ensure 100% data privacy where no resume text or PII ever leaves your local machine or private cloud:

1. In `.env`, set:
   ```env
   USE_LOCAL_LLM=true
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```
2. Start your local Ollama daemon and pull the target model:
   ```bash
   ollama serve
   ollama pull llama3
   ```
3. Alternatively, launch the bundled Ollama Docker profile:
   ```bash
   docker compose --profile local-llm up --build
   ```

The backend's `LLM Router` will automatically detect `USE_LOCAL_LLM=true` and route all `Extractor`, `Critic`, and `Drafter` agent queries to Ollama.

---

## 🛠️ Manual Local Development (Without Docker)

### 1. Create a Python Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies & Pre-download NLP Models
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

*(Note for Linux users: WeasyPrint requires Cairo and Pango system libraries)*:
```bash
# Ubuntu / Debian
sudo apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev
```

### 3. Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Streamlit Frontend
In a second terminal (with `venv` activated):
```bash
streamlit run frontend/streamlit_app.py
```

Visit [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 API Verification & Testing

Verify that all NLP pipelines and model weights are initialized:
```bash
curl -X GET http://localhost:8000/api/v1/health
```

Expected Response:
```json
{
  "status": "healthy",
  "nlp_loaded": true,
  "embedder_loaded": true
}
```

Trigger an automated analysis via curl:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-resume" \
  -H "Authorization: Bearer guest-token" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Senior Backend Engineer with Python, FastAPI, Docker, and Kubernetes experience."
```

---

## 👨‍💻 Author & Attribution

* **Sole Contributor & Author:** **Prathamesh Shimpi**
* **GitHub Profile:** [@Pratham243](https://github.com/Pratham243)
* **Target Project Repository:** [https://github.com/Pratham243/ats-resume-scorer](https://github.com/Pratham243/ats-resume-scorer)

---

## 📄 License
This project is licensed under the MIT License — feel free to use and adapt it for personal and enterprise resume auditing pipelines.
