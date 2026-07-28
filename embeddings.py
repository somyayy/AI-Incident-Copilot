"""
Embedding generation for incident text using OpenAI's embedding models.
"""

from langchain_openai import OpenAIEmbeddings

from app.config import get_settings

settings = get_settings()

_embedding_model: OpenAIEmbeddings | None = None


def get_embedding_model() -> OpenAIEmbeddings:
    """Lazily instantiate a singleton embedding model client."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
    return _embedding_model


def embed_text(text: str) -> list[float]:
    """Return the embedding vector for a single piece of text."""
    model = get_embedding_model()
    return model.embed_query(text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors for a batch of documents."""
    model = get_embedding_model()
    return model.embed_documents(texts)
