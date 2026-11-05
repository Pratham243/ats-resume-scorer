"""
Streamlit Cloud Entrypoint Alias.
Allows deployment using either 'frontend/app.py' or 'frontend/streamlit_app.py'.
"""
import sys
from pathlib import Path
import runpy

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

target_file = Path(__file__).resolve().parent / "streamlit_app.py"
runpy.run_path(str(target_file), run_name="__main__")
