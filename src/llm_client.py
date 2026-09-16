"""Thin wrapper around the Groq-hosted LLM used everywhere else in the app.

Centralizing client construction here means the rest of the codebase never
touches API keys or model names directly.
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.config import GROQ_MODEL_NAME

load_dotenv()


def get_llm(model_name: str = GROQ_MODEL_NAME, temperature: float = 0.7) -> ChatGroq:
    """Build a configured ChatGroq client.

    Raises a clear error immediately if the API key is missing, instead of
    failing deep inside a LangChain call later.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to a .env file in the project "
            "root (see .env.example)."
        )
    return ChatGroq(groq_api_key=api_key, model_name=model_name, temperature=temperature)


# Module-level default instance so existing call sites can just `from
# src.llm_client import llm`.
llm = get_llm()


if __name__ == "__main__":
    response = llm.invoke("Name two essential ingredients in a samosa.")
    print(response.content)
