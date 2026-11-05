"""
Legacy parser adapter module.
Delegates to the modern ExtractorAgent for multi-agent architecture compatibility.
"""
from typing import Dict
from backend.services.agents.extractor_agent import ExtractorAgent

def parse_resume(raw_text: str) -> Dict:
    """Parse resume text into structured dictionary using ExtractorAgent."""
    extracted = ExtractorAgent.extract_resume(raw_text)
    return extracted.model_dump()

def parse_job_description(raw_text: str) -> Dict:
    """Parse job description text into structured dictionary using ExtractorAgent."""
    extracted = ExtractorAgent.extract_job_description(raw_text)
    return extracted.model_dump()
