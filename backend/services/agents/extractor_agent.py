import logging
from typing import Any, Dict, List
from backend.models.schemas import (
    ExtractedResumeData,
    ExtractedJDData,
    ExperienceItem,
    EducationItem,
    ProjectItem,
)
from backend.services.agents.llm_client import call_llm_json

logger = logging.getLogger('ats_resume_scorer')

RESUME_EXTRACTOR_SYSTEM_PROMPT = (
    "You are an expert ATS Extractor Agent. Your duty is to extract structured, "
    "high-fidelity information from resume text and return strictly valid JSON conforming "
    "to the requested schema. You must extract every technical competency, skill, date, "
    "role, and accomplishment without making assumptions or truncating."
)

RESUME_EXTRACTOR_USER_PROMPT = """Analyze the following resume text and extract the information into this exact JSON structure:
{{
  "name": "Full candidate name",
  "email": "candidate email or null",
  "phone": "candidate phone number or null",
  "linkedin": "LinkedIn URL or username if present, otherwise null",
  "github": "GitHub URL or username if present, otherwise null",
  "professional_summary": "Full text of summary, objective, or profile statement if present, else empty string",
  "skills": ["comprehensive", "list", "of", "all", "technical", "and", "soft", "skills"],
  "experience": [
    {{
      "job_title": "Position Title",
      "company": "Company Name",
      "start_date": "MM/YYYY or Year",
      "end_date": "MM/YYYY, Year, or Present",
      "duration_months": 12,
      "description": "Full summary of responsibilities",
      "bullet_points": [
        "Individual achievement bullet point 1",
        "Individual achievement bullet point 2"
      ]
    }}
  ],
  "education": [
    {{
      "degree": "Degree and Major",
      "institution": "University or College",
      "year": "Graduation Year"
    }}
  ],
  "certifications": ["List of certifications, licenses, or professional credentials"],
  "projects": [
    {{
      "title": "Project Title",
      "description": "Comprehensive explanation of the project",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "action_verbs": ["Action verbs starting bullet points, e.g., Engineered, Spearheaded, Accelerated"],
  "keywords": ["Domain-specific ATS keywords and noun phrases present in the resume"]
}}

Key parsing rules:
1. 'duration_months': Calculate total months between start_date and end_date. If 'Present' or 'Current', calculate to current year.
2. 'bullet_points': Extract each distinct achievement or responsibility bullet point separately.
3. 'skills': Extract all technical frameworks, programming languages, databases, cloud tools, and soft skills mentioned anywhere.
4. Output ONLY the JSON object.

Resume Text:
{raw_text}
"""

JD_EXTRACTOR_SYSTEM_PROMPT = (
    "You are an expert ATS Job Description Extractor Agent. Parse the job description "
    "and output strictly valid JSON detailing requirements, qualifications, and domain keywords."
)

JD_EXTRACTOR_USER_PROMPT = """Extract the requirements from this job description into this exact JSON structure:
{{
  "job_title": "Target job title",
  "required_skills": ["Must-have technical competencies and prerequisites"],
  "preferred_skills": ["Nice-to-have or bonus qualifications"],
  "experience_required": "Years of experience or seniority level required",
  "education_required": "Minimum degree or education required",
  "key_responsibilities": ["Primary job duties and functions"],
  "keywords": ["ATS indexing keywords, acronyms, methodologies, and technical terms"]
}}

Job Description Text:
{raw_text}
"""


class ExtractorAgent:
    """
    Extractor Agent: Parses unstructured resume & JD text into
    strictly-typed, schema-validated Pydantic structures.
    """

    @classmethod
    def extract_resume(cls, raw_text: str) -> ExtractedResumeData:
        """Parse raw resume text into structured ExtractedResumeData."""
        prompt = RESUME_EXTRACTOR_USER_PROMPT.format(raw_text=raw_text)
        data = call_llm_json(
            system_prompt=RESUME_EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.0
        )

        if not isinstance(data, dict):
            data = {}

        # Safe parsing into Pydantic model
        experiences = []
        for exp in data.get("experience", []):
            if isinstance(exp, dict):
                bullets = exp.get("bullet_points", [])
                if not bullets and exp.get("description"):
                    # Split lines if bullets not cleanly arrayed
                    bullets = [b.strip("-*• ") for b in exp.get("description", "").split("\n") if b.strip()]
                experiences.append(
                    ExperienceItem(
                        job_title=exp.get("job_title", ""),
                        company=exp.get("company", ""),
                        start_date=exp.get("start_date", ""),
                        end_date=exp.get("end_date", ""),
                        duration_months=int(exp.get("duration_months", 0) or 0),
                        description=exp.get("description", ""),
                        bullet_points=bullets,
                    )
                )

        educations = []
        for edu in data.get("education", []):
            if isinstance(edu, dict):
                educations.append(
                    EducationItem(
                        degree=edu.get("degree", ""),
                        institution=edu.get("institution", ""),
                        year=str(edu.get("year", "")),
                    )
                )

        projects = []
        for proj in data.get("projects", []):
            if isinstance(proj, dict):
                projects.append(
                    ProjectItem(
                        title=proj.get("title", ""),
                        description=proj.get("description", ""),
                        technologies=proj.get("technologies", []) if isinstance(proj.get("technologies"), list) else [],
                    )
                )

        return ExtractedResumeData(
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            linkedin=data.get("linkedin"),
            github=data.get("github"),
            professional_summary=data.get("professional_summary", ""),
            skills=data.get("skills", []) if isinstance(data.get("skills"), list) else [],
            experience=experiences,
            education=educations,
            certifications=data.get("certifications", []) if isinstance(data.get("certifications"), list) else [],
            projects=projects,
            action_verbs=data.get("action_verbs", []) if isinstance(data.get("action_verbs"), list) else [],
            keywords=data.get("keywords", []) if isinstance(data.get("keywords"), list) else [],
        )

    @classmethod
    def extract_job_description(cls, raw_text: str) -> ExtractedJDData:
        """Parse raw JD text into structured ExtractedJDData."""
        prompt = JD_EXTRACTOR_USER_PROMPT.format(raw_text=raw_text)
        data = call_llm_json(
            system_prompt=JD_EXTRACTOR_SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.0
        )

        if not isinstance(data, dict):
            data = {}

        return ExtractedJDData(
            job_title=data.get("job_title", ""),
            required_skills=data.get("required_skills", []) if isinstance(data.get("required_skills"), list) else [],
            preferred_skills=data.get("preferred_skills", []) if isinstance(data.get("preferred_skills"), list) else [],
            experience_required=str(data.get("experience_required", "")),
            education_required=str(data.get("education_required", "")),
            key_responsibilities=data.get("key_responsibilities", []) if isinstance(data.get("key_responsibilities"), list) else [],
            keywords=data.get("keywords", []) if isinstance(data.get("keywords"), list) else [],
        )
