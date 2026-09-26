import os
from functools import lru_cache
from langchain_ollama import OllamaEmbeddings, ChatOllama
from app.config import get_settings
from app.exceptions import EmbeddingServiceUnavailableError, GenerationServiceUnavailableError


@lru_cache
def get_embedding_client() -> OllamaEmbeddings:
    """
    Initializes and returns a cached LangChain OllamaEmbeddings client
    using environment variables to avoid validation errors.
    """
    settings = get_settings()
    os.environ["OLLAMA_BASE_URL"] = settings.OLLAMA_BASE_URL

    try:
        return OllamaEmbeddings(model=settings.EMBEDDING_MODEL)
    except Exception as e:
        raise EmbeddingServiceUnavailableError(
            f"Could not initialize Ollama embedding client: {e}"
        )


@lru_cache
def get_generation_client() -> ChatOllama:
    """
    Initializes and returns a cached LangChain ChatOllama client for
    the generation model, configured with a low temperature to keep
    RAG answers factual and deterministic rather than creative.
    """
    settings = get_settings()
    os.environ["OLLAMA_BASE_URL"] = settings.OLLAMA_BASE_URL

    try:
        return ChatOllama(
            model=settings.LLM_MODEL,
            temperature=0.1
        )
    except Exception as e:
        raise GenerationServiceUnavailableError(
            f"Could not initialize Ollama generation client: {e}"
        )