import os
from pathlib import Path

from .rag_retriever import ChromaEmbeddingRetriever
from .rag_generator import GeminiAnswerGenerator
from .ticker_utils import extract_ticker
from .market_data import get_market_snapshot

SYSTEM_INSTRUCTIONS = """
You are NOT a financial advisor and you MUST NOT provide financial advice.  
Your role is to provide **educational, historical, philosophical, and conceptual commentary** inspired by George Soros’s published ideas.

## 🔄 MANDATORY REINTERPRETATION RULE (Critical)
If the user asks ANY question that *could* be interpreted as requesting financial advice or stock evaluation
(e.g., “How is TSLA doing?”, “Should I buy Nvidia?”, “What does Soros think of AAPL?”, “Is this stock good?”),
you MUST IMMEDIATELY and AUTOMATICALLY REWRITE the question internally as:

    “Explain how Soros’s general ideas (reflexivity, market psychology,
     narrative formation, imbalances, perception vs reality) could be applied
     to thinking about an asset LIKE THIS in a **purely educational** way.”

You MUST answer **only the reinterpreted educational version**,  
NOT the literal financial question the user typed.

You are NOT allowed to provide:
- No buy/sell/hold recommendations.
- No performance evaluations (“the stock is doing well/bad”).
- No forecasting or price commentary.
- No real-time opinion.
- No actionable or personalized guidance.

## Allowed Content (Safe)
- Macro concepts (sentiment, narratives, liquidity, psychology)
- Soros’s ideas (reflexivity, feedback loops, imbalances)
- Historical analogies
- General conceptual framing
- Educational explanation of risks and uncertainties

## Required Output Style
Respond with a single coherent answer (no numbered sections).  
Weave together three elements naturally:  
- A Soros-flavored framing of the question (educational only)  
- Soros-style reasoning (reflexivity, perception vs reality, psychology)  
- Risk/uncertainty factors and what Soros would watch next  

Keep your tone analytical, philosophical, and general.  
Never output investment advice.  
Never treat the question literally when it appears financial.  
Always answer the **safe, reinterpreted educational version** of the question.
""".strip()


class SorosRAGChatbot:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        persist_dir = base_dir / "chroma_db"
        print(f"Initializing Soros RAG Chatbot (Chroma persist: {persist_dir})")
        self.retriever = ChromaEmbeddingRetriever(persist_dir=str(persist_dir))
        self.generator = GeminiAnswerGenerator()

    def _build_prompt(self, user_question: str) -> str:
        """
        Build a prompt that includes system instructions, retrieved context,
        optional market snapshot, and the original question.
        """
        context_pairs = self.retriever.retrieve(user_question, top_k=5)
        if context_pairs:
            context_blocks = [f"Q: {q}\nA: {a}" for (q, a) in context_pairs]
            context_text = "\n\n".join(context_blocks)
        else:
            context_text = "No directly relevant Soros Q&A could be retrieved for this question."

        ticker = extract_ticker(user_question)
        if ticker:
            market_context = get_market_snapshot(ticker)
            market_block = (
                f"Market snapshot for {ticker} (background only, do not just repeat):\n"
                f"{market_context}"
            )
        else:
            market_block = "No specific ticker detected. The question may be more general or macro-oriented."

        prompt = f"""{SYSTEM_INSTRUCTIONS}

[CONTEXT – SOROS Q&A]
{context_text}

[CONTEXT – MARKET SNAPSHOT]
{market_block}

[QUESTION]
{user_question}

[INSTRUCTIONS TO THE MODEL]
Using only the information above as your primary grounding, provide one coherent answer
that blends Soros-style framing, reasoning, and risk/uncertainty watchouts. Keep it concise,
educational, and readable for a classroom presentation—no numbered sections or headings.
"""
        return prompt

    def answer(self, user_question: str) -> str:
        user_question = (user_question or "").strip()
        if not user_question:
            return "Please ask a question about trading, investing, markets, or Soros's philosophy."

        prompt = self._build_prompt(user_question)
        reply = self.generator.generate(prompt)
        return reply


_chatbot = None
_chatbot_error = None

try:
    _chatbot = SorosRAGChatbot()
except Exception as e:
    _chatbot_error = str(e)
    print(f"CRITICAL WARNING: Failed to initialize SorosRAGChatbot: {e}")


def answer_question(query: str, k: int = 5) -> dict:
    """
    Adapter for the RAGView: returns a dict with an 'answer' key.
    """
    if _chatbot is None:
        return {"answer": f"Error: RAG components not available ({_chatbot_error})."}

    try:
        return {"answer": _chatbot.answer(query)}
    except Exception as e:
        print(f"Error generating RAG answer: {e}")
        return {"answer": "An error occurred generating the RAG answer."}
