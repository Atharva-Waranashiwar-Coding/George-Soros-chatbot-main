# rag_generator.py

import os
from typing import Optional, Dict, Any

import google.generativeai as genai

DEFAULT_MODEL_NAME = "models/gemini-2.5-flash"


def _resolve_api_key() -> Optional[str]:
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        from soros_backend import secrets  # type: ignore

        return getattr(secrets, "GEMINI_API_KEY", None)
    except Exception:
        return None


class GeminiAnswerGenerator:
    """
    Wrapper around a Gemini model used as the generator in the RAG pipeline.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        api_key: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        key = api_key or _resolve_api_key()
        if not key:
            raise RuntimeError(
                "Gemini API key not configured. Set GOOGLE_API_KEY or GEMINI_API_KEY."
            )

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config: Dict[str, Any] = generation_config or {
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

    def generate(self, prompt: str) -> str:
        prompt = (prompt or "").strip()
        if not prompt:
            raise ValueError("Prompt is empty in GeminiAnswerGenerator.generate().")

        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
        )

        text = None
        try:
            text = response.text
        except Exception:
            text = None

        if text:
            return text.strip()

        parts = []
        for cand in getattr(response, "candidates", []) or []:
            content = getattr(cand, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                t = getattr(part, "text", None)
                if t:
                    parts.append(t)

        if parts:
            return "\n".join(parts).strip()

        finish_reasons = []
        for cand in getattr(response, "candidates", []) or []:
            fr = getattr(cand, "finish_reason", None)
            if fr is not None:
                finish_reasons.append(str(fr))

        fr_info = ", ".join(sorted(set(finish_reasons))) if finish_reasons else "unknown"

        return (
            "The model could not return a normal answer (finish_reason="
            + fr_info
            + "). This often happens due to safety filters or content restrictions.\n\n"
            "For your demo, you can explain that the underlying LLM refused to answer "
            "this exact phrasing. Try rephrasing the question in more general, "
            "educational terms and avoid asking for explicit buy/sell/hold advice."
        )
