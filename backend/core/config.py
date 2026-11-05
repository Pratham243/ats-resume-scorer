import os
from pathlib import Path

# Load .env from the project root (two levels up from this file) explicitly —
# load_dotenv() with no args relies on caller-frame inspection that can fail
# silently under uvicorn reload, leaving env vars unset.
try:
    from dotenv import load_dotenv
    _ENV_PATH = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(_ENV_PATH)
except ImportError:
    pass

# API metadata
APP_TITLE = 'ATS Resume Analyzer API'
APP_VERSION = '2.0.0'
APP_DESCRIPTION = 'Multi-Agent ATS Resume Scorer & Career Alignment Platform'

ALLOWED_ORIGINS = [
    '*',
    'http://localhost:8501',
    'http://127.0.0.1:8501',
    'http://localhost:3000',
    'https://appapppy-ktwxupi73vqhjzweksze9d.streamlit.app/'
]

# File upload limits
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported MIME types and extensions
SUPPORTED_MIME_TYPES = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
}

SUPPORTED_EXTENSIONS = {'.pdf', '.doc', '.docx'}

# NLP & ML Models
SPACY_MODEL_PRIMARY = os.getenv("SPACY_MODEL_PRIMARY", "en_core_web_md")
SPACY_MODEL_SECONDARY = os.getenv("SPACY_MODEL_SECONDARY", "en_core_web_sm")
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

# Score component weights (Configurable business logic)
SCORE_WEIGHTS = {
    "formatting": 20,
    "keywords": 25,
    "content": 25,
    "skill_validation": 15,
    "ats_compatibility": 15,
}

JD_KEYWORD_WEIGHT = 0.6
JD_SEMANTIC_WEIGHT = 0.4

# LLM Configuration & GDPR Local Toggle
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").strip().lower() in ("true", "1", "yes")
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Supabase Auth & Database
SUPABASE_URL = os.getenv('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')               # service_role — DB writes (bypasses RLS)
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')     # public anon — frontend auth calls
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '') # used by backend to verify access tokens

# Guest access fallback for local dev / unconfigured Supabase
ALLOW_GUEST_ACCESS = os.getenv('ALLOW_GUEST_ACCESS', 'true').strip().lower() in ("true", "1", "yes")
