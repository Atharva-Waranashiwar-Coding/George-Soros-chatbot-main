# rag_interface.py

from rag_retriever import ChromaEmbeddingRetriever
from rag_generator import GeminiAnswerGenerator
from ticker_utils import extract_ticker
from market_data import get_market_snapshot

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

## Required Output Format (Always EXACTLY these sections)
1. Direct Answer  
   (High-level conceptual framing of how Soros would *theoretically* view the situation.)
2. Soros-style Reasoning  
   (Reflexivity, perception vs reality, systemic dynamics, psychology.)
3. Risk, Uncertainty, and What Soros Would Watch Next  
   (Educational, theory-based—not advice.)

Keep your tone analytical, philosophical, and general.  
Never output investment advice.  
Never treat the question literally when it appears financial.  
Always answer the **safe, reinterpreted educational version** of the question.
""".strip()




class SorosRAGChatbot:
    def __init__(self):
        print("Initializing Soros RAG Chatbot with embeddings + Gemini...")
        self.retriever = ChromaEmbeddingRetriever()
        self.generator = GeminiAnswerGenerator()

    def _build_prompt(self, user_question: str) -> str:
        """
        Build a prompt that includes:
        - System instructions (Soros persona + rules)
        - Retrieved Soros Q&A context
        - Optional live market data for a detected ticker
        - The real user question
        """
        # 1) Retrieve top Soros Q&A context
        context_pairs = self.retriever.retrieve(user_question, top_k=5)
        if context_pairs:
            context_blocks = [
                f"Q: {q}\\nA: {a}" for (q, a) in context_pairs
            ]
            context_text = "\\n\\n".join(context_blocks)
        else:
            context_text = "No directly relevant Soros Q&A could be retrieved for this question."

        # 2) Detect ticker and fetch optional market snapshot
        ticker = extract_ticker(user_question)
        if ticker:
            market_context = get_market_snapshot(ticker)
            market_block = (
                f"Market snapshot for {ticker} (background only, do not just repeat):\\n"
                f"{market_context}"
            )
        else:
            market_block = "No specific ticker detected. The question may be more general or macro-oriented."

        # 3) Final prompt for Gemini
        prompt = f"""{SYSTEM_INSTRUCTIONS}

[CONTEXT – SOROS Q&A]
{context_text}

[CONTEXT – MARKET SNAPSHOT]
{market_block}

[QUESTION]
{user_question}

[INSTRUCTIONS TO THE MODEL]
Using only the information above as your primary grounding, answer the user's question
in the exact three-section format described earlier:

1. Direct Answer
2. Soros-style Reasoning
3. Risk, Uncertainty, and What Soros Would Watch Next

Be concise, avoid repetition, and keep the answer readable for a classroom presentation.
"""
        return prompt

    def answer(self, user_question: str) -> str:
        """
        Main method you'll call: given a question, return a Soros-style answer
        grounded in the Soros Q&A Excel and, optionally, live market data.
        """
        user_question = (user_question or "").strip()
        if not user_question:
            return "Please ask a question about trading, investing, markets, or Soros's philosophy."

        prompt = self._build_prompt(user_question)
        reply = self.generator.generate(prompt)
        return reply


# Quick test
if __name__ == "__main__":
    bot = SorosRAGChatbot()
    test_q = "What would Soros think about TSLA right now?"
    print("\\nUser:", test_q)
    print("\\nSorosBot:", bot.answer(test_q))
