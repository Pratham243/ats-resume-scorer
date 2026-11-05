import logging
from typing import Any, Dict, List, Optional

from backend.models.schemas import STARBulletRewrite
from backend.services.agents.llm_client import call_llm_json

logger = logging.getLogger('ats_resume_scorer')

DRAFTER_SYSTEM_PROMPT = (
    "You are an elite Technical Resume Drafter and Executive Career Coach. "
    "Your objective is to transform weak, passive, or metric-poor resume bullet points "
    "into high-impact statements using the STAR methodology (Situation, Task, Action, Result) "
    "and Google's 'Accomplished [X] as measured by [Y] by doing [Z]' formula.\n\n"
    "Rules for rewrites:\n"
    "1. Begin with a powerful active verb (e.g., Engineered, Spearheaded, Optimized, Orchestrated, Automated).\n"
    "2. Weave in concrete technical tools, frameworks, and architectural concepts.\n"
    "3. Incorporate realistic, quantified business or performance impact (e.g., percentages, latencies, cost savings, scale, user count).\n"
    "4. Return strictly valid JSON array."
)

DRAFTER_USER_PROMPT = """Transform the following weak bullet points into high-impact STAR-format bullet points.
{context_info}

Bullets to rewrite:
{bullets_json}

Return ONLY a JSON array with this exact structure:
[
  {{
    "original": "Original bullet text",
    "star_situation": "The context or challenge faced",
    "star_task": "The objective or engineering responsibility",
    "star_action": "The specific technical action taken, architecture implemented, or tools leveraged",
    "star_result": "The quantified result or business outcome achieved",
    "improved_bullet": "Full polished bullet point combining Action + Context + Quantified Metric",
    "impact_explanation": "Why this revision elevates ATS ranking and recruiter interest"
  }}
]
"""


class DrafterAgent:
    """
    Drafter Agent: Synthesizes findings from Extractor and Critic to craft
    STAR-method (Situation, Task, Action, Result) bullet point rewrites.
    """

    @classmethod
    def generate_star_rewrites(
        cls,
        weak_bullets: List[Dict[str, str]],
        target_role: Optional[str] = None,
        missing_keywords: Optional[List[str]] = None,
    ) -> List[STARBulletRewrite]:
        """Generate high-yield STAR rewrites for identified weak bullet points."""
        if not weak_bullets:
            logger.info("No weak bullets provided to Drafter Agent; skipping rewrite generation.")
            return []

        # Limit to top 4 bullets to maintain response speed and quality
        selected_bullets = weak_bullets[:4]

        context_lines = []
        if target_role:
            context_lines.append(f"Target Role: {target_role}")
        if missing_keywords:
            context_lines.append(f"Keywords to naturally incorporate if applicable: {', '.join(missing_keywords[:8])}")

        context_info = "\n".join(context_lines)

        bullets_payload = [
            {
                "context": b.get("context", "Work Experience"),
                "bullet": b.get("bullet", ""),
                "flaw": b.get("weakness", "Lacks quantified impact"),
            }
            for b in selected_bullets
        ]

        import json
        prompt = DRAFTER_USER_PROMPT.format(
            context_info=context_info,
            bullets_json=json.dumps(bullets_payload, indent=2)
        )

        try:
            results = call_llm_json(
                system_prompt=DRAFTER_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.3
            )

            if not isinstance(results, list):
                logger.warning(f"Drafter Agent returned non-list response: {type(results)}")
                return []

            rewrites = []
            for item in results:
                if not isinstance(item, dict):
                    continue
                rewrites.append(
                    STARBulletRewrite(
                        original=item.get("original", ""),
                        star_situation=item.get("star_situation", ""),
                        star_task=item.get("star_task", ""),
                        star_action=item.get("star_action", ""),
                        star_result=item.get("star_result", ""),
                        improved_bullet=item.get("improved_bullet", ""),
                        impact_explanation=item.get("impact_explanation", ""),
                    )
                )
            return rewrites

        except Exception as e:
            logger.error(f"Drafter Agent failed to generate STAR rewrites: {e}")
            return []
