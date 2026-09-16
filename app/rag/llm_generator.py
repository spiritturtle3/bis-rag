from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from app.rag.llm_validator import validate_llm_answer

load_dotenv()


class LLMProviderError(Exception):
    pass


def _build_prompt(
    query: str,
    recommendations: list[dict],
    evidence: list[dict] | None = None,
) -> str:
    payload = {
        "query": query,
        "recommendations": recommendations,
        "evidence": evidence or [],
    }

    return f"""
You are an expert assistant for Indian Standards and procurement specifications.

Answer the user's procurement query using ONLY the supplied RAG results and evidence.

Rules:
- Do not invent Indian Standards.
- You may mention ONLY standards present in the supplied RAG results.
- Do not introduce a standard merely because it is related or commonly known.
- Do not invent clauses, editions, amendments, certifications, or requirements.
- Clearly distinguish the role of each retrieved standard.
- "Primary" means the standard directly governing the procured product or its main technical requirements.
- "Supporting" means a standard that directly supports the primary standard or is needed for an identified aspect of the product specification.
- "Related/Reference" means a potentially relevant standard that should be reviewed if applicable, but should NOT be presented as a direct requirement for the procured product.
- Use "Related/Reference" when the retrieved standard is relevant to the surrounding application or infrastructure but does not directly govern the main product.
- Do not turn every retrieved standard into a Primary or Supporting recommendation.
- If evidence is insufficient to establish direct applicability, prefer "Related/Reference" or omit the standard.
- Preserve standard numbers exactly as supplied.
- Mention certification only when supported by the supplied evidence.
- Mention amendments when supplied.
- Give a concise, procurement-focused explanation.
- Respond in the same language as the user's query when practical.
- Return valid JSON only.

Required JSON format:
{{
  "summary": "short summary",
  "recommendations": [
    {{
      "standardNumber": "exact standard number from RAG",
      "applicability": "Primary, Supporting, or Related/Reference",
      "reason": "evidence-grounded reason"
    }}
  ],
  "certification": [],
  "testing": [],
  "warnings": []
}}

RAG DATA:
{json.dumps(payload, ensure_ascii=False, indent=2)}
""".strip()


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("`"):
        text = text.replace("`json", "", 1)
        text = text.replace("`", "")
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMProviderError(
            "LLM returned invalid JSON"
        ) from exc

    if not isinstance(result, dict):
        raise LLMProviderError(
            "LLM response must be a JSON object"
        )

    return result


def generate_with_gemini(
    prompt: str,
    model: str = "gemini-3.6-flash",
) -> dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise LLMProviderError(
            "GEMINI_API_KEY is not configured"
        )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.interactions.create(
            model=model,
            input=prompt,
        )

        return _extract_json(response.output_text)

    except Exception as exc:
        raise LLMProviderError(
            f"Gemini failed: {exc}"
        ) from exc


def generate_with_groq(
    prompt: str,
    model: str = "llama-3.3-70b-versatile",
) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise LLMProviderError(
            "GROQ_API_KEY is not configured"
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return valid JSON only. "
                        "Use only supplied evidence and "
                        "only standards present in the RAG results."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        return _extract_json(
            response.choices[0].message.content
        )

    except Exception as exc:
        raise LLMProviderError(
            f"Groq failed: {exc}"
        ) from exc


def generate_with_openrouter(
    prompt: str,
    model: str = "openrouter/free",
) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise LLMProviderError(
            "OPENROUTER_API_KEY is not configured"
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return valid JSON only. "
                        "Use only supplied evidence and "
                        "only standards present in the RAG results."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        return _extract_json(
            response.choices[0].message.content
        )

    except Exception as exc:
        raise LLMProviderError(
            f"OpenRouter failed: {exc}"
        ) from exc


def deterministic_fallback(
    query: str,
    recommendations: list[dict],
) -> dict[str, Any]:
    output = []

    for recommendation in recommendations:
        output.append(
            {
                "standardNumber": recommendation.get(
                    "standardNumber",
                    "",
                ),
                "applicability": "Supporting",
                "reason": recommendation.get(
                    "scope",
                    recommendation.get(
                        "bestChunk",
                        "Retrieved as a relevant standard.",
                    ),
                ),
            }
        )

    return {
        "summary": (
            "Recommendations generated from "
            "retrieved BIS standards. LLM explanation "
            "was unavailable."
        ),
        "recommendations": output,
        "certification": [],
        "testing": [],
        "warnings": [
            "LLM providers were unavailable; "
            "results are based directly on RAG retrieval."
        ],
    }


def generate_answer(
    query: str,
    recommendations: list[dict],
    evidence: list[dict] | None = None,
) -> dict[str, Any]:

    prompt = _build_prompt(
        query,
        recommendations,
        evidence,
    )

    providers = [
        ("gemini", generate_with_gemini),
        ("groq", generate_with_groq),
        ("openrouter", generate_with_openrouter),
    ]

    errors = []

    for name, provider in providers:
        try:
            result = provider(prompt)

            result = validate_llm_answer(
                result,
                recommendations,
            )

            result["_provider"] = name

            return result

        except LLMProviderError as exc:
            errors.append(f"{name}: {exc}")

    fallback = deterministic_fallback(
        query,
        recommendations,
    )

    fallback["_provider"] = "deterministic"
    fallback["_errors"] = errors

    return fallback
