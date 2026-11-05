import logging
from typing import Dict, List, Optional
import spacy
from sentence_transformers import SentenceTransformer

from backend.models.schemas import (
    ExtractedResumeData,
    ExtractedJDData,
    STARBulletRewrite,
)
from backend.services.agents.extractor_agent import ExtractorAgent
from backend.services.agents.critic_agent import CriticAgent
from backend.services.agents.drafter_agent import DrafterAgent

logger = logging.getLogger('ats_resume_scorer')


def analyze_full_resume(
    resume_text: str,
    nlp: spacy.Language,
    embedder: SentenceTransformer,
    job_description: Optional[str] = None,
) -> Dict:
    """
    Multi-Agent Orchestrator Pipeline:
    1. Extractor Agent: Ingests unstructured resume and extracts strict JSON schema.
    2. Critic Agent: Compares parsed schema to JD and ATS rubrics, generating weighted scores
       and identifying underperforming bullet points.
    3. Drafter Agent: Generates STAR-method (Situation, Task, Action, Result) bullet point rewrites.
    """
    logger.info("Step 1: Ingesting resume text with Extractor Agent...")
    resume_data: ExtractedResumeData = ExtractorAgent.extract_resume(resume_text)

    jd_data: Optional[ExtractedJDData] = None
    has_jd = bool(job_description and job_description.strip())
    if has_jd:
        logger.info("Step 1b: Ingesting Job Description with Extractor Agent...")
        jd_data = ExtractorAgent.extract_job_description(job_description.strip())

    logger.info("Step 2: Performing analytical evaluation with Critic Agent...")
    critique = CriticAgent.evaluate(
        resume_data=resume_data,
        resume_text=resume_text,
        nlp=nlp,
        embedder=embedder,
        jd_data=jd_data,
        jd_text=job_description.strip() if has_jd else None,
    )

    logger.info("Step 3: Synthesizing STAR bullet rewrites with Drafter Agent...")
    weak_bullets = critique.get("weak_bullets", [])
    target_role = jd_data.job_title if jd_data else (resume_data.experience[0].job_title if resume_data.experience else None)
    missing_keywords = critique.get("missing_keywords", [])

    star_rewrites: List[STARBulletRewrite] = DrafterAgent.generate_star_rewrites(
        weak_bullets=weak_bullets,
        target_role=target_role,
        missing_keywords=missing_keywords,
    )

    # Compile unified response
    response_payload = {
        "ATS_score": critique["ats_score"],
        "ats_score": critique["ats_score"],
        "component_scores": critique["component_scores"].model_dump(),
        "issues_summary": critique["issues_summary"],
        "detailed_feedback": critique["detailed_feedback"],
        "jd_match_analysis": critique["jd_comparison"],
        "jd_comparison": critique["jd_comparison"],
        "skill_validation_details": critique["skill_validation_details"].model_dump(),
        "star_rewrites": [r.model_dump() for r in star_rewrites],
        "strengths": critique["strengths"],
        "critical_issues": critique["critical_issues"],
        "matched_keywords": critique["matched_keywords"],
        "missing_keywords": critique["missing_keywords"],
        "skills": critique["skills"],
        "raw_extracted_resume": resume_data.model_dump(),
        "experience_months": sum(e.duration_months for e in resume_data.experience),
    }

    logger.info(f"Analysis complete. Overall ATS Score: {critique['ats_score']}/100 with {len(star_rewrites)} STAR rewrites.")
    return response_payload
