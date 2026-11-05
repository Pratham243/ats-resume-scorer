from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# ── Extractor Agent Schemas ──

class ExperienceItem(BaseModel):
    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    duration_months: int = 0
    description: str = ""
    bullet_points: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""

class ProjectItem(BaseModel):
    title: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)

class ExtractedResumeData(BaseModel):
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    professional_summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    action_verbs: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class ExtractedJDData(BaseModel):
    job_title: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required: str = ""
    education_required: str = ""
    key_responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

# ── Drafter Agent Schemas (STAR Method) ──

class STARBulletRewrite(BaseModel):
    original: str
    star_situation: str = ""
    star_task: str = ""
    star_action: str = ""
    star_result: str = ""
    improved_bullet: str
    impact_explanation: str

# ── Analysis & Scorer Schemas ──

class ComponentScores(BaseModel):
    formatting: float
    keywords: float
    content: float
    skill_validation: float
    ats_compatibility: float

class JDComparison(BaseModel):
    match_percentage: float
    semantic_similarity: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    skills_gap: List[str]

class SkillValidationDetails(BaseModel):
    validated: List[Dict[str, Any]] = Field(default_factory=list)       # [{'skill': str, 'projects': [str]}]
    unvalidated: List[str] = Field(default_factory=list)                # ['Flask', 'A/B Testing', ...]
    total: int = 0
    validated_count: int = 0
    validation_pct: float = 0.0

class IssueDetail(BaseModel):
    issue_title: str
    severity_level: str
    ats_impact: str
    explanation: str
    where_it_appears: str
    how_to_fix: str
    action_items: List[str] = Field(default_factory=list)
    example_improvement: str

class AnalysisResponse(BaseModel):
    ATS_score: float
    component_scores: ComponentScores
    issues_summary: List[str]
    detailed_feedback: List[IssueDetail]
    jd_match_analysis: Optional[JDComparison] = None
    skill_validation_details: Optional[SkillValidationDetails] = None
    star_rewrites: List[STARBulletRewrite] = Field(default_factory=list)

    # Backward compatibility fields
    ats_score: float
    keyword_match: float = 0.0
    missing_keywords: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    jd_comparison: Optional[JDComparison] = None
    warnings: List[str] = Field(default_factory=list)
    interpretation: str = ""
