from __future__ import annotations

import json
import os
import time
from typing import Any

from dotenv import load_dotenv

from app.rag.llm_validator import validate_llm_answer

load_dotenv()

LLM_TIMEOUT = 3.0


class LLMProviderError(Exception):
    pass


def _build_prompt(
    query: str,
    recommendations: list[dict],
    evidence: list[dict] | None = None,
) -> str:
    compact_recommendations = []

    for item in recommendations:
        compact_recommendations.append({
            "standardNumber": item.get("standardNumber"),
            "title": item.get("title"),
            "scope": item.get("scope"),
            "confidence": item.get("confidence"),
            "currentEdition": item.get("currentEdition"),
            "amendments": item.get("amendments", []),
            "compliance": item.get("compliance", {}),
            "testing": item.get("testingAndInspection", {}),
            "relatedStandards": item.get("relatedStandards", []),
        })

    compact_evidence = []

    for item in evidence or []:
        evidence_items = item.get("evidence", [])
        evidence_points = item.get("evidencePoints", [])

        if isinstance(evidence_items, list):
            evidence_items = evidence_items[:2]

        if isinstance(evidence_points, list):
            evidence_points = evidence_points[:3]

        compact_evidence.append({
            "standardNumber": item.get("standardNumber"),
            "title": item.get("title"),
            "evidencePoints": evidence_points,
            "evidence": evidence_items,
        })

    payload = {
        "query": query,
        "recommendations": compact_recommendations,
        "evidence": compact_evidence,
    }

    return f"""
You are an Indian Standards procurement assistant.

Answer using ONLY the supplied RAG data.

Rules:
- Use ONLY the supplied RAG data. Do not use outside knowledge.
- Never invent standards, clauses, editions, amendments, certifications, legal requirements, or testing requirements.
- Mention only standards present in the RAG data.
- Primary = directly governs the product.
- Supporting = directly supports the product or primary standard.
- Related/Reference = potentially relevant but does not directly govern the product.
- Do not force every retrieved standard into the answer.
- Certification:
  - If certificationRequired is true, you may state that certification is required.
  - If mandatory is true, you may state that it is mandatory.
  - If mandatory is null or missing, DO NOT call certification mandatory.
  - Instead state that mandatory status is not established by the supplied RAG data.
- Amendments: mention only amendments explicitly supplied in the RAG data.
- Testing: mention only testing requirements explicitly supplied in the RAG data.
- Preserve IS numbers exactly.
- Be concise and evidence-grounded.
- Respond in the user's language when practical.
- Return valid JSON only.

Required JSON:
{{
  "summary": "short procurement-focused summary",
  "recommendations": [
    {{
      "standardNumber": "exact IS number",
      "applicability": "Primary, Supporting, or Related/Reference",
      "reason": "short evidence-grounded reason"
    }}
  ],
  "certification": [],
  "testing": [],
  "warnings": []
}}

RAG DATA:
{json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}
""".strip()


