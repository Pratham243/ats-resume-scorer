import os
import json
import logging
import re
from typing import Any, Dict, List, Optional, Union
import httpx

from backend.core.config import (
    USE_LOCAL_LLM,
    GROQ_API_KEY,
    GROQ_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)

logger = logging.getLogger('ats_resume_scorer')

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable not set. Please set it in .env or switch to USE_LOCAL_LLM=true.")
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


def _call_groq(system_prompt: str, user_prompt: str, temperature: float = 0.0, max_tokens: int = 4096) -> str:
    """Call the Groq Cloud API for ultra-fast Llama-3 inference."""
    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _call_ollama(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    """
    Call a local Ollama instance for 100% GDPR-compliant, on-premise inference.
    No resume or PII data leaves the host environment.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    try:
        with httpx.Client(timeout=180.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "").strip()
    except httpx.ConnectError as err:
        logger.error(f"Failed to connect to local Ollama at {OLLAMA_BASE_URL}: {err}")
        raise RuntimeError(
            f"Cannot connect to local Ollama at {OLLAMA_BASE_URL}. "
            "Ensure Ollama is running (`ollama serve`) and the model is downloaded (`ollama pull llama3`)."
        ) from err
    except Exception as err:
        logger.error(f"Error during Ollama inference: {err}")
        raise RuntimeError(f"Ollama inference error: {err}") from err


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.0, max_tokens: int = 4096) -> str:
    """
    Unified LLM router. Checks USE_LOCAL_LLM environment variable:
    - If True: Routes to local Ollama instance (GDPR compliant).
    - If False: Routes to Groq Cloud API (High speed).
    """
    if USE_LOCAL_LLM:
        logger.info(f"[GDPR Mode] Routing LLM call to local Ollama instance ({OLLAMA_MODEL})")
        return _call_ollama(system_prompt, user_prompt, temperature)
    else:
        logger.info(f"[Cloud Mode] Routing LLM call to Groq API ({GROQ_MODEL})")
        try:
            return _call_groq(system_prompt, user_prompt, temperature, max_tokens)
        except Exception as groq_err:
            logger.warning(f"Groq API call failed: {groq_err}. Checking if local Ollama fallback is available...")
            # Optional resilience: if Ollama is accessible, fallback gracefully
            try:
                fallback_result = _call_ollama(system_prompt, user_prompt, temperature)
                logger.info("Successfully completed inference using local Ollama fallback.")
                return fallback_result
            except Exception:
                raise groq_err


def clean_json_string(text: str) -> str:
    """Strip markdown code fences and whitespace from LLM outputs."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
        cleaned = cleaned[first_newline + 1:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def extract_json_from_text(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """Attempt direct parse, then fallback to regex match of outermost brackets."""
    cleaned = clean_json_string(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try matching first {...} or [...] block
    match_obj = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match_obj:
        try:
            return json.loads(match_obj.group(1))
        except json.JSONDecodeError:
            pass

    return None


def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
    retry_prompt: Optional[str] = None
) -> Union[Dict[str, Any], List[Any]]:
    """
    Executes an LLM request ensuring the returned content is valid JSON.
    Performs 1 strict retry if initial response fails parsing.
    """
    raw_response = call_llm(system_prompt, user_prompt, temperature=temperature)
    parsed = extract_json_from_text(raw_response)

    if parsed is not None:
        return parsed

    logger.warning("First LLM JSON parse attempt failed. Retrying with strict output instructions...")
    strict_user_prompt = (
        (retry_prompt or user_prompt)
        + "\n\nCRITICAL ERROR: Your previous response was not valid JSON. "
          "Return ONLY a raw JSON object or array. Do NOT include markdown code fences, headers, or conversational text."
    )

    retry_response = call_llm(system_prompt, strict_user_prompt, temperature=0.0)
    retry_parsed = extract_json_from_text(retry_response)

    if retry_parsed is not None:
        return retry_parsed

    raise ValueError(
        f"LLM failed to return valid JSON after retry. First 300 chars of response:\n{retry_response[:300]}"
    )
