import asyncio
from ollama import Client

from langchain_core.embeddings import Embeddings


class OllamaEmbeddings(Embeddings):
    def __init__(
        self,
        model: str = "embeddinggemma",
        host: str = "http://127.0.0.1:11434",
        batch_size: int = 100,
    ):
        self.client = Client(
            host=host,
        )
        self.model = model
        self.__batch_size = batch_size

    def embed_query(self, text: str) -> list[float] | list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embed(
            model=self.model,
            input=[text],
            dimensions=768,
        )
        return response.embeddings[0]

    async def aembed_query(self, text: str) -> list[float]:
        """Async version of embed_query."""
        return await asyncio.to_thread(self.embed_query, text)

    def embed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Async version of embed_documents."""
        all_embeddings: list[list[float]] = []
        batch_size = batch_size or self.__batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # Replace empty texts with placeholder
            batch = [text or "EMPTY" for text in batch]
            response = self.client.embed(
                model=self.model,
                input=batch,
                dimensions=768,
            )
            all_embeddings.extend(response.embeddings)
        return all_embeddings

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed_documents, texts)