def _extract_json(text: str) -> dict[str, Any]:
    if not text:
        raise LLMProviderError("LLM returned empty content")

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "")
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMProviderError("LLM returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise LLMProviderError("LLM response must be a JSON object")

    return result


def generate_with_groq(
    prompt: str,
    model: str = "openai/gpt-oss-20b",
) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise LLMProviderError("GROQ_API_KEY is not configured")

    start = time.perf_counter()
    print("LLM TIMING: Groq request started")

    try:
        from groq import Groq

        client = Groq(
            api_key=api_key,
            timeout=LLM_TIMEOUT,
            max_retries=0,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON. "
                        "Do not use markdown. "
                        "Do not use code fences. "
                        "Use only supplied evidence. "
                        "Mention only standards present in the RAG results."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        elapsed = time.perf_counter() - start

        print(
            f"LLM TIMING: Groq request completed: "
            f"{elapsed:.3f}s"
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise LLMProviderError(
                "Groq returned empty content"
            )

        return _extract_json(content)

    except Exception as exc:
        elapsed = time.perf_counter() - start

        print(
            f"LLM TIMING: Groq failed after "
            f"{elapsed:.3f}s: {exc}"
        )

        raise LLMProviderError(
            f"Groq failed: {exc}"
        ) from exc


def generate_with_mistral(prompt: str) -> str:
    import os
    import time
    from openai import OpenAI

    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise LLMProviderError("MISTRAL_API_KEY is not configured")

    start = time.perf_counter()
    print("LLM TIMING: Mistral request started")

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
            timeout=3.0,
            max_retries=0,
        )

        response = client.chat.completions.create(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return valid JSON only. "
                        "Do not include markdown or code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        elapsed = time.perf_counter() - start
        print(f"LLM TIMING: Mistral request completed: {elapsed:.3f}s")

        content = response.choices[0].message.content

        if not content:
            raise LLMProviderError("Mistral returned empty content")

        return content

    except Exception as exc:
        elapsed = time.perf_counter() - start
        print(f"LLM TIMING: Mistral failed after {elapsed:.3f}s: {exc}")
        raise LLMProviderError(f"Mistral failed: {exc}") from exc


def generate_with_openrouter(
    prompt: str,
    model: str = "openrouter/free",
) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise LLMProviderError(
            "OPENROUTER_API_KEY is not configured"
        )

    start = time.perf_counter()
    print("LLM TIMING: OpenRouter request started")

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=LLM_TIMEOUT,
            max_retries=0,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON. "
                        "Do not use markdown. "
                        "Do not use code fences. "
                        "Use only supplied evidence. "
                        "Mention only standards present in the RAG results."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        elapsed = time.perf_counter() - start

        print(
            f"LLM TIMING: OpenRouter request completed: "
            f"{elapsed:.3f}s"
        )

        content = response.choices[0].message.content

        if not content or not content.strip():
            raise LLMProviderError(
                "OpenRouter returned empty content"
            )

        return _extract_json(content)

    except Exception as exc:
        elapsed = time.perf_counter() - start

        print(
            f"LLM TIMING: OpenRouter failed after "
            f"{elapsed:.3f}s: {exc}"
        )

        raise LLMProviderError(
            f"OpenRouter failed: {exc}"
        ) from exc


def deterministic_fallback(
    query: str,
    recommendations: list[dict],
) -> dict[str, Any]:
    output = []

    for recommendation in recommendations:
        output.append({
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
        })

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
    total_start = time.perf_counter()

    print("LLM TIMING: Building prompt started")

    prompt_start = time.perf_counter()

    prompt = _build_prompt(
        query,
        recommendations,
        evidence,
    )

    print(
        f"LLM TIMING: Prompt building: "
        f"{time.perf_counter() - prompt_start:.3f}s"
    )

    print(
        f"LLM TIMING: Prompt size: "
        f"{len(prompt)} characters"
    )

    providers = [
        ("groq", generate_with_groq),
        ("mistral", generate_with_mistral),
        ("openrouter", generate_with_openrouter),
    ]

    errors = []

    for name, provider in providers:
        provider_start = time.perf_counter()

        try:
            result = provider(prompt)

            validation_start = time.perf_counter()

            result = validate_llm_answer(
                result,
                recommendations,
            )

            print(
                f"LLM TIMING: {name} validation: "
                f"{time.perf_counter() - validation_start:.3f}s"
            )

            result["_provider"] = name

            print(
                f"LLM TIMING: TOTAL generate_answer: "
                f"{time.perf_counter() - total_start:.3f}s"
            )

            return result

        except LLMProviderError as exc:
            elapsed = time.perf_counter() - provider_start

            print(
                f"LLM TIMING: {name} total failed: "
                f"{elapsed:.3f}s"
            )

            errors.append(
                f"{name}: {exc}"
            )

    fallback = deterministic_fallback(
        query,
        recommendations,
    )

    fallback["_provider"] = "deterministic"
    fallback["_errors"] = errors

    print(
        f"LLM TIMING: TOTAL generate_answer: "
        f"{time.perf_counter() - total_start:.3f}s"
    )

    return fallback