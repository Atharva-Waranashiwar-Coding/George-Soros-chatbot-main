# rag_generator.py

import os
from typing import Optional, Dict, Any

import google.generativeai as genai

# Default model for the Soros RAG chatbot
DEFAULT_MODEL_NAME = "models/gemini-2.5-flash"


class GeminiAnswerGenerator:
    """
    Wrapper around a Gemini model used as the generator in the RAG pipeline.

    - Uses GOOGLE_API_KEY from the environment.
    - Default model: models/gemini-2.5-flash (fast, high-quality).
    - You call .generate(prompt) with a fully constructed prompt
      (system instructions + context + question).
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        api_key: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        # 1) Resolve API key
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError(
                "GOOGLE_API_KEY not found. "
                "Set it in your environment before running the chatbot."
            )

        # 2) Configure the Gemini client
        genai.configure(api_key=key)

        # 3) Create the GenerativeModel instance
        self.model = genai.GenerativeModel(model_name)

        # 4) Default generation config tuned for your use-case:
        # low-ish temperature for analytical Soros-style answers
        self.generation_config: Dict[str, Any] = generation_config or {
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

    def generate(self, prompt: str) -> str:
        """
        Generate an answer from Gemini given a full prompt string.

        The prompt should already include:
        - Soros persona / system instructions
        - Retrieved RAG context
        - Optional market snapshot
        - The user question
        - Explicit output format instructions
        """
        prompt = (prompt or "").strip()
        if not prompt:
            raise ValueError("Prompt is empty in GeminiAnswerGenerator.generate().")

        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
        )

        # --- First try: safe access to response.text ---
        text = None
        try:
            text = response.text  # this can raise ValueError if no valid Part
        except Exception:
            text = None

        if text:
            return text.strip()

        # --- Second try: manually reconstruct from candidates/parts ---
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

        # --- Final fallback: likely safety / blocked content ---
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


# Simple manual test (optional)
if __name__ == "__main__":
    gen = GeminiAnswerGenerator()
    reply = gen.generate("Say one short, harmless test sentence.")
    print("Gemini 2.5 Flash test reply:\n", reply)
