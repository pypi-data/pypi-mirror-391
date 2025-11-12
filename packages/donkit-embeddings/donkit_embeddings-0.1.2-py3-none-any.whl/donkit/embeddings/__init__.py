"""Custom embeddings implementations for Donkit RagOps."""

from typing import Literal

from langchain_core.embeddings import Embeddings

from .openai_embedder import OpenAIEmbeddings
from .vertex_embeddings import VertexEmbeddings
from .ollama_embeddings import OllamaEmbeddings


__all__ = [
    "OpenAIEmbeddings",
    "VertexEmbeddings",
    "OllamaEmbeddings",
    "get_custom_embeddings_openai_api",
    "get_vertexai_embeddings",
    "get_ollama_embeddings",
]


def get_custom_embeddings_openai_api(
    base_url: str, api_key: str, model: str
) -> Embeddings:
    """Factory function for CustomEmbeddings.

    Args:
        base_url: Base URL for the OpenAI-compatible API
        api_key: API key for authentication
        model: Model name to use for embeddings

    Returns:
        CustomEmbeddings instance
    """
    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )


def get_vertexai_embeddings(
    credentials_data: dict[str, str],
    *,
    model_name: Literal[
        "text-embedding-005",
        "text-multilingual-embedding-002",
    ] = "text-multilingual-embedding-002",
    vector_size: int = 768,
    batch_size: int = 100,
) -> Embeddings:
    """Factory function for VertexEmbeddings.

    Args:
        credentials_data: GCP service account credentials
        model_name: Vertex AI embedding model name
        vector_size: Output dimensionality for embeddings
        batch_size: Batch size for embedding documents

    Returns:
        VertexEmbeddings instance
    """
    return VertexEmbeddings(
        credentials_data=credentials_data,
        model_name=model_name,
        vector_size=vector_size,
        batch_size=batch_size,
    )


def get_ollama_embeddings(
    model: str = "embeddinggemma",
    host: str = "http://localhost:11434",
    batch_size: int = 50,
) -> Embeddings:
    """Factory function for OllamaEmbeddings.

    Args:
        model: Ollama model name
        host: Ollama host
        batch_size: Batch size for embedding documents

    Returns:
        OllamaEmbeddings instance
    """
    return OllamaEmbeddings(
        model=model,
        host=host,
        batch_size=batch_size,
    )
