from langchain_groq import ChatGroq
from BACKEND.Config.config import GROQ_API_KEY, GROQ_MODEL


_llm = None

def get_groq_llm() -> ChatGroq:
    """
    Load and return the Groq LLM.

    The LLM object is created only once and then reused
    throughout the application lifetime.
    """

    global _llm

    if _llm is None:

        if not GROQ_API_KEY:
            raise RuntimeError(
                "Missing GROQ_API_KEY. Set it in your .env file "
                "locally, or in Railway's Variables tab in "
                "production."
            )

        print(f"Loading Groq LLM: {GROQ_MODEL}")

        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
            temperature=0.0,
        )

        print("Groq LLM loaded successfully.")

    return _llm