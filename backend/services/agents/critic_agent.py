import re
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer

from backend.models.schemas import (
    ExtractedResumeData,
    ExtractedJDData,
    ComponentScores,
    JDComparison,
    SkillValidationDetails,
    IssueDetail,
)
from backend.core.config import SCORE_WEIGHTS, JD_KEYWORD_WEIGHT, JD_SEMANTIC_WEIGHT
from backend.services.jd_matcher import compare_resume_with_jd
from backend.services.ats_scorer import calculate_overall_score, validate_skills_with_projects
from backend.services.feedback_engine import analyze_issues, generate_issues_summary

logger = logging.getLogger('ats_resume_scorer')

WEAK_VERB_PATTERNS = [
    r'\bresponsible for\b',
    r'\bhelped with\b',
    r'\bworked on\b',
    r'\bassisted in\b',
    r'\btasked with\b',
    r'\bparticipated in\b',
    r'\bhandled\b',
    r'\bdid\b',
    r'\bsupported\b',
]

METRIC_PATTERN = r'(\d+[\d,.]*\s*(?:%|percent|k|m|million|billion|users|clients|dollars|\$|x|ms|s|hours|days|reduction|increase|boost|scale|throughput))'


class CriticAgent:
    """
    Critic Agent: Performs analytical evaluation, rubric-based weighted scoring,
    and identifies critical qualification gaps and underperforming bullet points.
    """

    @classmethod
    def evaluate(
        cls,
        resume_data: ExtractedResumeData,
        resume_text: str,
        nlp: spacy.Language,
        embedder: SentenceTransformer,
        jd_data: Optional[ExtractedJDData] = None,
        jd_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Conducts comprehensive critique comparing resume against JD and ATS standards.
        """
        resume_dict = resume_data.model_dump()
        skills = resume_data.skills
        projects = [p.model_dump() for p in resume_data.projects]
        experience_entries = [e.model_dump() for e in resume_data.experience]
        keywords = resume_data.keywords
        action_verbs = resume_data.action_verbs

        # 1. Skill Validation against Experience & Projects
        skill_validation = validate_skills_with_projects(
            skills=skills,
            projects=projects,
            experience_entries=experience_entries,
            embedder=embedder,
        )

        # 2. JD Comparison & Semantic Alignment
        jd_comparison_result = None
        jd_keywords = None

        if jd_text and jd_text.strip():
            if jd_data:
                jd_keywords = list(set(
                    jd_data.keywords + jd_data.required_skills + jd_data.preferred_skills
                ))
            else:
                jd_keywords = []

            jd_comparison_raw = compare_resume_with_jd(
                resume_text=resume_text,
                resume_keywords=keywords,
                resume_skills=skills,
                jd_text=jd_text.strip(),
                jd_keywords=jd_keywords,
                embedder=embedder,
                nlp=nlp,
            )

            jd_comparison_result = JDComparison(
                match_percentage=round(float(jd_comparison_raw.get('match_percentage', 0.0)), 1),
                semantic_similarity=round(float(jd_comparison_raw.get('semantic_similarity', 0.0)), 3),
                matched_keywords=jd_comparison_raw.get('matched_keywords', [])[:25],
                missing_keywords=jd_comparison_raw.get('missing_keywords', [])[:20],
                skills_gap=jd_comparison_raw.get('skills_gap', [])[:15],
            )

        # 3. Component and Overall ATS Scoring
        from backend.utils.file_utils import get_default_grammar_results, get_default_location_results
        grammar_results = get_default_grammar_results()
        location_results = get_default_location_results()

        experience_months = sum(e.duration_months for e in resume_data.experience)

        scores = calculate_overall_score(
            text=resume_text,
            parsed_resume=resume_dict,
            skills=skills,
            keywords=keywords,
            action_verbs=action_verbs,
            skill_validation_results=skill_validation,
            grammar_results=grammar_results,
            location_results=location_results,
            jd_keywords=jd_keywords,
            experience_months=experience_months,
        )

        # 4. Detailed Issue Detection
        contact_info = {
            'email': resume_data.email,
            'phone': resume_data.phone,
            'linkedin': resume_data.linkedin,
            'github': resume_data.github,
            'portfolio': None,
        }

        detailed_feedback = analyze_issues(
            resume_text=resume_text,
            parsed_resume=resume_dict,
            skills=skills,
            projects=projects,
            action_verbs=action_verbs,
            skill_validation=skill_validation,
            scores=scores,
            contact_info=contact_info,
        )

        issues_summary = generate_issues_summary(detailed_feedback)

        # 5. Extract Candidate Weak Bullets for Drafter Agent
        weak_bullets = cls._identify_weak_bullets(resume_data)

        # Strengths & Critical flags
        strengths = cls._compile_strengths(scores, resume_data, jd_comparison_result)
        critical_issues = [
            f"{issue.issue_title}: {issue.how_to_fix}"
            for issue in detailed_feedback
            if issue.severity_level.lower() in ("critical", "high")
        ]

        svd_raw = skill_validation or {}
        skill_val_details = SkillValidationDetails(
            validated=svd_raw.get('validated', []),
            unvalidated=svd_raw.get('unvalidated', []),
            total=svd_raw.get('total', 0),
            validated_count=svd_raw.get('validated_count', 0),
            validation_pct=svd_raw.get('validation_pct', 0.0),
        )

        return {
            "ats_score": round(scores['overall'], 1),
            "component_scores": ComponentScores(
                formatting=scores['breakdown']['formatting'],
                keywords=scores['breakdown']['keywords'],
                content=scores['breakdown']['content'],
                skill_validation=scores['breakdown']['skill_validation'],
                ats_compatibility=scores['breakdown']['ats_compatibility'],
            ),
            "issues_summary": issues_summary,
            "detailed_feedback": detailed_feedback,
            "jd_comparison": jd_comparison_result,
            "skill_validation_details": skill_val_details,
            "strengths": strengths,
            "critical_issues": critical_issues,
            "weak_bullets": weak_bullets,
            "matched_keywords": jd_comparison_result.matched_keywords if jd_comparison_result else [],
            "missing_keywords": jd_comparison_result.missing_keywords if jd_comparison_result else [],
            "skills": skills[:25],
        }

    @classmethod
    def _identify_weak_bullets(cls, resume_data: ExtractedResumeData) -> List[Dict[str, str]]:
        """Identify bullet points lacking quantifiable results or using passive language."""
        candidates = []

        # Check experience bullets
        for exp in resume_data.experience:
            role_label = f"{exp.job_title} at {exp.company}".strip()
            bullets = exp.bullet_points or [b.strip("-*• ") for b in exp.description.split("\n") if b.strip()]

            for bullet in bullets:
                cleaned = bullet.strip()
                if len(cleaned.split()) < 4 or len(cleaned) < 15:
                    continue

                weakness = []
                lower_b = cleaned.lower()

                # Check for weak verbs
                for pattern in WEAK_VERB_PATTERNS:
                    if re.search(pattern, lower_b):
                        weakness.append("Begins with weak/passive verb")
                        break

                # Check for lack of quantified results
                if not re.search(METRIC_PATTERN, lower_b) and not any(ch.isdigit() for ch in cleaned):
                    weakness.append("Lacks quantifiable metrics or measurable outcomes")

                if weakness:
                    candidates.append({
                        "context": role_label or "Experience",
                        "bullet": cleaned,
                        "weakness": "; ".join(weakness),
                    })

        # Check project descriptions if few experience bullets found
        if len(candidates) < 3:
            for proj in resume_data.projects:
                proj_label = f"Project: {proj.title}".strip()
                desc = proj.description.strip()
                if desc and len(desc.split()) >= 4:
                    if not any(ch.isdigit() for ch in desc):
                        candidates.append({
                            "context": proj_label,
                            "bullet": desc,
                            "weakness": "Lacks specific quantifiable metrics or architecture depth",
                        })

        return candidates[:6]  # Return top 6 candidates for rewriting

    @classmethod
    def _compile_strengths(
        cls,
        scores: Dict[str, Any],
        resume_data: ExtractedResumeData,
        jd_comp: Optional[JDComparison]
    ) -> List[str]:
        strengths = []
        breakdown = scores.get('breakdown', {})

        if breakdown.get('formatting', 0) >= 16:
            strengths.append("Excellent layout structure with standard ATS-parseable sections.")
        if breakdown.get('keywords', 0) >= 20:
            strengths.append("Strong keyword density and alignment with target role terminology.")
        if breakdown.get('content', 0) >= 20:
            strengths.append("Substantial experience depth with meaningful project contributions.")
        if breakdown.get('skill_validation', 0) >= 12:
            strengths.append("High correlation between declared skills and hands-on project accomplishments.")
        if jd_comp and jd_comp.match_percentage >= 70:
            strengths.append(f"High JD match alignment ({jd_comp.match_percentage}%) with key requirements.")

        if not strengths:
            strengths.append("Clear foundational sections and contact information.")

        return strengths
