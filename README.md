# 🎯 ATS Resume Scorer - AI-Powered Resume Feedback Tool

> **Full-stack GenAI web app** that scores how well your resume matches a job description and gives you category-by-category, LLM-powered improvement suggestions.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com)

**🔗 Live Demo:** [your-app-url-here]

---

## What This Does

Paste a job description + upload your resume → get back:

- **ATS Score (0–100)** broken down by: formatting, keywords, content depth, skill validation, ATS compatibility
- **LLM-generated suggestions** for each failing category (powered by Groq Llama 3)
- **Downloadable PDF report** of the full analysis
- **History dashboard** — log in and revisit every previous analysis

---

## Screenshot

*(Add a screenshot of the Streamlit UI here)*

---

## How It Works

```
Resume (PDF/DOC/DOCX)  +  Job Description (text)
              │
              ▼
      FastAPI Backend
              │
      ┌───────┴────────┐
      │                │
      ▼                ▼
  spaCy NLP       Sentence-Transformers
  (skill & exp    (semantic similarity
   extraction)     scoring)
      │                │
      └───────┬────────┘
              │
              ▼
    ATS Score Breakdown
    (5 categories, weighted)
              │
              ▼
    Groq API (Llama 3)
    (improvement suggestions
     per failing category)
              │
              ▼
    Supabase (save to history)
              │
              ▼
    Streamlit UI
    + PDF Export (WeasyPrint)
```

---

## Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| NLP | spaCy (en_core_web_md) |
| Semantic Scoring | Sentence-Transformers (all-MiniLM-L6-v2) |
| LLM Suggestions | Groq API (Llama 3 70B) |
| Frontend | Streamlit |
| Auth + Database | Supabase (email/password + Google OAuth, Postgres) |
| PDF Export | WeasyPrint + Jinja2 |
| File Parsing | python-docx, PyMuPDF |

---

## ATS Scoring Breakdown

| Category | What's Measured | Weight |
|---|---|---|
| **Keywords** | JD keyword overlap (NLP + semantic) | 30% |
| **Content** | Quantified achievements, depth of experience | 25% |
| **Skills** | Validated against JD skill requirements | 20% |
| **Formatting** | Section structure, bullet length, readability | 15% |
| **ATS Compatibility** | Parseable fonts, no tables, standard headers | 10% |

---

## How to Run

```bash
git clone https://github.com/Pratham243/ats-resume-scorer
cd ats-resume-scorer

# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
streamlit run frontend/app.py
```

Add your Groq API key and Supabase credentials to `.env` (see `.env.example`).

---

## Features

- ✅ Resume upload (PDF, DOC, DOCX)
- ✅ Semantic + keyword ATS scoring (5 categories)
- ✅ LLM improvement suggestions per category
- ✅ User accounts with history (Supabase + Google OAuth)
- ✅ PDF report export
- ✅ Live deployed (Streamlit Cloud / Railway)

---

*Full-stack GenAI product · by [Prathamesh Shimpi](https://linkedin.com/in/prathamesh-shimpi0501)*
